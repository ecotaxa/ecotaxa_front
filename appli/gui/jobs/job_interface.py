from flask_babel import _
from typing import Dict
from flask import request
from appli.utils import ApiClient
from appli.gui.jobs.staticlistes import JOB_STATE_TO_USER_STATE
from to_back.ecotaxa_cli_py import ApiException, MinUserModel
from to_back.ecotaxa_cli_py.api import UsersApi
from to_back.ecotaxa_cli_py.models import JobModel


def export_format_options(type=None):
    options = dict(
        {
            "general": {
                "only_annotations": {
                    "label": _("Only save objects' last annotation data"),
                    "options": [
                        {"label": _("Yes"), "value": 1},
                        {"label": _("No"), "value": 0},
                    ],
                    "format": "radio",
                    "discard": "with_images|none,with_internal_ids|0,with_types_row|0,split_by|none",
                    "help": "help_export_only_annotations",
                },
                "with_images": {
                    "label": _("Images"),
                    "options": [
                        {"label": _("First image"), "value": "first"},
                        {"label": _("All images"), "value": "all"},
                        {"label": _("None"), "value": "none"},
                    ],
                    "format": "radio",
                    "help": "help_export_with_images",
                },
                "with_internal_ids": {
                    "label": _("Internal database IDs"),
                    "options": [
                        {"label": _("Yes"), "value": 1},
                        {"label": _("No"), "value": 0},
                    ],
                    "format": "radio",
                },
                "with_types_row": {
                    "label": _("Add an EcoTaxa-compatible second line with types"),
                    "options": [
                        {"label": _("Yes"), "value": 1},
                        {"label": _("No"), "value": 0},
                    ],
                    "format": "radio",
                },
                # "taxo_mapping": {
                #    "label": _(
                #        "Mapping from present taxon (key) to output replacement one (value)"
                #    ),
                #    "comment": _(
                #        "Use a null replacement to _discard_ the present taxon"
                #    ),
                #    "format": "textarea",
                # },
                "split_by": {
                    "label": _("Separate (in ZIP sub-directories) output by"),
                    "options": [
                        {"label": _("Sample"), "value": "sample"},
                        {"label": _("Acquisition"), "value": "acquisition"},
                        {"label": _("Taxon"), "value": "taxon"},
                        {"label": _("None"), "value": "none"},
                    ],
                    "format": "radio",
                },
                "out_to_ftp": {
                    "label": _(
                        "Copy result file to FTP area. Original file is still available"
                    ),
                    "options": [
                        {"label": _("Yes"), "value": 1},
                        {"label": _("No"), "value": 0},
                    ],
                    "format": "radio",
                },
            }
        }
    )
    formdatas = dict(
        {
            "general": {
                "path": "/gui/job/create/GeneralExport",
                "title": _("General Export"),
                "legend": _("Configurable objects export"),
                "datas": {
                    "split_by": ("none", False),
                    "with_images": ("none", False),
                    "with_internal_ids": (0, False),
                    "with_types_row": (0, False),
                    "only_annotations": (0, False),
                    "out_to_ftp": (0, False),
                },
            },
            "backup": {
                "path": "/gui/job/create/BackupExport",
                "title": _("Backup Export"),
                "legend": _("Backup export, for restoring or archiving"),
                "datas": {
                    "split_by": ("sample", True),
                    "with_images": ("all", True),
                    "with_internal_ids": (False, True),
                    "with_types_row": (1, True),
                    "only_annotations": (0, True),
                    "out_to_ftp": (0, False),
                },
            },
            "summary": {
                "path": "/gui/job/create/SummaryExport",
                "title": _("Summary Export"),
                "legend": _("Synthetic taxon-oriented export"),
                "datas": {
                    "quantity": ("abundance", False),
                    "summarise_by": ("none", False),
                    "taxo_mapping": ({}, False),
                    "formulae": (
                        """
    subsample_coef: 1/ssm.sub_part
    total_water_volume: sam.tot_vol/1000
    individual_volume: 4.0/3.0*math.pi*(math.sqrt(obj.area/math.pi)*ssm.pixel_size)**3 """,
                        False,
                    ),
                    "out_to_ftp": (0, False),
                },
            },
        }
    )

    options["summary"] = dict(
        {
            "quantity": {
                "label": _("Quantity to compute"),
                "options": [
                    {"label": _("Abundance"), "value": "abundance"},
                    {"label": _("Concentration"), "value": "concentration"},
                    {"label": _("Biovolume"), "value": "biovolume"},
                ],
                "format": "radio",
                "help": "help_export_summary_quantity",
            },
            "summarise_by": {
                "label": _("Computations aggregation level"),
                "options": [
                    {"label": _("Sample"), "value": "sample"},
                    {"label": _("Acquisition"), "value": "acquisition"},
                    {"label": _("None"), "value": "none"},
                ],
                "format": "radio",
            },
            "taxo_mapping": {
                "label": _("Mapping from present taxon to output replacement one "),
                "comment": _(" Type '_discard_' to discard taxon"),
                "format": "taxoline",
                "help": "help_export_summary_taxo_mapping",
                "addoption": "_discard_,0",
            },
            "formulae": {
                "label": _("Formulae"),
                "example": '{"subsample_coef"->str, "total_water_volume"->str, "individual_volume"->str}',
                "format": "textarea",
                "help": "help_export_summary_formulae",
            },
            "out_to_ftp": {
                "label": _(
                    "Copy result file to FTP area. Original file is still available"
                ),
                "options": [
                    {"label": _("Yes"), "value": 1},
                    {"label": _("No"), "value": 0},
                ],
                "format": "radio",
            },
        }
    )
    if type != None:
        formdata = dict()
        option = dict()
        formdata[type] = formdatas[type]
        if type == "backup":
            typoption = "general"
        else:
            typoption = type
        option[type] = options[typoption]
        export_links = []
        for key, fdata in formdatas.items():
            if key != type:
                export_links.append({"path": fdata["path"], "title": fdata["title"]})
        return formdata, option, export_links
    else:
        options["backup"] = options["general"]
    return formdatas, options, None


