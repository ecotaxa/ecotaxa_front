from typing import List

from flask import g, flash, request
from flask_security import login_required

from appli import app, PrintInCharte, gvp, gvg, XSSEscape
from appli.project import sharedfilter
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ApiException, ObjectsApi, ObjectSetQueryRsp


@app.route('/prjPurge/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def prjPurge(PrjId):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot Purge this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    txt = obj_list_txt = ""
    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt += "<div style='margin-left: 5px;'><h3>ERASE OBJECTS TOOL </h3>"

    if gvp("objlist") == "":

        # Extract filter values
        filtres = {}
        for k in sharedfilter.FilterList:
            if gvg(k):
                filtres[k] = gvg(k, "")
        if len(filtres):
            # Query objects, using filters, in project
            with ApiClient(ObjectsApi, request) as api:
                object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres).object_ids
            obj_list_txt = "\n".join((str(r) for r in object_ids))

            txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
                   "USING Active Project Filters, {0} objects</span>".format(len(object_ids))
        else:
            txt += """Enter the list of internal object id you want to delete. 
            <br>Or type in <span style='cursor:pointer;color:#337ab7;' onclick="$('#objlist').val('DELETEALL')">
            "DELETEALL"</span> to remove all object from this project.
            <br>(<b>Around 10000 objects are deleted per second, so on a big project it can be long, 
            a NGinx Error may happen, but erase process is still working in background. 
            <br/>Statistics are not updated during erase project. </b>)
            <br>You can retrieve object id from a TSV export file using export data from project action menu<br>"""
        txt += """
        <form action=? method=post>
        <textarea name=objlist id=objlist cols=15 rows=20 autocomplete=off>{1}</textarea><br>
        <input type=checkbox name=destroyproject value=Y> DELETE project after DELETEALL action.<br>
        <input type="submit" class="btn btn-danger" value='ERASE THESE OBJECTS !!! IRREVERSIBLE !!!!!'>
        <a href ="/prj/{0}" class="btn btn-success">Cancel, Back to project home</a>
        </form></div>
        """.format(PrjId, obj_list_txt)
    else:
        if gvp("objlist") == "DELETEALL":
            # DELETE all objects
            with ApiClient(ProjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_project_projects_project_id_delete(project_id=PrjId,
                                                                                    only_objects=gvp(
                                                                                        "destroyproject") != "Y")
        else:
            # DELETE some objects in project
            objs = [int(x.strip()) for x in gvp("objlist").splitlines() if x.strip() != ""]
            err = None
            with ApiClient(ObjectsApi, request) as api:
                try:
                    res: ObjectSetQueryRsp = api.query_object_set_parents_object_set_parents_post(objs)
                except ApiException as ae:
                    if ae.status == 403:
                        err = 'At least one object does not belong to you'
                    else:
                        raise
            if err is None:
                nb_not_in_project = 0
                for a_prjid in res.project_ids:
                    if a_prjid != PrjId:
                        nb_not_in_project += 1
                if nb_not_in_project > 0:
                    err = '%d object(s) are not in current project.' % nb_not_in_project
            if err is not None:
                flash(err, 'error')
                return PrintInCharte(txt + "<br><br><a href ='/prj/{0}'>Back to project home</a>".format(PrjId))

            with ApiClient(ObjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_object_set_object_set_delete(objs)

        txt += "Deleted %d Objects, %d ObjectHisto, %d Images in Database and %d files" % (no, noh, ni, nbrfile)

        if gvp("objlist") == "DELETEALL" and gvp("destroyproject") == "Y":
            txt += "<br>Project and associated privileges, destroyed"
            return PrintInCharte(txt + "<br><br><a href ='/prj/'>Back to project list</a>")

    return PrintInCharte(txt + "<br><br><a href ='/prj/{0}'>Back to project home</a>".format(PrjId))
