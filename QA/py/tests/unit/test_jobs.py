import importlib
import pkgutil

import pytest

import appli.gui.jobs.by_type as by_type_pkg
from appli.gui.jobs.Job import Job, load_from_json

for _m in pkgutil.iter_modules(by_type_pkg.__path__):
    importlib.import_module(by_type_pkg.__name__ + "." + _m.name)

UI_NAMES = [
    "DarwinCoreExport",
    "GeneralImport",
    "SimpleImport",
    "UpdateImport",
    "GenExport",
    "FileImport",
    "Subset",
    "SummaryExport",
    "IdentificationExport",
    "BackupExport",
    "GeneralExport",
    "Prediction",
]


@pytest.mark.parametrize("name", UI_NAMES)
def test_find_job_class_by_name(name):
    clazz = Job.find_job_class_by_name(Job, name)
    assert clazz is not None and issubclass(clazz, Job)
    assert clazz.UI_NAME == name


def test_find_job_class_unknown():
    assert Job.find_job_class_by_name(Job, "NoSuchJob") is None


def test_ui_names_are_unique():
    seen = []

    def walk(c):
        for s in c.__subclasses__():
            seen.append(s.UI_NAME)
            walk(s)

    walk(Job)
    assert len(seen) == len(set(seen)), seen


@pytest.mark.parametrize(
    "txt, clazz, expected",
    [('{"a": 1}', dict, {"a": 1}), ("[1, 2]", list, [1, 2]), ("not json", dict, {}), ("[1]", dict, {})],
)
def test_load_from_json(txt, clazz, expected):
    assert load_from_json(txt, clazz) == expected


def test_update_import_modes():
    from appli.gui.jobs.by_type.UpdateImport import UpdateImportJob

    assert UpdateImportJob._update_mode("Y") == "Cla"
    assert UpdateImportJob._update_mode("") == "Yes"
    assert UpdateImportJob._must_skip_existing_objects() is True


def test_format_options_build(req_ctx):
    from appli.gui.jobs import job_interface as ji

    formdatas, options, links = ji.export_format_options()
    assert "general" in formdatas and formdatas["general"]["path"] == "/gui/job/create/GeneralExport"
    assert isinstance(options, dict)
    formdatas, options, links = ji.import_format_options()
    assert formdatas and isinstance(options, dict) and links is None


@pytest.mark.parametrize(
    "target, _type",
    [("project", t) for t in ("general", "backup", "summary", "identification")]
    + [("collection", t) for t in ("darwincore", "general", "backup", "summary", "identification")],
)
def test_export_options_for_type(req_ctx, target, _type):
    from appli.gui.jobs import job_interface as ji

    formdata, option, links = ji.export_format_options(_type=_type, target=target)
    assert list(formdata) == [_type]
    assert _type in option
    # ftp option for all but darwincore
    assert (len(option) > 1) == (_type != "darwincore")
    # links to the other export types
    assert _type not in [l["path"].rsplit("/", 1)[-1].lower() for l in links if l["path"].endswith(_type)]
    assert len(links) >= 3
