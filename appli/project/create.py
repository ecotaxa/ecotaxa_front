from flask import request
from flask_security import login_required

from appli import app, gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, CreateProjectReq


@app.route('/prj/simplecreate/', methods=['GET', 'POST'])
@login_required
def SimpleCreate():
    with ApiClient(ProjectsApi, request) as api:
        req = CreateProjectReq(title=gvp("projtitle"))
        rsp: int = api.create_project_projects_create_post(req)

    # return "<a href='/prj/{0}' class='btn btn-primary'>Project Created ! Open IT</a>".format(Prj.projid)
    return "<script>window.location='/prj/{0}';</script>".format(rsp)
