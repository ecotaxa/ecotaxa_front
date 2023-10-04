import flask
from flask import request, render_template, Response, redirect, url_for, flash
from flask_login import current_user, login_required

import appli.constants
from appli import app, gvg
from appli.gui.jobs.Job import Job
from appli.gui.commontools import is_partial_request, py_get_messages

# noinspection PyUnresolvedReferences
from appli.gui.jobs.by_type import *
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException, MinUserModel
from to_back.ecotaxa_cli_py.api import JobsApi, UsersApi, ProjectsApi
from to_back.ecotaxa_cli_py.models import JobModel, ProjectModel


@app.route("/gui/job/create/<job_type>", methods=["GET", "POST"])
@login_required
def gui_job_create(job_type: str):

    """
    Used from menu (GET) and in self-submitted POST.
    """
    py_messages = py_get_messages("jobs")
    try:
        job_cls = Job.find_job_class_by_name(Job, job_type)
        assert job_cls is not None, "%s not known as a job UI type" % job_type
    except:
        raise ApiException(
            status=404,
            reason=py_messages["jobtypeunknown"],
        )
    if request.method == "GET":
        return job_cls.initial_dialog()
    else:
        # POST, so either an initial submit or a subsequent one in case of validation problem
        return job_cls.create_or_update()


@app.route("/gui/job/show/<int:job_id>", methods=["GET", "POST"])
@login_required
def gui_job_show(job_id: int):
    """
    Used from full job display (GET) and in self-submitted POST.
    """
    py_messages = py_get_messages("jobs")
    job = None
    with ApiClient(JobsApi, request) as api:
        try:
            job: JobModel = api.get_job(job_id=job_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["notfound"], "error")
            return redirect(url_for("gui_list_jobs"))

    with ApiClient(UsersApi, request) as uapi:
        owner: MinUserModel = uapi.get_user(user_id=job.owner_id)

    txt = ""
    if job and gvg("log") == "Y":
        with ApiClient(JobsApi, request) as japi:
            rsp = japi.get_job_log_file(job_id=job_id)
        return Response(rsp, mimetype="text/plain")

    target_prj = job.params.get("target_prj")
    target_prj = None
    if target_prj:
        target_prj = render_prj_summary(target_prj)
    steperrors = None
    customdetails = None
    if job.state != "E" and job.state != "F":
        codemessage = "jobmonitor"
    else:
        codemessage = None

    return render_template(
        "./v2/jobs/show.html",
        job=job,
        owner=owner,
        partial=is_partial_request(request),
        monitor=gvg("monitor"),
        steperrors=steperrors,
        target_proj=target_prj,
        customdetails=customdetails,
        codemessage=codemessage,
    )


@app.route("/gui/job/question/<int:job_id>", methods=["GET", "POST"])
@login_required
def gui_job_question(job_id: int):
    """
    Used for jobs needing user input during the processing.
    """
    py_messages = py_get_messages("jobs")
    with ApiClient(JobsApi, request) as japi:
        try:
            job: JobModel = japi.get_job(job_id=job_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                flash(py_messages["upload"]["nofile"], "error")
                return redirect(url_for("gui_list_jobs"))
    with ApiClient(UsersApi, request) as uapi:
        owner: MinUserModel = uapi.get_user(user_id=job.owner_id)

    if job.state != "A":
        return ""

    job_cls = Job.find_job_class_by_name(Job, job.type)
    assert job_cls is not None, "%s not known as a job UI type" % job.type
    if request.method == "GET":
        return job_cls.initial_question_dialog(job)
    else:
        return job_cls.treat_question_reply(job)


@app.route("/gui/job/status/<int:job_id>", methods=["GET"])
@login_required
def gui_job_status(job_id: int):
    """
    Ajax entry point for getting a job status. Called only from view jobs/show.html.
    """
    try:
        with ApiClient(JobsApi, request) as api:
            job: JobModel = api.get_job(job_id=job_id)
        job_cls = Job.find_job_class_by_name(Job, job.type)
        rep = job.to_dict()
        rep["finalaction"] = job_cls.final_action(job)
    except ValueError as e:  # Exception as e:
        rep = dict({"errors": [{"err": e.status, "message": str(e)}]})
    return rep


@app.route("/gui/job/forcerestart/<int:job_id>", methods=["GET"])
@login_required
def gui_job_force_restart(job_id: int):
    with ApiClient(JobsApi, request) as api:
        api.restart_job(job_id=job_id)
    return redirect(url_for("gui_job_show", job_id=job_id))


@app.route("/gui/job/clean/<int:jobid>", methods=["GET"])
@login_required
def gui_job_cleanup(jobid: int):
    py_messages = py_get_messages("jobs")
    with ApiClient(JobsApi, request) as api:
        try:
            job: JobModel = api.get_job(job_id=jobid)
            projid = job.params.get("prj_id")
            if projid is None and job.params.get("req") is not None:
                projid = job.params["req"].get("project_id")
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                flash(py_messages["notfound"], "error")
    with ApiClient(JobsApi, request) as api:
        api.erase_job(job_id=jobid)

    if gvg("thengotoproject") == "Y":
        return redirect("/prj/%d" % projid)
    else:
        return render_template(
            "v2/jobs/jobcleaned.html", partial=is_partial_request, jobid=jobid
        )


@app.route("/gui/jobs/listall")
@login_required
def gui_list_jobs():

    # TODO: Remove DB dependency
    seeall = ""
    is_admin = current_user.has_role(appli.constants.AdministratorLabel)
    wantsadmin = gvg("seeall") == "Y"
    if is_admin and wantsadmin:
        seeall = "&seeall=Y"
    cleanresult = []
    partial = is_partial_request(request)
    if gvg("cleandone") == "Y" or gvg("cleanerror") == "Y" or gvg("cleanall") == "Y":
        cleanall = gvg("cleanall") == "Y"
        cleandone = gvg("cleandone") == "Y"
        cleanerror = gvg("cleanerror") == "Y"
        with ApiClient(JobsApi, request) as api:
            apijobs: List[JobModel] = api.list_jobs(for_admin=wantsadmin)
            for ajob in apijobs:
                if (
                    cleanall
                    or (cleanerror and ajob.state == "E")
                    or (cleandone and ajob.state == "F")
                ):
                    api.erase_job(job_id=ajob.id)
                    cleanresult.append(ajob.id)

    if partial:
        return render_template(
            "/v2/jobs/_cleanresult.html",
            cleanresult=cleanresult,
        )
    tasks = []
    from appli.gui.jobs.job_interface import display_job

    with ApiClient(JobsApi, request) as api:
        apijobs: List[JobModel] = api.list_jobs(for_admin=wantsadmin)
        cache = {}
        tasks.extend([display_job(cache, ajob) for ajob in apijobs])
        tasks.sort(key=lambda t: t["id"], reverse=True)

    return render_template(
        "./v2/jobs/listall.html",
        jobs=tasks,
        seeall=seeall,
        cleanresult=cleanresult,
        partial=partial,
        IsAdmin=is_admin,
    )
