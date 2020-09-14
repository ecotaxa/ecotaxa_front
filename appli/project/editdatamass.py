from typing import List, Dict

from flask import render_template, g, flash, request
from flask_login import current_user
from flask_security import login_required

import appli.project.sharedfilter as sharedfilter
from appli import app, PrintInCharte, gvg, gvp, XSSEscape
from appli.database import ExecSQL
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ObjectHeaderModel, ApiException, ObjectsApi


def GetFieldList(prj_model: ProjectModel):
    fieldlist = []

    excluded = set()
    for k in ObjectHeaderModel.openapi_types.keys():
        # TODO: Hardcoded, not rename-friendly
        if k not in ('objid', 'projid', 'img0id', 'imgcount'):
            fieldlist.append({'id': 'h' + k, 'text': 'object.' + k})
        else:
            excluded.add(k)
    assert excluded == {'objid', 'projid', 'img0id', 'imgcount'}, "Attempt to exclude a non-existing column"

    # TODO: Hardcoded, not completely rename-friendly
    # 2 fields in object_fields
    fieldlist.append({'id': 'f''orig_id', 'text': 'object.''orig_id'})
    fieldlist.append({'id': 'f''object_link', 'text': 'object.''object_link'})
    # 1 field in sample
    fieldlist.append({'id': 's''dataportal_descriptor', 'text': 'sample.''dataportal_descriptor'})
    # 1 field in acquisition
    fieldlist.append({'id': 'a''instrument', 'text': 'acquis.''instrument'' (fixed)'})

    MapList = (('f', prj_model.obj_free_cols), ('s', prj_model.sample_free_cols),
               ('a', prj_model.acquisition_free_cols), ('p', prj_model.process_free_cols))
    MapPrefix = {'f': 'object.', 's': 'sample.', 'a': 'acquis.', 'p': 'process.'}
    mapv: Dict[str, str]
    for mapk, mapv in MapList:
        for k in sorted(mapv.keys()):
            fieldlist.append({'id': mapk + mapv[k], 'text': MapPrefix[mapk] + k})
    return fieldlist


######################################################################################################################
@app.route('/prj/editdatamass/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditDataMass(PrjId):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot do mass data edition on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt = "<h3>Project Mass data edition </h3>"

    sqlparam = {}

    filtres = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filtres[k] = gvg(k, "")

    # Get the field name from user input
    field = gvp('field')
    if field and gvp('newvalue'):
        tables = {'f': 'obj_field', 'h': 'obj_head',
                  's': 'samples', 'a': 'acquisitions', 'p': 'process'}
        tablecode = field[0]
        table = tables[tablecode]  # on extrait la table à partir de la premiere lettre de field
        field = field[1:]  # on supprime la premiere lettre qui contenait le nom de la table
        sql = "update " + table + " set " + field + "=%(newvalue)s  "
        if field == 'classif_id':
            sql += " ,classif_when=current_timestamp,classif_who=" + str(current_user.id)
        sql += " where "
        if tablecode == "h":
            sql += " objid in ( select objid from objects o "
        elif tablecode == "f":
            sql += " objfid in ( select objid from objects o "
        elif tablecode == "s":
            sql += " sampleid in ( select distinct sampleid from objects o "
        elif tablecode == "a":
            sql += " acquisid in ( select distinct acquisid from objects o "
        elif tablecode == "p":
            sql += " processid in ( select distinct processid from objects o "
        sql += "  where projid=" + str(target_proj.projid)
        sqlparam['newvalue'] = gvp('newvalue')
        if len(filtres):
            sql += " " + sharedfilter.GetSQLFilter(filtres, sqlparam, str(current_user.id))
        sql += ")"
        if field == 'classif_id':
            sqlhisto = """insert into objectsclassifhisto(objid, classif_date, classif_type, classif_id, 
                                                          classif_qual, classif_who)
                          select objid, classif_when, 'M', classif_id,
                                 classif_qual,classif_who
                            from objects o
                           where projid=""" + str(target_proj.projid) + " and classif_when is not null "
            sqlhisto += sharedfilter.GetSQLFilter(filtres, sqlparam, str(current_user.id))
            ExecSQL(sqlhisto, sqlparam)
        ExecSQL(sql, sqlparam)
        flash('Data updated', 'success')

    if field == 'latitude' or field == 'longitude' or gvp('recompute') == 'Y':
        ExecSQL("""update samples s set latitude=sll.latitude,longitude=sll.longitude
              from (select o.sampleid,min(o.latitude) latitude,min(o.longitude) longitude
              from obj_head o
              where projid=%(projid)s and o.latitude is not null and o.longitude is not null
              group by o.sampleid) sll where s.sampleid=sll.sampleid and projid=%(projid)s """,
                {'projid': target_proj.projid})
        flash('sample latitude and longitude updated', 'success')

    if len(filtres):
        # Query the filtered list in project
        with ApiClient(ObjectsApi, request) as api:
            object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres)
        # Warn the user
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "USING Active Project Filters, {0} objects</span>". \
            format(len(object_ids))
    else:
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "Apply to ALL OBJECTS OF THE PROJECT (NO Active Filters)</span>"

    Lst = GetFieldList(target_proj)

    return PrintInCharte(render_template("project/prjeditdatamass.html",
                                         Lst=Lst, header=txt))


######################################################################################################################
@app.route('/prj/resettopredicted/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjResetToPredicted(PrjId):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot do reset to predicted on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt = "<h3>Reset status to predicted</h3>"

    filtres = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filtres[k] = gvg(k, "")

    proceed = gvp('process')
    if proceed == 'Y':
        # Do the job on back-end
        with ApiClient(ObjectsApi, request) as api:
            api.reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post(PrjId, filtres)

        # flash('Data updated', 'success')
        txt += "<a href='/prj/%s' class='btn btn-primary'>Back to project</a> " % target_proj.projid

        return PrintInCharte(txt)

    if len(filtres):
        # Query the filtered list in project
        with ApiClient(ObjectsApi, request) as api:
            object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres)
        # Warn the user
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "USING Active Project Filters, {0} objects</span>" \
            .format(len(object_ids))
    else:
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "Apply to ALL OBJECTS OF THE PROJECT (NO Active Filters)</span>"

    # The eventual filter is in the URL (GET), so when POST-ed again after validation, the filter is preserved
    return PrintInCharte(render_template("project/prjresettopredicted.html",
                                         header=txt))
