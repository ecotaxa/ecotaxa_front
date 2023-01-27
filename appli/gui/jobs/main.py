import flask
from flask import request, render_template, Response, redirect
from flask_login import login_required, current_user

import appli.constants
from appli import app, PrintInCharte, gvg, XSSEscape
from appli.gui.jobs.Job import Job

# noinspection PyUnresolvedReferences

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException, MinUserModel
from to_back.ecotaxa_cli_py.api import JobsApi, UsersApi, ProjectsApi
from to_back.ecotaxa_cli_py.models import JobModel, ProjectModel


@app.route("/gui/job/show/<int:job_id>", methods=["GET", "POST"])
def job_display(job_id: int):
    """
    Used from full job display (GET) and in self-submitted POST.
    """
    with ApiClient(JobsApi, request) as api:
        try:
            job: JobModel = api.get_job(job_id=job_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                return PrintInCharte(
                    "This job doesn't exist anymore, perhaps it was automatically purged"
                )
    with ApiClient(UsersApi, request) as uapi:
        owner: MinUserModel = uapi.get_user(user_id=job.owner_id)

    txt = ""
    if gvg("log") == "Y":
        with ApiClient(JobsApi, request) as japi:
            rsp = japi.get_job_log_file(job_id=job_id)
        return Response(rsp, mimetype="text/plain")

    # if gvg('CustomDetails') == "Y":
    #     return task.ShowCustomDetails()
    # if "GetResultFile" in dir(task):
    #     f = task.GetResultFile()
    #     if f is None:
    #         txt += "Error, final file not available"
    #     else:
    #         txt += "<a href='/Task/GetFile/%d/%s' class='btn btn-primary btn-sm ' role='button'>Get file %s</a>" % (
    #             TaskID, f, f)
    #
    # CustomDetailsAvail = "ShowCustomDetails" in dir(task)

    proj_id = job.params.get("prj_id")
    if proj_id:
        # Inject project title in headers
        with ApiClient(ProjectsApi, request) as papi:
            target_prj: ProjectModel = papi.project_query(proj_id, for_managing=False)

    step_errors = ""
    custom_details = ""
    print(job.to_dict())
    return render_template(
        "./v2/jobs/show.html",
        job=job,
        owner=owner,
        steperror=step_errors,
        job_proj=dict({"projid": target_prj.projid, "title": target_prj.title}),
        customdetails=custom_details,
    )


@app.route("/gui/jobs/listall")
@login_required
def list_jobs():
    from appli.jobs.emul import _build_jobs_list, _clean_jobs

    headcenter = "<H3>Task Monitor</h3>"

    # TODO: Remove DB dependency
    seeall = ""
    is_admin = current_user.has_role(appli.constants.AdministratorLabel)
    wants_admin = gvg("seeall") == "Y"
    if is_admin and wants_admin:
        seeall = "&seeall=Y"

    txt = ""
    if gvg("cleandone") == "Y" or gvg("cleanerror") == "Y" or gvg("cleanall") == "Y":
        txt = "Cleaning process result :<br>"
        clean_all = gvg("cleanall") == "Y"
        clean_done = gvg("cleandone") == "Y"
        clean_error = gvg("cleanerror") == "Y"
        txt += _clean_jobs(clean_all, clean_done, clean_error, wants_admin)

    # txt += "<a class='btn btn-default'  href=?cleandone=Y>Clean All Done</a> <a class='btn btn-default'
    # href=?cleanerror=Y>Clean All Error</a>   <a class='btn btn-default' href=?cleanall=Y>Clean All
    # (warning !!!)</a>  Task count : "+str(len(tasks))
    tasks = _build_jobs_list(wants_admin)
    return render_template(
        "./v2/jobs/listall.html",
        jobs=tasks,
        header=txt,
        len_tasks=len(tasks),
        seeall=seeall,
        IsAdmin=is_admin,
    )
