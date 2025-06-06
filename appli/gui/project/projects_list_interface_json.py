# list : full project list table def - homepage
# import-[...] settings table def - projectsettings page create or update

from to_back.ecotaxa_cli_py.models import ProjectModel
from typing import List, Dict
from flask_babel import _


def project_table_columns(
    typeimport: str, selection: str = "list", listall: bool = False
) -> dict:
    if typeimport == "":
        selection = selection
    else:
        selection = "import"
    # return only visible columns names and display props
    if not listall:
        columns_list = dict(
            {
                "projid": {
                    "label": _("ID"),
                    "sortable": "desc",
                    "format": "number",
                },
                "instrument": {
                    "label": _("Instrument"),
                    "autocomplete": "instrument",
                },
                "title": {
                    "label": _("Title"),
                    "request": "about",
                    "subfield": "contact",
                    "sublabel": " - manager or contact",
                    "trim": True,
                },
                "contact": {"label": _("Contact"), "hidden": True},
                "annotators": {"label": _("Annotators"), "hidden": True},
                "managers": {"label": _("Managers"), "hidden": True},
                "viewers": {"label": _("Viewers"), "hidden": True},
                "status": {"label": _("Status"), "format": "status"},
                "access": {"label": _("Access"), "format": "access"},
                "objcount": {"label": _("Nb objects"), "format": "number"},
                "pctvalidated": {
                    "label": _("%validated"),
                    "format": "progress",
                    "default": "0.0",
                },
            }
        )
    else:
        columns_list = dict(
            {
                "projid": {
                    "label": _("ID"),
                    "sortable": "desc",
                    "format": "number",
                },
                "instrument": {
                    "label": _("Instrument"),
                    "autocomplete": "instrument",
                },
                "title": {
                    "label": _("Title"),
                    "request": "about",
                    "subfield": "contact",
                    "sublabel": " - manager or contact",
                    "trim": True,
                },
                "contact": {"label": _("Contact"), "hidden": True},
                "status": {"label": _("Status"), "format": "status"},
                "access": {"label": _("Access"), "format": "access"},
                "objcount": {"label": _("Nb objects"), "format": "number"},
                "pctvalidated": {
                    "label": _("%validated"),
                    "format": "progress",
                    "default": "0.0",
                },
            }
        )
    columns = {
        "list": columns_list,
        "prediction": dict(
            {
                "select": {
                    "select": "selectmultiple",
                    "field": "projid",
                    "emptydata": "projid",
                },
                "projid": {
                    "label": "ID",
                },
                "instrument": {
                    "label": _("Instrument"),
                },
                "title": {"label": _("Title"), "trim": True},
                "validated_nb": {"label": _("Validated nb"), "format": "number"},
                "matching_nb": {"label": _("Matching nb"), "format": "number"},
                "deep_model": {"label": _("Deep features")},
            }
        ),
        "import": {
            "commons": dict(
                {
                    "projid": {
                        "label": _("ID"),
                        "format": "number",
                    },
                    "instrument": {
                        "label": _("Instrument"),
                        "autocomplete": "instrument",
                    },
                    "title": {"label": _("Title"), "trim": True},
                }
            ),
            "taxo": dict(
                {
                    "preset": {
                        "label": _("Preset categories"),
                        "format": "taxons",
                    },
                    "objtaxonnotinpreset": {
                        "label": _("Extra categories used"),
                        "format": "taxons",
                    },
                }
            ),
            "privileges": dict(
                {
                    "privileges": {"label": _("Members"), "format": "privileges"},
                    "contact": {"label": _("contact"), "hidden": True},
                }
            ),
            "fields": dict(
                {
                    "classiffieldlist": {"label": "presets", "format": "text"},
                }
            ),
            "settings": dict(
                {
                    "status": {"label": _("status")},
                    "contact": {"label": _("contact"), "hidden": True},
                    "description": {"label": _("description"), "hidden": True},
                    "comments": {"label": _("comments"), "hidden": True},
                    "init_classif_list": {"label": _("preset"), "hidden": True},
                    "privileges": {"label": _("members"), "format": "privileges"},
                    "access": {"label": _("access"), "format": "access"},
                    "classiffieldlist": {"label": _("sorting tools"), "format": "text"},
                    "cnn_network_id": {"label": _("Deep feature ext.")},
                }
            ),
            "project": dict(
                {
                    "title": {"label": _("title")},
                    "status": {"label": _("status")},
                    "contact": {"label": _("contact"), "hidden": True},
                    "privileges": {"label": _("members"), "format": "privileges"},
                    "access": {"label": _("Access"), "format": "access"},
                }
            ),
        },
        "samples": dict(
            {
                "select": {
                    "select": "selectmultiple",
                    "field": "sampleid",
                    "emptydata": "sampleid",
                },
                "sampleid": {"hidden": True},
                "orig_id": {
                    "label": _("Sample ID"),
                },
                "used_taxa": {
                    "label": _("used taxa"),
                    "format": "taxa",
                },
            }
        ),
        "validations": dict(
            {
                "nb_validated": {"label": _("validated"), "format": "number"},
                "nb_dubious": {"label": _("dubious"), "format": "number"},
                "nb_predicted": {"label": _("predicted"), "format": "number"},
                "nb_unclassified": {
                    "label": _("none"),
                    "format": "number",
                },
            }
        ),
    }
    select = {
        "taxo": {
            "select": {
                "what": "taxo",
                "field": "projid",
                "selectcells": [
                    "preset",
                    "objtaxonnotinpreset",
                ],
                "parts": ["preset", "objtaxonnotinpreset"],
            }
        },
        "privileges": {
            "select": {
                "what": "privileges",
                "field": "projid",
                "selectcells": ["privileges", "contact"],
                "parts": ["privileges"],
            }
        },
        "fields": {
            "select": {
                "what": "fields",
                "field": "projid",
                "selectcells": ["classiffieldlist"],
            }
        },
        "settings": {
            "select": {
                "label": _("select"),
                "what": "settings",
                "field": "projid",
                "selectcells": [
                    "title",
                    "description",
                    "comments",
                    "instrument",
                    "contact",
                    "status",
                    "access",
                    "init_classif_list",
                    "classiffieldlist",
                    "privileges",
                    "cnn_network_id",
                ],
            },
        },
        "project": {
            "select": {
                "label": _("select"),
                "what": "project",
                "selectcells": ["projid"],
            }
        },
    }

    if selection == "import":
        ths = dict(
            {
                **select[typeimport],
                **columns["import"]["commons"],
                **columns["import"][typeimport],
            }
        )
        return ths
    elif selection == "list":
        cols = {
            **{"select": {"select": "controls", "field": "projid"}},
            **columns[selection],
        }
        return cols
    elif selection == "merge":
        cols = {
            **{"select": {"select": "select", "field": "projid"}},
            **columns["list"],
        }
        return cols
    else:
        return columns[selection]


