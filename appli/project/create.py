from flask import request
from flask_login import login_required, current_user

from appli import app, gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py.models import CreateProjectReq


@app.route("/prj/simplecreate/", methods=["GET", "POST"])
@login_required
def SimpleCreate():
    if not current_user.is_authenticated or not current_user.is_active:
        raise HTTPException(403)
    with ApiClient(ProjectsApi, request) as api:

        req = CreateProjectReq(
            title=gvp("projtitle"), instrument=gvp("proj_instrument")
        )
        rsp: int = api.create_project(req)

    # return "<a href='/prj/{0}' class='btn btn-primary'>Project Created ! Open IT</a>".format(Prj.projid)
    return "<script>window.location='/prj/{0}';</script>".format(rsp)
