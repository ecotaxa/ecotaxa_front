import flask
from flask import request, render_template, Response, redirect, g
from flask_login import login_required, current_user

import appli.constants
from appli import app, PrintInCharte, gvg, XSSEscape, AddJobsSummaryForTemplate
from appli.jobs.Job import Job
# noinspection PyUnresolvedReferences
from appli.jobs.by_type import *  # Import all for job searching in class hierarchy
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException, MinUserModel
from to_back.ecotaxa_cli_py.api import JobsApi, UsersApi, ProjectsApi
from to_back.ecotaxa_cli_py.models import JobModel, ProjectModel


@app.route('/Job/Create/<job_type>', methods=['GET', 'POST'])
def jobCreate(job_type: str):
    """
        Used from menu (GET) and in self-submitted POST.
    """
    AddJobsSummaryForTemplate()
    job_cls = Job.find_job_class_by_name(Job, job_type)
    assert job_cls is not None, "%s not known as a job UI type" % job_type
    if request.method == 'GET':
        return job_cls.initial_dialog()
    else:
        # POST, so either an initial submit or a subsequent one in case of validation problem
        return job_cls.create_or_update()


@app.route('/Job/Show/<int:job_id>', methods=['GET', 'POST'])
def jobDisplay(job_id: int):
    """
        Used from full job display (GET) and in self-submitted POST.
    """
    AddJobsSummaryForTemplate()
    with ApiClient(JobsApi, request) as api:
        try:
            job: JobModel = api.get_job(job_id=job_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                return PrintInCharte("This job doesn't exist anymore, perhaps it was automatically purged")
    with ApiClient(UsersApi, request) as uapi:
        owner: MinUserModel = uapi.get_user(user_id=job.owner_id)

    txt = ""
    if gvg('log') == "Y":
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
        g.headcenter = "<h4>Project : <a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid,
                                                                              XSSEscape(target_prj.title))

    step_errors = ""
    custom_details = ""
    return render_template('jobs/show.html', job=job, owner=owner,
                           steperror=step_errors,
                           CustomDetailsAvail=custom_details,
                           extratext=txt)


@app.route('/Job/Question/<int:job_id>', methods=['GET', 'POST'])
def jobAsk(job_id: int):
    """
        Used for jobs needing user input during the processing.
    """
    AddJobsSummaryForTemplate()
    with ApiClient(JobsApi, request) as japi:
        try:
            job: JobModel = japi.get_job(job_id=job_id)
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                return PrintInCharte("This job doesn't exist anymore, perhaps it was automatically purged")
    with ApiClient(UsersApi, request) as uapi:
        _owner: MinUserModel = uapi.get_user(user_id=job.owner_id)

    if job.state != 'A':
        return ""

    job_cls = Job.find_job_class_by_name(Job, job.type)
    assert job_cls is not None, "%s not known as a job UI type" % job.type
    if request.method == 'GET':
        return job_cls.initial_question_dialog(job)
    else:
        return job_cls.treat_question_reply(job)


@app.route('/Job/Monitor/<int:job_id>', methods=['GET', 'POST'])
def jobMonitor(job_id: int):
    """
        Single-job monitoring.
    """
    AddJobsSummaryForTemplate()
    return render_template('jobs/monitor.html', job_id=job_id)