def render_samples_stats(
    samples: list,
    samplestats: list,
    withtaxa: bool = True,
    partial: bool = True,
    _format: str = "json",
) -> List[Dict]:

    from appli.gui.taxonomy.tools import taxo_with_names

    sampleslist = dict()
    for i, sample in enumerate(samples):
        sampleslist.update({str(sample.sampleid): sample})
    used_taxa = []
    samples = []
    for i, samplestat in enumerate(samplestats):
        sampledict = dict(
            {
                "sampleid": samplestat.sample_id,
                "orig_id": sampleslist[str(samplestat.sample_id)].orig_id,
            }
        )
        if withtaxa:
            taxa = [str(t) for t in samplestat.used_taxa]
            sampledict.update({"used_taxa": samplestat.used_taxa})
            used_taxa.extend(taxa)
        sampledict.update(
            {
                "nb_validated": samplestat.nb_validated,
                "nb_dubious": samplestat.nb_dubious,
                "nb_predicted": samplestat.nb_predicted,
                "nb_unclassified": samplestat.nb_unclassified,
            }
        )

        samples.append(sampledict)
    # replace taxa ids by their names
    if withtaxa:
        if len(used_taxa) > 0:
            usedtaxa = dict({})
            for t in taxo_with_names(list(set(used_taxa))):
                usedtaxa.update(dict({str(t[0]): t[1]}))
            for i, sample in enumerate(samples):
                taxa = []
                for taxon in sample["used_taxa"]:
                    if str(taxon) in usedtaxa.keys():
                        taxa.append((taxon, usedtaxa[str(taxon)]))
                    else:
                        taxa.append((taxon, "notfound"))
                samples[i]["used_taxa"] = taxa
    return samples


def _strip_if(key, value):
    yes_strip = ["title"]
    if key in yes_strip:
        return value.strip()
    return value


def _extract_items(prj, keepkeys):
    return {k: _strip_if(k, v) for k, v in prj.items() if k in keepkeys}


def render_stat_proj(prj: ProjectModel, partial: bool = True) -> dict:
    if partial:
        return dict(
            {
                "projid": prj.projid,
                "title": prj.title.strip(),
                "status": prj.status,
                "description": prj.description,
                "privileges": _render_privileges(prj),
                "cnn_network_id": prj.cnn_network_id,
                "instrument": prj.instrument,
            }
        )
    else:
        return dict(
            {
                "projid": prj.projid,
                "title": prj.title.strip(),
                "status": prj.status,
                "description": prj.description,
                "comments": prj.comments,
                "privileges": _render_privileges(prj),
                "cnn_network_id": prj.cnn_network_id,
                "instrument": prj.instrument,
                "access": prj.access,
                "sample_free_cols": prj.sample_free_cols,
                "acquisition_free_cols": prj.acquisition_free_cols,
                "process_free_cols": prj.process_free_cols,
                "obj_free_cols": prj.obj_free_cols,
            }
        )


