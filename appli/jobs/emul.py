#
# Some functions to interface with historical task management
#
import json
from typing import Dict, List

from flask import request

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import UsersApi, JobsApi
from to_back.ecotaxa_cli_py.models import MinUserModel, JobModel

JOB_STATE_TO_USER_STATE = {'P': 'Pending',
                           'R': 'Running',
                           'A': 'Question',
                           'E': 'Error',
                           'F': 'Done'}


def _enrich_job(user_cache: Dict, a_job: JobModel):
    """ Enrich back-end job for display """
    a_job.state = JOB_STATE_TO_USER_STATE.get(a_job.state, a_job.state)
    if "prj_id" in a_job.params:
        # noinspection PyUnresolvedReferences
        a_job.params["ProjectId"] = str(a_job.params["prj_id"])
    if "req" in a_job.params and "project_id" in a_job.params["req"]:
        # noinspection PyUnresolvedReferences
        a_job.params["ProjectId"] = str(a_job.params["req"]["project_id"])
    owner: MinUserModel = user_cache.get(a_job.owner_id)
    if owner is None:
        with ApiClient(UsersApi, request) as api:
            owner: MinUserModel = api.get_user(user_id=a_job.owner_id)
        user_cache[a_job.owner_id] = owner
    a_job.owner_id = owner  # TODO: a bit dirty, replacing an ID with a model
    return a_job


def _build_jobs_list(wants_admin):
    # Add jobs from back-end
    ret = []
    with ApiClient(JobsApi, request) as api:
        api_jobs: List[JobModel] = api.list_jobs(for_admin=wants_admin)
        cache = {}
        ret.extend([_enrich_job(cache, a_job) for a_job in api_jobs])
        ret.sort(key=lambda t: t.id, reverse=True)
    return ret


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


def _build_jobs_summary():
    from appli.utils import ApiClient
    ret = {}
    with ApiClient(JobsApi, request) as api:
        try:
            api_jobs: List[JobModel] = api.list_jobs(for_admin=False)
            for a_job in api_jobs:
                state = JOB_STATE_TO_USER_STATE.get(a_job.state, a_job.state)
                if state in ret:
                    ret[state] += 1
                else:
                    ret[state] = 1
        except ApiException as ae:
            pass
    return ret