def import_format_options(type=None) -> dict:
    taxomapping = dict(
        {
            "taxo_mapping": {
                "label": _("Mapping from present taxon to output replacement one "),
                "comment": _(" Type '_discard_' to discard taxon"),
                "format": "taxoline",
                "help": "help_import_summary_taxo_mapping",
                "addoption": "_discard_,0",
            }
        },
    )
    formdatas = dict(
        {
            "general": {
                "path": "/gui/job/create/GeneralImport",
                "title": _("General Import"),
                "legend": _("Import Images and TSV files"),
                "datas": {
                    "skiploaded": False,
                    "skipobjectduplicate": False,
                },
            },
            "simple": {
                "path": "/gui/job/create/SimpleImport",
                "title": _("Simple Import"),
                "legend": _(
                    "Import images in jpg, png, gif (possibly animated) formats and associate a fixed & reduced set of metadata, that you can enter below."
                ),
            },
            "update": {
                "path": "/gui/job/create/UpdateImport",
                "title": _("Update Metadata"),
                "legend": _("Update metada associated to already importer images"),
                "datas": {"updateclassif": False},
            },
        }
    )

    options = dict(
        {
            "general": {
                "skiploaded": {
                    "label": _("Skip tsv that have already been imported"),
                    "format": "checkbox",
                    "value": "Y",
                },
                "skipobjectduplicate": {
                    "label": _("Skip objects that have already been imported"),
                    "format": "checkbox",
                    "value": "Y",
                },
                "advanced_options": taxomapping,
            },
            "simple": {"metadata": {"label": _("Metadata"), "format": "array"}},
            "update": {
                "updateclassif": {
                    "label": _("Allow update of classification data"),
                    "format": "checkbox",
                    "value": "Y",
                },
                "advanced_options": taxomapping,
            },
        }
    )
    return formdatas, options, None


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
