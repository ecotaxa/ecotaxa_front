from flask_babel import _
from typing import Dict
from flask import request
from appli.utils import ApiClient
from appli.gui.jobs.staticlistes import py_messages, JOB_STATE_TO_USER_STATE
from to_back.ecotaxa_cli_py import ApiException, MinUserModel
from to_back.ecotaxa_cli_py.api import JobsApi, UsersApi
from to_back.ecotaxa_cli_py.models import JobModel


def export_format_options(type=None):
    options = dict(
        {
            "options": [
                {
                    "name": "objectdata",
                    "label": _("Object Data (median,mean, x, y, ...)"),
                },
                {
                    "name": "processdata",
                    "label": _("Process Data (software,version, ...)"),
                },
                {
                    "name": "acqdata",
                    "label": _("Acquisition Data (Resolution, ...)"),
                },
                {
                    "name": "sampledata",
                    "label": _("Sample Data (lat,long, date, ...)"),
                },
                {
                    "name": "histodata",
                    "label": _("Historical Data"),
                },
                {
                    "name": "commentsdata",
                    "label": _("Comments"),
                },
            ],
            "otheroptions": [
                {
                    "name": "usecomasepa",
                    "label": _("Use coma as decimal separator"),
                },
                {
                    "name": "formatdates",
                    "label": _("Format dates and times using - and :"),
                },
                {
                    "name": "internalids",
                    "label": _("Internal Ids (including taxonomic source Id)"),
                },
            ],
            "images": {
                "name": "exportimages",
                "label": _("Export image files"),
            },
        }
    )
    if type == "SUM":
        return {
            **dict(
                {
                    "data": {
                        "SUM": {},
                    }
                }
            ),
            **options,
        }
    else:
        return {
            **dict(
                {
                    "fields": {
                        "TSV": {
                            "exportimages": {
                                "select": [
                                    {"label": _("NO Images"), "value": ""},
                                    # {"label": _("Only Rank 0 Image"), "value": "1"},
                                    # {
                                    #    "label": _("All images of each object"),
                                    #    "value": "A",
                                    # },
                                ]
                            },
                        },
                        "BAK": {
                            "exportimages": {
                                "select": [
                                    # {"label": _("NO Images"), "value": ""},
                                    {
                                        "label": _("All images files"),
                                        "value": "A",
                                    },
                                ]
                            }
                        },
                    },
                    "data": {
                        "TSV": {
                            "objectdata": ("1", False),
                            "processdata": ("1", False),
                            "acqdata": ("1", False),
                            "sampledata": ("1", False),
                            "histodata": ("", False),
                            "commentsdata": ("", False),
                            "usecomasepa": ("", False),
                            "formatdates": ("1", False),
                            "internalids": ("1", False),
                            "splitcsvby": "",
                            "exportimages": ("", False),
                        },
                        "BAK": {
                            "objectdata": ("1", True),
                            "processdata": ("1", True),
                            "acqdata": ("1", True),
                            "sampledata": ("1", True),
                            "histodata": ("", True),
                            "commentsdata": ("", True),
                            "usecomasepa": ("", True),
                            "formatdates": ("1", True),
                            "internalids": ("1", True),
                            "splitcsvby": "",
                            "exportimages": ("", False),
                        },
                    },
                }
            ),
            **options,
        }


def display_job(usercache: Dict[int, MinUserModel], ajob: JobModel):
    """Enrich back-end job for display"""
    job = ajob.to_dict()
    job["state"] = JOB_STATE_TO_USER_STATE.get(ajob.state, ajob.state)

    if "prj_id" in job["params"]:
        job["projid"] = str(ajob.params["prj_id"])
    if (
        ("projid" not in job or job["projid"] is None)
        and "req" in ajob.params
        and "project_id" in ajob.params["req"]
    ):
        # noinspection PyUnresolvedReferences
        projid = str(ajob.params["req"]["project_id"])

    owner: Optional[MinUserModel] = usercache.get(ajob.owner_id)
    if owner is None:
        with ApiClient(UsersApi, request) as api:
            owner = api.get_user(user_id=ajob.owner_id)
        usercache[ajob.owner_id] = owner
    job["owner"] = owner
    return job
