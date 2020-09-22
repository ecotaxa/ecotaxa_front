from collections import OrderedDict
from typing import List

from flask import g, flash, request, render_template
from flask_security import login_required

from appli import app, PrintInCharte, database, gvg
from appli.database import GetAll, ExecSQL
from appli.project.main import RecalcProjectTaxoStat

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ApiException, UsersApi, UserModel


######################################################################################################################
# noinspection PyPep8Naming,SpellCheckingInspection
@app.route('/prj/EditAnnot/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditAnnot(PrjId):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot do mass annotation edition on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, target_proj.title)

    header = "<h3>Project Edit / Erase annotation massively </h3>"

    # Store posted variables
    old_author = gvg('OldAuthor')  # Note: is an id or one of the special choices below
    new_author = gvg('NewAuthor')
    date_filter = gvg('filt_date')
    time_filter_hour = gvg('filt_hour')
    time_filter_minutes = gvg('filt_min')
    # ############### 1er Ecran
    if not new_author or not old_author:
        # Selection lists, special choices, in first
        LstUserOld = OrderedDict({'anyuser': "Any User"})
        LstUserNew = OrderedDict({'lastannot': "Previous Annotation available, or prediction, or Nothing"})
        # TODO: It would be nice to offer only relevant users as a choice
        with ApiClient(UsersApi, request) as api:
            all_users: List[UserModel] = api.get_users_users_get()
        # No guaranteed order from API, so sort now, see #475 for the strip()
        all_users.sort(key=lambda user: user.name.strip())
        # Complete selection lists
        for usr in all_users:
            LstUserOld[usr.id] = usr.name
            LstUserNew[usr.id] = usr.name
        return PrintInCharte(render_template("project/MassAnnotationEdition.html",
                                             old_authors=LstUserOld, new_authors=LstUserNew,
                                             header=header))

    # Prepare data for the 2 other possibilities:
    #   - Estimate of the impacted data
    #   - Real execution of the update
    sqlclause = {"projid": target_proj.projid, 'retrictsq': "", 'retrictq': "", 'jointype': ""}
    if old_author == "anyuser":
        from_txt = "Replace all classification"
    else:
        OldAuthor = database.users.query.filter_by(id=int(old_author)).first()
        if OldAuthor is None:
            flash("Invalid new author", 'error')
            return PrintInCharte("URL Hacking ?")
        sqlclause['retrictsq'] += " and och.classif_who!=%s " % old_author
        sqlclause['retrictq'] += " and o.classif_who=%s " % old_author
        from_txt = "Replace classification done by <b>%s</b>" % OldAuthor.name

    if new_author == "lastannot":
        to_txt = "By the last classification of any other author"
        sqlclause['jointype'] = 'left'
    else:
        NewAuthor = database.users.query.filter_by(id=int(new_author)).first()
        if NewAuthor is None:
            flash("Invalid new author", 'error')
            return PrintInCharte("URL Hacking ?")
        sqlclause['retrictsq'] += " and och.classif_who=%s " % new_author
        sqlclause['retrictq'] += " and o.classif_who!=%s " % new_author
        to_txt = "By classification done by <b>%s</b>" % NewAuthor.name

    if date_filter:
        sqlclause['retrictq'] += " and o.classif_when>=to_date('" + date_filter
        if time_filter_hour:
            sqlclause['retrictq'] += " " + time_filter_hour
        if time_filter_minutes:
            sqlclause['retrictq'] += ":" + time_filter_minutes
        sqlclause['retrictq'] += " ','YYYY-MM-DD HH24:MI')"

    # ############### 2nd Ecran, affichage liste des categories & estimations
    if not gvg('Process'):
        sql = """
        select t.id,concat(t.name,' (',t2.name,')') as name, count(*) nbr
        from obj_head o
        {jointype} join (select rank() over(PARTITION BY och.objid order by och.classif_date desc) ochrank,och.*
              from objectsclassifhisto och
              join obj_head ooch on ooch.objid=och.objid and ooch.projid={projid}
        where och.classif_type='M' {retrictsq}) newclassif on newclassif.objid=o.objid and newclassif.ochrank=1
        join taxonomy t on o.classif_id=t.id
        left join taxonomy t2 on t.parent_id=t2.id
        where o.projid={projid} {retrictq}
        GROUP BY t.id,concat(t.name,' (',t2.name,')')
        order BY t.name
        """.format(**sqlclause)
        data = GetAll(sql, debug=False)
        return PrintInCharte(render_template("project/MassAnnotationEdition.html",
                                             header=header, from_txt=from_txt, to_txt=to_txt,
                                             old_author=old_author, new_author=new_author,
                                             date_filter=date_filter, time_filter_hour=time_filter_hour,
                                             time_filter_minutes=time_filter_minutes,
                                             taxo_impact=data
                                             ))

    # ############### 3eme Ecran Execution Requetes
    if gvg('Process') == 'Y':
        sqlclause['taxoin'] = ",".join((x[4:] for x in request.form if x[0:4] == "taxo"))
        if sqlclause['taxoin'] == "":
            flash("You must select at least one categorie to do the replacement", 'error')
            return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
        sql = """
        update obj_head as ou
            set classif_who=newclassif.classif_who,
            classif_when=coalesce(newclassif.classif_date,ou.classif_auto_when),
            classif_id=coalesce(newclassif.classif_id,ou.classif_auto_id),
            classif_qual=case when newclassif.classif_qual is not null then newclassif.classif_qual
                                 when ou.classif_auto_id is not null then 'P'
                                 else null end
        from obj_head o {jointype} join
        (select rank() over(PARTITION BY och.objid order by och.classif_date desc) ochrank,och.*
              from objectsclassifhisto och
              join obj_head ooch on ooch.objid=och.objid and ooch.projid={projid}
        where och.classif_type='M' {retrictsq}) newclassif on newclassif.objid=o.objid and newclassif.ochrank=1
        join taxonomy t on o.classif_id=t.id
        where  o.projid={projid} {retrictq} and o.classif_id in ({taxoin})
        and o.objid=ou.objid

        """.format(**sqlclause)
        RowCount = ExecSQL(sql, debug=True)
        RecalcProjectTaxoStat(target_proj.projid)
        return PrintInCharte(render_template("project/MassAnnotationEdition.html",
                                             header=header,
                                             nb_rows=RowCount, projid=target_proj.projid))
