from typing import List

from flask import g, flash, request
from flask_security import login_required

from appli import app, PrintInCharte, gvg, XSSEscape, FormatError
######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, MergeRsp, ApiException


@app.route('/prj/merge/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjMerge(PrjId):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exist"
            elif ae.status in (401, 403):
                flash('You cannot merge this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt = "<h3>Project Merge / Fusion </h3>"

    if not gvg('src'):
        # No submit -> preliminary page display
        txt += """<ul><li>You are allowed to merge projects that you are allowed to manage
<li>User privileges from both projects will be added
<li>This tool allows to merge two projects in a single projet (called Current project). The added project will then be automatically deleted. If object data are not consistent between both projects :
<ul><li>New data fields are added to the Current project.
    <li>The resulting project will thus contain partially documented datafields.
<li>Samples with same sample_id on both sides will <b>not</b> be updated from added project.
<li>Acquisitions with same acq_id on both sides will <b>not</b> be updated from added project.
</ul><li>Note : Next screen will indicate compatibility issues (if exists) and allow you to Confirm the merging operation.
</ul>
                """
        # Fetch the potential merge sources
        with ApiClient(ProjectsApi, request.cookies.get('session')) as api:
            rsp: List[ProjectModel] = api.search_projects_projects_search_get(for_managing=True)

        # TODO: XSSEscape??
        # Display them
        txt += """<table class='table table-bordered table-hover table-verycondensed'>
                <tr><th width=120>ID</td><th>Title</td><th width=100>Status</th><th width=100>Nbr Obj</th>
            <th width=100>% Validated</th><th width=100>% Classified</th></tr>"""
        for r in rsp:
            # Don't merge into self :)
            if r.projid == target_proj.projid:
                continue
            if r.objcount is None:
                r.objcount = 0
            if r.pctclassified is None:
                r.pctclassified = 0
            if r.pctvalidated is None:
                r.pctvalidated = 0
            txt += """<tr><td><a class="btn btn-primary" href='/prj/merge/{activeproject}?src={_projid}'>Select</a> {_projid}</td>
            <td>{_title}</td>
            <td>{_status}</td>
            <td>{_objcount:0.0f}</td>
            <td>{_pctvalidated:0.2f}</td>
            <td>{_pctclassified:0.2f}</td>
            </tr>""".format(activeproject=target_proj.projid, **r.__dict__)
        txt += "</table>"
        return PrintInCharte(txt)

    src_prj_id = int(gvg('src'))
    with ApiClient(ProjectsApi, request) as api:
        try:
            source_proj: ProjectModel = api.project_query_projects_project_id_get(src_prj_id, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Source project doesn't exist"
            elif ae.status in (401, 403):
                flash('You cannot merge from this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    txt += """<h4>Source Project : {0} - {1} (This project will be destroyed)</h4>
            """.format(source_proj.projid, XSSEscape(source_proj.title))

    if not gvg('merge'):  # Ici la src à été choisie et vérifiée
        # Validate the merge
        with ApiClient(ProjectsApi, request.cookies.get('session')) as api:
            rsp: MergeRsp = api.project_merge_projects_project_id_merge_post(project_id=target_proj.projid,
                                                                             source_project_id=source_proj.projid,
                                                                             dry_run=True)

        for an_error in rsp.errors:
            flash(an_error, "error")

        if len(rsp.errors) == 0:
            txt += FormatError(""" <span class='glyphicon glyphicon-warning-sign'></span>
            Warning project {1} - {2}<br>
            Will be destroyed, its content will be transfered in the target project.<br>
            This operation is irreversible</p>
            <br><a class='btn btn-lg btn-warning' href='/prj/merge/{0}?src={1}&merge=Y'>Start Project Fusion</a>        
            """, target_proj.projid, source_proj.projid, XSSEscape(source_proj.title), DoNotEscape=True)
            return PrintInCharte(txt)
        else:
            return PrintInCharte("Hit \"Back\" on the navigator to pick another source project.")

    if gvg('merge') == 'Y':
        # Do the real merge
        with ApiClient(ProjectsApi, request.cookies.get('session')) as api:
            rsp: MergeRsp = api.project_merge_projects_project_id_merge_post(project_id=target_proj.projid,
                                                                             source_project_id=source_proj.projid,
                                                                             dry_run=False)

        txt += "<div class='alert alert-success' role='alert'>Fusion Done successfully</div>"
        txt += "<br><a class='btn btn-lg btn-primary' href='/prj/%s'>Back to target project</a>" % target_proj.projid
        return PrintInCharte(txt)
