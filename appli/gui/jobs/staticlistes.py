from flask_babel import _

JOB_STATE_TO_USER_STATE = dict(
    {
        "P": _("Pending"),
        "R": _("Running"),
        "A": _("Question"),
        "E": _("Error"),
        "F": _("Done"),
    }
)
py_messages = dict(
    {
        "filetoloaderror": _("Error on file upload"),
        "access403": _("Access denied "),
        "notfound": _(
            "This job doesn't exist anymore, perhaps it was automatically purged"
        ),
        "jobtypeunknown": _("not known as a job UI type"),
        "import": {"nopermission": _("no permission to import")},
        "upload": {
            "nopermission": _("no permission to upload"),
            "nofile": _("no file to upload"),
        },
        "jobiderror": _("job_id error"),
        "dirlist": {"nopermission": _("no permission to list")},
        "messages": {"jobmonitor": _("this is an asynchronous process")},
    }
)
