#
# Some functions to interface with historical task management
#
import json
from types import SimpleNamespace
from typing import Dict, List

from flask import request

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import UsersApi, JobsApi
from to_back.ecotaxa_cli_py.models import UserModel, JobModel

JOB_STATE_TO_TASK_STATE = {'P': 'Pending',
                           'R': 'Running',
                           'A': 'Question',
                           'E': 'Error',
                           'F': 'Done'}


def _pseudo_task(user_cache: Dict, a_job: JobModel):
    """ Mimic a Task from a Job in order to get consistent display """
    from appli.tasks.taskmanager import Task
    ret = Task()
    ret.id = a_job.id
    ret.taskclass = "Task" + a_job.type
    ret.taskstate = JOB_STATE_TO_TASK_STATE.get(a_job.state, a_job.state)
    ret.taskstep = a_job.step if a_job.step else ""
    ret.progresspct = a_job.progress_pct
    ret.progressmsg = a_job.progress_msg
    if "prj_id" in a_job.params:
        # noinspection PyUnresolvedReferences
        a_job.params["ProjectId"] = str(a_job.params["prj_id"])
    if "req" in a_job.params and "project_id" in a_job.params["req"]:
        # noinspection PyUnresolvedReferences
        a_job.params["ProjectId"] = str(a_job.params["req"]["project_id"])
    ret.inputparam = json.dumps(a_job.params)
    ret.creationdate = a_job.creation_date
    ret.lastupdate = a_job.updated_on
    ret.owner_rel = SimpleNamespace()
    owner: UserModel = user_cache.get(a_job.owner_id)
    if owner is None:
        with ApiClient(UsersApi, request) as api:
            owner = api.get_user(user_id=a_job.owner_id)
        user_cache[a_job.owner_id] = owner
    ret.owner_rel = owner
    # ret.inputparam.update(a_job.result)
    ret.from_job = True
    return ret


def _add_jobs_to_task_list(tasks, wants_admin):
    # Add jobs from back-end
    with ApiClient(JobsApi, request) as api:
        api_jobs: List[JobModel] = api.list_jobs(for_admin=wants_admin)
        # Mimic tasks for display
        cache = {}
        tasks.extend([_pseudo_task(cache, a_job) for a_job in api_jobs])
        tasks.sort(key=lambda t: t.id, reverse=True)


def _clean_jobs(clean_all: bool, clean_done: bool, clean_error: bool, wants_admin: bool) -> str:
    # Clean some/all jobs depending on request
    ret = []
    with ApiClient(JobsApi, request) as api:
        api_jobs: List[JobModel] = api.list_jobs(for_admin=wants_admin)
        for a_job in api_jobs:
            if clean_all or (clean_error and a_job.state == 'E') or (clean_done and a_job.state == 'F'):
                api.erase_job(job_id=a_job.id)
                ret.append("Cleaned job %d" % a_job.id)
    return "<br>".join(ret)


def _add_jobs_to_tasks_summary(summary):
    from appli.utils import ApiClient
    with ApiClient(JobsApi, request) as api:
        try:
            api_jobs: List[JobModel] = api.list_jobs(for_admin=False)
            for a_job in api_jobs:
                state = JOB_STATE_TO_TASK_STATE.get(a_job.state, a_job.state)
                if state in summary:
                    summary[state] += 1
                else:
                    summary[state] = 1
        except ApiException as ae:
            pass