def render_stat_proj_json(prj: dict, partial: bool = True) -> dict:
    if partial:
        keepkeys = [
            "projid",
            "title",
            "description",
            "privileges",
            "cnn_network_id",
            "instrument",
            "status",
        ]

    else:
        keepkeys = [
            "projid",
            "title",
            "description",
            "comments",
            "privileges",
            "cnn_network_id",
            "instrument",
            "access",
            "status",
            "sample_free_cols",
            "acquisition_free_cols",
            "process_free_cols",
            "obj_free_cols",
        ]
    prj["privileges"] = dict(
        {
            "managers": prj["managers"],
            "annotators": prj["annotators"],
            "viewers": prj["viewers"],
        }
    )
    return _extract_items(prj, keepkeys)


def render_for_js(prjs: list, columns: dict, can_access: dict) -> list:
    from appli.gui.staticlistes import py_project_status
    from datetime import datetime
    from flask_login import current_user
    from to_back.ecotaxa_cli_py.models.access_level_enum import AccessLevelEnum

    isadmin = current_user.is_authenticated and current_user.is_app_admin == True
    jsonprjs = list([])
    translations = dict(
        {
            "controls": dict(
                {
                    "A": dict({"A": _("Annotate")}),
                    "V": dict({"V": _("View")}),
                    "R": dict({"R": _("Request Access")}),
                    "M": dict({"M": _("Settings")}),
                }
            ),
            "status": py_project_status,
        }
    )
    for prj in prjs:
        jsonprj = list([])
        for key, column in columns.items():
            if key == "privileges":
                jsonprj.append(
                    dict(
                        {
                            "managers": prj["managers"],
                            "annotators": prj["annotators"],
                            "viewers": prj["viewers"],
                        }
                    )
                )

            else:
                if key == "select":
                    if "select" in column and column["select"] == "controls":
                        select = dict({})
                        if prj["status"] != "ExploreOnly" and (
                            (
                                prj["projid"]
                                in can_access["Manage"] + can_access["Annotate"]
                            )
                            or isadmin
                        ):
                            select.update(translations["controls"]["A"])
                        elif isadmin or prj["projid"] in (
                            can_access["View"] + can_access["Manage"]
                        ):
                            select.update(translations["controls"]["V"])
                        elif prj["access"] in [AccessLevelEnum._1, AccessLevelEnum._2]:
                            select.update(translations["controls"]["V"])
                            select.update(translations["controls"]["R"])
                        else:
                            select.update(translations["controls"]["R"])
                        if prj["projid"] in can_access["Manage"] or isadmin:
                            select.update(translations["controls"]["M"])
                        attrvalue = select
                    else:
                        attrvalue = ""
                elif key == "contact":
                    if prj["contact"]:
                        attrvalue = prj["contact"]
                    elif len(prj["managers"]):
                        attrvalue = prj["managers"][0]
                    else:
                        attrvalue = ""
                else:
                    # data come from different types (if taxo it's  dict)
                    attrvalue = prj[key]
                    if key in translations:
                        if attrvalue in translations[key]:
                            attrvalue = translations[key][attrvalue]
                    if isinstance(attrvalue, datetime):
                        attrvalue = attrvalue.isoformat()
                if "trim" in column:
                    attrvalue = attrvalue.strip()
                if "request" in column:
                    if column["request"] == "about":
                        if (
                            isadmin
                            or (prj["status"] == "Annotate" or prj["status"] == "View")
                            and (prj["projid"] in can_access["Manage"])
                        ):
                            attrvalue = list([attrvalue, 1])
                        else:
                            attrvalue = list([attrvalue, 0])

                jsonprj.append(attrvalue)
        jsonprjs.append(jsonprj)
    return jsonprjs


def _render_privileges(prj: ProjectModel) -> dict:
    privileges = dict({})
    rights = dict(
        {
            "managers": prj.managers,
            "annotators": prj.annotators,
            "viewers": prj.viewers,
        }
    )
    for keypriv, right in rights.items():
        privileges.update(dict({keypriv: []}))

        for u in right:

            privileges[keypriv].append(u.to_dict())
    return privileges


def render_prj_summary(prj: ProjectModel) -> dict:
    # for jobs
    return dict(
        {
            "projid": prj.projid,
            "title": prj.title.strip(),
            "contact": prj.contact,
        }
    )


def render_prj_summary_json(prj: dict) -> dict:
    # for jobs
    return _extract_items(prj, ["projid", "title", "contact"])