@app.route('/Job/GetStatus/<int:job_id>', methods=['GET'])
def jobGetStatus(job_id: int):
    """
        Ajax entry point for getting a job status. Called only from view jobs/monitor.html.
        TODO: Rewrite in JS.
    """
    try:
        with ApiClient(JobsApi, request) as api:
            job: JobModel = api.get_job(job_id=job_id)

        progress = job.progress_pct
        if progress is None:
            progress = 0

        if job.progress_msg is None:
            job.progress_msg = "In Progress"

        if job.state == "A":
            rep = {'q': {
                'Message': "Question waiting for your Answer",
                'Url': "/Job/Question/" + str(job.id)}}
        else:
            rep = {'d': {
                'PercentComplete': progress,
                'WorkDescription': job.progress_msg}
            }
            # if len(job.params.steperrors):
            #     rep['d']['WorkDescription'] += "".join("<br>\n-" + s for s in task.param.steperrors)

            if job.state == "F":
                rep['d']['IsComplete'] = "Y"
                rep['d']['ExtraAction'] = "<a href='/Job/Show/%d' class='btn btn-primary btn-sm ' " \
                                          "role='button'>Show Task</a>" % job_id
                job_cls = Job.find_job_class_by_name(Job, job.type)
                assert job_cls is not None, "%s type?" % job.type
                extra_action = job_cls.final_action(job)
                if extra_action:
                    rep['d']['ExtraAction'] = extra_action
            elif job.state == "E":
                rep['d']['IsError'] = "Y"
            elif job.state == "P":
                rep['d']['WorkDescription'] = "Pending"
    except ValueError as e:  # Exception as e:
        rep = {'d': {'IsError': 'Y',
                     'WorkDescription': str(e)}}
    # app.logger.info("Getstatus=%s",rep)
    return flask.jsonify(rep)


@app.route('/Job/ForceRestart/<int:job_id>', methods=['GET'])
def jobForceRestart(job_id: int):
    AddJobsSummaryForTemplate()
    with ApiClient(JobsApi, request) as api:
        api.restart_job(job_id=job_id)
    return redirect("/Job/Monitor/%d" % job_id)


@app.route('/Job/Clean/<int:job_id>', methods=['GET'])
def jobCleanup(job_id: int):
    AddJobsSummaryForTemplate()
    with ApiClient(JobsApi, request) as api:
        try:
            job: JobModel = api.get_job(job_id=job_id)
            proj_id = job.params.get("prj_id")
            if proj_id is None and job.params.get("req") is not None:
                proj_id = job.params["req"].get("project_id")
        except ApiException as ae:
            if ae.status in (401, 403):
                # Not logged in
                return ""
            elif ae.status == 404:
                return PrintInCharte("This job doesn't exist anymore, perhaps it was automatically purged")
    with ApiClient(JobsApi, request) as api:
        api.erase_job(job_id=job_id)

    msg = ""
    if proj_id:
        msg += "<a href='/prj/%s'>Back to project</a><br>" % proj_id

    msg += '<br><a href="/Jobs/listall"><span class="label label-info"> Back to Task List</span></a>'
    if gvg('thengotoproject') == 'Y':
        return redirect("/prj/%d" % proj_id)
    else:
        return PrintInCharte(msg)


@app.route('/Jobs/listall')
@login_required
def ListJobs():
    from appli.jobs.emul import _build_jobs_list, _clean_jobs
    g.headcenter = "<H3>Task Monitor</h3>"
    AddJobsSummaryForTemplate()

    # TODO: Remove DB dependency
    seeall = ""
    is_admin = current_user.has_role(appli.constants.AdministratorLabel)
    wants_admin = gvg("seeall") == 'Y'
    if is_admin and wants_admin:
        seeall = '&seeall=Y'

    txt = ""
    if gvg("cleandone") == 'Y' or gvg("cleanerror") == 'Y' or gvg("cleanall") == 'Y':
        txt = "Cleaning process result :<br>"
        clean_all = gvg("cleanall") == 'Y'
        clean_done = gvg("cleandone") == 'Y'
        clean_error = gvg("cleanerror") == 'Y'
        txt += _clean_jobs(clean_all, clean_done, clean_error, wants_admin)

    # txt += "<a class='btn btn-default'  href=?cleandone=Y>Clean All Done</a> <a class='btn btn-default'
    # href=?cleanerror=Y>Clean All Error</a>   <a class='btn btn-default' href=?cleanall=Y>Clean All
    # (warning !!!)</a>  Task count : "+str(len(tasks))
    tasks = _build_jobs_list(wants_admin)
    return render_template('jobs/listall.html', jobs=tasks, header=txt,
                           len_tasks=len(tasks), seeall=seeall,
                           IsAdmin=is_admin)
