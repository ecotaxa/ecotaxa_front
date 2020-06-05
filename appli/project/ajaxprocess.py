from collections import OrderedDict
from typing import Optional, Dict

from flask import request
from flask_login import current_user
from flask_security import login_required

from appli import app, database, gvp
from appli.database import db
from appli.db_raw_connection import RawConnection


@app.route('/prj/ManualClassif/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjManualClassif(PrjId):
    # noinspection PyStatementEffect
    # request.form  # Force la lecture des données POST sinon il y a une erreur 504
    Prj = database.Projects.query.filter_by(projid=PrjId).first()
    if not Prj.CheckRight(1):  # Level 0 = Read, 1 = Annotate, 2 = Admin
        return '<span class="label label-danger">You cannot Annotate this project</span>'

    logger = app.logger

    # e.g. changes[160030063]: -1
    ui_changes = {}
    # Sanitize & convert input
    for k, v in request.form.items():
        if k[0:7] != "changes":
            continue
        try:
            obj_id = int(k[8:-1])
            if v not in ("-1", ""):
                _tst = int(v)
        except ValueError:
            logger.info("ManualClassif: Bad form variable %s %s", k, v)
            continue
        ui_changes[obj_id] = v
    if len(ui_changes) == 0:
        return '<span class="label label-warning">No pending change to update</span>'

    # Get a fresh low_level DB connection
    db_cnx = RawConnection(db.engine.raw_connection())

    try:
        ret = write_changes_to_db(PrjId, ui_changes, db_cnx, logger)
    except Exception as e:  # noqa
        logger.exception(e)
        ret = '<span class="label label-danger">Changes NOT saved (see logs)</span>'
    if "Successful" in ret:
        db_cnx.commit()
    else:
        db_cnx.rollback()
    return ret


def write_changes_to_db(prj_id, ui_changes: Dict[int, str], db_cnx: RawConnection, logger):
    """
        Do the DB work in a single transaction.
    """
    # Gather state of classification, for impacted objects, before the change. Keep a lock on rows.
    present_vals_sql = """select o.objid,
                                 o.classif_auto_id, o.classif_auto_when, o.classif_auto_score, 
                                 o.classif_id, o.classif_qual, o.classif_who, o.classif_when 
                            from obj_head o
                           where o.objid = any(%s)
                          for no key update"""
    prev = db_cnx.get_as_dict(present_vals_sql, [list(ui_changes.keys())], 'objid')

    # Cook a diff b/w present and wanted values, both for the update of obj_head and preparing the ones on _stat
    upd_params = []
    upd_objids = []
    all_changes = {}
    collated_changes: Dict[int, Dict] = {}
    mru_changes = OrderedDict()  # We'd need an OrderedSet, not sure that keeping the order is important however
    wanted_qualif = gvp('qual')
    current_user_id = current_user.id
    for obj_id, v in ui_changes.items():
        prev_obj = prev[obj_id]
        prev_classif_id: Optional[int] = prev_obj['classif_id']
        if v == "-1" or v == "":  # special value from validate all
            # Arrange that no change can happen for this field
            # Note: prev_classif_id can be None
            new_classif_id: Optional[int] = prev_classif_id
        else:
            new_classif_id: Optional[int] = int(v)
        prev_classif_qual = prev_obj['classif_qual']
        if (prev_classif_id == new_classif_id
                and prev_classif_qual == wanted_qualif
                and prev_obj['classif_who'] == current_user_id):
            continue
        # There was at least 1 field change for this object
        params = {'objid': obj_id, 'classif_id': new_classif_id, 'classif_qual': wanted_qualif,
                  'classif_who': current_user_id}
        upd_params.append(params)
        upd_objids.append(obj_id)
        # Decrement for what was before
        count_in_and_out(collated_changes, prev_classif_id, prev_classif_qual, -1)
        # Increment for what arrives
        count_in_and_out(collated_changes, new_classif_id, wanted_qualif, 1)
        # MRU needs update if there are changes in _usage_ of taxa
        if prev_classif_id != new_classif_id:
            mru_changes.setdefault(new_classif_id)
        # Compact logging lines, grouped by operation
        change_key = (prev_classif_id, prev_classif_qual, new_classif_id, wanted_qualif)
        for_this_change = all_changes.setdefault(change_key, [])
        for_this_change.append(obj_id)

    # Apply MRU changes if any
    for new_classif_id in mru_changes.keys():
        update_MRU(db_cnx, current_user_id, new_classif_id)

    if len(upd_params) == 0:
        return '<span class="label label-success">Nothing found to update</span>'

    # Log a bit
    for a_chg, impacted in all_changes.items():
        logger.info("change %s for %s", a_chg, impacted)

    # Historize the updated rows (can be a lot!)
    ins_sql = """insert into objectsclassifhisto(objid, classif_date, classif_type, classif_id, 
                                                        classif_qual, classif_who, classif_score)
                 select objid, classif_when, 'M' classif_type, classif_id, 
                        classif_qual, classif_who, null as classif_score
                   from obj_head oh
                  where objid = any(%s)
                    and classif_when is not null
                 on conflict on constraint objectsclassifhisto_pkey do nothing """
    db_cnx.execute(ins_sql, [upd_objids])

    # Prepare a bulk update of obj_head
    upd_sql = """update obj_head 
                    set classif_id = %(classif_id)s, classif_qual = %(classif_qual)s, 
                        classif_who = %(classif_who)s, classif_when=now()
                  where objid=%(objid)s """
    nb_updated = db_cnx.executemany(upd_sql, upd_params)
    if nb_updated != len(upd_params):
        # Not all was done, rollback and tell the user
        return '<span class="label label-danger">Unable to save _all_ changes</span>'

    # Propagate changes to projects_taxo_stat
    needed_ids = list(collated_changes.keys())
    # Lock taxo lines to prevent re-entering, during validation it's often a handful of them.
    pts_sql = """select id
                   from taxonomy
                  where id=any(%s)
                 for no key update
    """
    db_cnx.execute(pts_sql, [needed_ids])

    # Lock the rows we are going to update
    pts_sql = """select id
                   from projects_taxo_stat 
                  where projid=%s
                    and id=any(%s) 
                 for no key update"""
    ids_in_db = set([row[0] for row in db_cnx.get(pts_sql, [prj_id, needed_ids])])
    ids_not_in_db = set(needed_ids).difference(ids_in_db)
    if len(ids_not_in_db) > 0:
        pts_ins = """insert into projects_taxo_stat(projid, id, nbr, nbr_v, nbr_d, nbr_p) 
                     select %(projid)s, classif_id, count(*) nbr, 
                            count(case when classif_qual='V' then 1 end) nbr_v,
                            count(case when classif_qual='D' then 1 end) nbr_d,
                            count(case when classif_qual='P' then 1 end) nbr_p
                       from obj_head
                      where projid=%(projid)s and classif_id=any(%(ids)s)
                   group by classif_id"""
        db_cnx.execute(pts_ins, {'projid': prj_id, 'ids': list(ids_not_in_db)})
        if -1 in ids_not_in_db:
            # I guess, special case for unclassified
            pts_ins = """insert into projects_taxo_stat(projid, id, nbr, nbr_v, nbr_d, nbr_p) 
                         select %(projid)s, -1, count(*) nbr, 
                                count(case when classif_qual='V' then 1 end) nbr_v,
                                count(case when classif_qual='D' then 1 end) nbr_d,
                                count(case when classif_qual='P' then 1 end) nbr_p
                           from obj_head
                          where projid=%(projid)s and classif_id is null"""
            db_cnx.execute(pts_ins, {'projid': prj_id})

    # Apply delta
    for classif_id, chg in collated_changes.items():
        if classif_id in ids_not_in_db:
            # The line was created with OK values
            continue
        sqlparam = {'projid': prj_id, 'id': classif_id, 'n': chg['n'], 'v': chg['V'], 'd': chg['D'], 'p': chg['P']}
        ts_sql = """update projects_taxo_stat 
                       set nbr=nbr+%(n)s, nbr_v=nbr_v+%(v)s, nbr_d=nbr_d+%(d)s, nbr_p=nbr_p+%(p)s 
                     where projid=%(projid)s and id=%(id)s"""
        db_cnx.execute(ts_sql, sqlparam)
    return '<span class="label label-success">Database update Successful</span>'


def count_in_and_out(cumulated_changes, classif_id, qualif, inc_or_dec):
    """ Cumulate change +/- for a given taxon """
    if classif_id is None:
        classif_id = -1  # Unclassified
    changes_for_id = cumulated_changes.setdefault(classif_id, {'n': 0, 'V': 0, 'P': 0, 'D': 0})
    changes_for_id['n'] += inc_or_dec
    if qualif in ('V', 'P', 'D'):
        changes_for_id[qualif] += inc_or_dec


def update_MRU(db_cnx: RawConnection, current_user_id: int, classif_id):
    with app.MRUClassif_lock:
        tbl = app.MRUClassif.get(current_user_id, [])
        for i, t in enumerate(tbl):
            if t["id"] == classif_id:
                if i > 0:
                    # The classif_id is already in MRU, but not in first. Move it.
                    tbl = [t] + tbl[0:i] + tbl[i + 1:]
                # We're done as the classif_id is in MRU, and first.
                break
        else:
            # Validate the id, it must be in the DB table, with a valid parent.
            taxo_sql = """select tf.display_name as name
                            from taxonomy tf
                       left join taxonomy p1 on tf.parent_id = p1.id
                           where tf.id = %(id)s """
            taxon = db_cnx.get(taxo_sql, {"id": classif_id})
            if len(taxon) == 1:
                taxon = taxon[0][0]
                tbl.insert(0, {"id": classif_id, "pr": 0, "text": taxon})
                if len(tbl) > 10:
                    tbl = tbl[0:10]
        app.MRUClassif[current_user_id] = tbl


@app.route('/prj/UpdateComment/<int:ObjId>', methods=['GET', 'POST'])
@login_required
def PrjUpdateComment(ObjId):
    Obj = database.Objects.query.filter_by(objid=ObjId).first()
    if Obj is None:
        return "Object doesnt exists"
    Prj = database.Projects.query.filter_by(projid=Obj.projid).first()
    if not Prj.CheckRight(1):  # Level 0 = Read, 1 = Annotate, 2 = Admin
        return "You cannot Annotate this project"

    Obj.complement_info = gvp('comment')
    db.session.commit()

    return '<span class="label label-success">Database update Successful</span>'
