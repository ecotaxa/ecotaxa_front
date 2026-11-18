import pytest

from fakes import api_exception, model
from to_back.ecotaxa_cli_py.api import JobsApi
from to_back.ecotaxa_cli_py.models import JobModel


def _job(id=5, type="Subset", state="R", params=None, **kw):
    return model(
        JobModel,
        id=id,
        owner_id=42,
        type=type,
        state=state,
        step=1,
        progress_pct=40,
        progress_msg="working",
        params=params if params is not None else {"prj_id": 1},
        result={},
        errors=[],
        question={},
        reply={},
        inside={},
        creation_date="2026-11-04T10:00:00",
        updated_on="2026-11-04T10:05:00",
        **kw,
    )


def test_job_status_json(user_client, backend):
    # a type without UI class: no final action
    get_job = backend.on(JobsApi, "get_job", returns=_job(type="NoUiForThis"))
    rsp = user_client.get("/gui/job/status/5")
    assert rsp.status_code == 200
    body = rsp.get_json()
    assert body["id"] == 5 and body["state"] == "R" and body["progress_pct"] == 40
    assert "finalaction" not in body
    get_job.assert_called_once_with(job_id=5)


@pytest.mark.parametrize(
    "exp_type, ui_type",
    [("TSV", "GeneralExport"), ("BAK", "BackupExport"), ("ABO", "SummaryExport"), ("XYZ", "SummaryExport")],
)
def test_job_status_legacy_export_type(user_client, backend, mocker, exp_type, ui_type):
    from appli.gui.jobs.Job import Job

    backend.on(JobsApi, "get_job", returns=_job(type="GenExport", params={"req": {"exp_type": exp_type}}))
    spy = mocker.spy(Job, "find_job_class_by_name")
    rsp = user_client.get("/gui/job/status/5")
    assert rsp.status_code == 200
    assert spy.call_args.args[1] == ui_type


def test_job_force_restart(user_client, backend):
    restart = backend.on(JobsApi, "restart_job")
    rsp = user_client.get("/gui/job/forcerestart/5")
    assert rsp.status_code == 302
    assert rsp.headers["Location"].endswith("/gui/job/show/5")
    restart.assert_called_once_with(job_id=5)


@pytest.mark.parametrize("status", [403, 404])
def test_job_show_refused_goes_to_list(user_client, backend, status):
    backend.on(JobsApi, "get_job", raises=api_exception(status))
    rsp = user_client.get("/gui/job/show/5")
    assert rsp.status_code == 302
    assert rsp.headers["Location"] == "/gui/jobs/listall"


def test_job_log_missing_answers_text(user_client, backend):
    backend.on(JobsApi, "get_job_log_file", raises=api_exception(500))
    rsp = user_client.get("/gui/job/show/5?log=Y")
    assert rsp.status_code == 500
    assert rsp.mimetype == "text/plain"


def test_job_log(user_client, backend):
    backend.on(JobsApi, "get_job_log_file", returns="line1\nline2")
    rsp = user_client.get("/gui/job/show/5?log=Y")
    assert rsp.status_code == 200
    assert rsp.data == b"line1\nline2"


# ------------------------------------------------------------- job creation dialogs

CREATE_TYPES = [
    "GeneralExport",
    "SummaryExport",
    "BackupExport",
    "IdentificationExport",
    "DarwinCoreExport",
    "FileImport",
    "SimpleImport",
    "GeneralImport",
    "UpdateImport",
    "Subset",
]


@pytest.fixture
def project_backend(backend):
    from fakes import make_project
    from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi
    from to_back.ecotaxa_cli_py.models import ProjectTaxoStatsModel

    backend.on(ProjectsApi, "project_query", returns=make_project(1))
    backend.on(
        ProjectsApi,
        "project_set_get_stats",
        returns=[
            model(ProjectTaxoStatsModel, projid=1, used_taxa=[], nb_unclassified=1, nb_validated=2, nb_dubious=0, nb_predicted=3)
        ],
    )
    backend.on(UsersApi, "get_current_user_prefs", returns="")
    return backend


@pytest.mark.parametrize("job_type", CREATE_TYPES)
def test_job_create_dialog(user_client, project_backend, job_type):
    rsp = user_client.get(f"/gui/job/create/{job_type}?projid=1")
    assert rsp.status_code == 200, job_type
    assert b"Test project" in rsp.data


def test_job_create_unknown_type(user_client):
    rsp = user_client.get("/gui/job/create/NoSuchJob?projid=1")
    assert rsp.status_code == 404


def _failed_import(source_path="import_20261117_abc123"):
    return _job(type="FileImport", state="E", params={"prj_id": 1, "req": {"source_path": source_path}})


def test_failed_import_tells_where_the_files_are(user_client, backend):
    import json
    from to_back.ecotaxa_cli_py.api import UsersApi

    backend.on(JobsApi, "get_job", returns=_failed_import())
    manifest = {"source_path": "import_20261117_abc123", "entries": [{"staged": "a", "original": "x/a"}]}
    backend.on(UsersApi, "get_current_user_prefs", returns=json.dumps(manifest))
    body = user_client.get("/gui/job/status/5").get_json()
    assert "import_20261117_abc123" in body["erroraction"]


def test_failed_import_of_a_folder_has_no_message(user_client, backend):
    # a folder imported as is, not gathered from a selection
    from to_back.ecotaxa_cli_py.api import UsersApi

    backend.on(JobsApi, "get_job", returns=_failed_import("my_folder"))
    backend.on(UsersApi, "get_current_user_prefs", returns="")
    body = user_client.get("/gui/job/status/5").get_json()
    assert body["erroraction"] == ""


@pytest.mark.parametrize(
    "question, expected",
    [
        ({"missing_taxa": ["copepoda"]}, ["Taxonomy manual mapping"]),
        ({"missing_users": ["Jane Doe"]}, ["Users manual mapping"]),
        (
            {"missing_taxa": ["copepoda"], "missing_users": ["Jane Doe"]},
            ["Taxonomy manual mapping", "Users manual mapping"],
        ),
    ],
)
def test_import_question_page(user_client, backend, question, expected):
    # "... or if (users...)" in the template crashed when there were only missing users
    from conftest import page_chrome
    from fakes import make_min_user, make_project
    from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi, UsersApi

    page_chrome(backend)
    job = _job(type="FileImport", state="A", params={"prj_id": 1})
    job.question = question
    backend.on(JobsApi, "get_job", returns=job)
    backend.on(UsersApi, "get_user", returns=make_min_user(id=42, name="Owner", email="o@example.org"))
    backend.on(ProjectsApi, "project_query", returns=make_project(1))
    backend.on(TaxonomyTreeApi, "get_taxonomy_recast", returns=None)
    rsp = user_client.get("/gui/job/question/5")
    assert rsp.status_code == 200, rsp.data[:500]
    body = rsp.get_data(as_text=True)
    for a_text in expected:
        assert a_text in body
    assert "Continue" in body
