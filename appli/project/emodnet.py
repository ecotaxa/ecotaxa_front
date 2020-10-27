from flask import request, flash, render_template

from appli import app, PrintInCharte
from flask_login import login_required

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ApiException, ExportsApi, EMODnetExportReq, \
    EMODnetExportRsp


@app.route('/prj/emodnet/<int:prj_id>', methods=['GET', 'POST'])
@login_required
def EMODnet_export(prj_id):
    """
        Export the given project for EMODnet-bio.
    """
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            source_proj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exist", 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")
            elif ae.status == 403:
                flash('You cannot export this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    if request.method == 'GET':
        # Initial loading
        with ApiClient(ExportsApi, request) as api:
            req: EMODnetExportReq = EMODnetExportReq(project_ids=[prj_id])
            export_rsp: EMODnetExportRsp = api.emodnet_format_export_export_emodnet_post(emo_dnet_export_req=req,
                                                                                         dry_run=True)

    else:
        # Self-post
        pass
    page = render_template("project/emodnet.html", data=export_rsp, prj=source_proj)
    return PrintInCharte(page)
