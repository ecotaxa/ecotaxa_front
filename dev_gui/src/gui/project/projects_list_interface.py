# list : full project list table def - homepage
# import-[...] settings table def - projectsettings page create or update
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    MinUserModel,
)

from flask_babel import _


def project_table_columns(typeimport: str, selection: str = "list") -> list:
    if typeimport == "":
        selection = selection
    else:
        selection = "import"
    columns = {
        "list": [
            {
                "label": _("ID"),
                "sortable": "desc",
                "field": "projid",
                "format": "number",
            },
            {
                "label": _("Instrument"),
                "field": "instrument",
                "autocomplete": "instrument",
            },
            {
                "label": _("Title"),
                "field": "title",
                "request": "about",
                "subfield": "contact",
                "sublabel": " - manager or contact",
            },
            {"label": _("contact"), "hidden": "true", "field": "contact"},
            {"label": _("Status"), "field": "status"},
            {
                "label": _("Visibility"),
                "field": "visible",
                "format": "check",
                "value": "Y",
            },
            {"label": _("License"), "field": "license", "format": "license"},
            {"label": _("Nb objects"), "field": "objcount", "format": "number"},
            {
                "label": _("%validated"),
                "field": "pctvalidated",
                "format": "progress",
                "default": "0.0",
            },
        ],
        "import": {
            "commons": [
                {
                    "label": _("ID"),
                    "field": "projid",
                    "format": "number",
                },
                {
                    "label": _("Instrument"),
                    "field": "instrument",
                    "autocomplete": "instrument",
                },
                {
                    "label": _("Title"),
                    "field": "title",
                },
            ],
            "taxo": [
                {
                    "label": _("Preset categories"),
                    "field": "preset",
                    "format": "taxons",
                },
                {
                    "label": _("Extra categories used"),
                    "field": "objtaxonnotinpreset",
                    "format": "taxons",
                },
            ],
            "privileges": [
                {"label": _("Members"), "field": "privileges", "format": "privileges"},
                {"label": _("contact"), "hidden": "true", "field": "contact"},
            ],
            "fields": [
                {"label": "presets", "field": "popoverfieldlist", "format": "text"},
            ],
            "settings": [
                {"label": _("status"), "field": "status"},
                {"label": _("description"), "field": "description", "hidden": "true"},
                {"label": _("comments"), "field": "comments", "hidden": "true"},
                {"label": _("contact"), "field": "contact", "hidden": "true"},
                {"label": _("members"), "field": "privileges", "format": "privileges"},
                {"label": _("license"), "field": "license", "format": "license"},
                {
                    "label": _("Visibility"),
                    "field": "visible",
                    "format": "check",
                    "value": "Y",
                    "hidden": "true",
                },
                {"label": _("presets"), "field": "popoverfieldlist", "format": "text"},
                {
                    "label": _("init classif"),
                    "field": "init_classif_list",
                    "hidden": "true",
                },
                {"label": _("Deep feature ext."), "field": "cnn_network_id"},
            ],
        },
        "samples": [
            {
                "label": _("ID"),
                "sortable": "desc",
                "field": "sampleid",
                "hidden": "true",
                "format": "number",
            },
            {
                "label": _("Sample ID"),
                "field": "orig_id",
            },
            {
                "label": _("used taxa"),
                "field": "used_taxa",
                "format": "taxa",
            },
        ],
        "validations": [
            {"label": _("validated"), "field": "nb_validated", "format": "validation"},
            {"label": _("dubious"), "field": "nb_dubious", "format": "validation"},
            {"label": _("predicted"), "field": "nb_predicted", "format": "validation"},
            {
                "label": _("none"),
                "field": "nb_unclassified",
                "format": "validation",
            },
        ],
    }
    select = {
        "taxo": {
            "field": "select",
            "select": "taxo",
            "parts": ["preset", "objtaxonnotinpreset"],
            "selectcells": [
                "preset",
                "objtaxonnotinpreset",
            ],
        },
        "privileges": {
            "field": "select",
            "select": "privileges",
            "parts": ["privileges"],
            "selectcells": ["privileges", "contact"],
        },
        "fields": {
            "field": "select",
            "select": "fields",
            "selectcells": ["popoverfieldlist"],
        },
        "settings": {
            "label": _("select"),
            "field": "select",
            "select": "settings",
            "selectcells": [
                "title",
                "description",
                "comments",
                "instrument",
                "contact",
                "cnn_network_id",
                "visible",
                "status",
                "license",
                "popoverfieldlist",
                "init_classif_list",
                "privileges",
            ],
        },
    }

    if selection == "import":
        ths = (
            [select[typeimport]]
            + columns["import"]["commons"]
            + columns["import"][typeimport]
        )
        # tag seletected columns to import
        for i, th in enumerate(ths):
            ths[i]["data"] = dict({})
            if "autocomplete" in th:
                ths[i]["data"].update({"autocomplete": th["autocomplete"]})
            if "parts" in th:
                ths[i]["data"].update({"parts": th["parts"]})
            if "value" in th:
                ths[i]["data"].update({"value": th["value"]})
            if th["field"] in select[typeimport]["selectcells"]:
                ths[i]["data"].update({"name": th["field"]})

            elif th["field"] == "select":
                ths[i]["data"].update({"what": typeimport})

        return ths
    elif selection == "list":
        return [{"field": "select", "select": "controls"}] + columns[selection]
    else:
        return columns[selection]


def render_samples_stats(
    samples: list,
    samplestats: list,
    partial: bool = True,
    format: str = "json",
    withtaxa: bool = True,
) -> dict:

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
        if withtaxa == True:
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
    if withtaxa == True:
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


def render_stat_proj(prj: ProjectModel, partial: bool = True) -> dict:
    if partial == True:
        return dict(
            {
                "projid": prj.projid,
                "title": prj.title,
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
                "title": prj.title,
                "description": prj.description,
                "comments": prj.comments,
                "privileges": _render_privileges(prj),
                "cnn_network_id": prj.cnn_network_id,
                "instrument": prj.instrument,
                "license": prj.license,
                "sample_free_cols": prj.sample_free_cols,
                "acquisition_free_cols": prj.acquisition_free_cols,
                "process_free_cols": prj.process_free_cols,
                "obj_free_cols": prj.obj_free_cols,
            }
        )


def render_for_js(prjs: list, columns: list, can_access: list, isadmin: bool) -> list:
    from appli.gui.staticlistes import py_project_status

    jsonprjs = list([])
    translations = dict(
        {
            "controls": dict(
                {
                    "A": dict({"A": _("Annotate")}),
                    "V": dict({"V": _("View")}),
                    "R": dict({"R": _("Request Access")}),
                    "M": dict({"M": _("Manage")}),
                }
            ),
            "status": py_project_status,
        }
    )
    for prj in prjs:
        jsonprj = list([])

        for column in columns:

            if column["field"] == "privileges":
                privileges = _render_privileges(prj)
                jsonprj.append(privileges)

            else:
                # if subfield  append object which will be formatted by the js component
                if column["field"] == "select":
                    if column["select"] == "controls":
                        select = dict({})
                        if prj.status != "ExploreOnly" and (
                            (
                                prj.projid
                                in can_access["Manage"] + can_access["Annotate"]
                            )
                            or isadmin
                        ):
                            select.update(translations["controls"]["A"])
                        elif prj.projid in can_access["View"] or isadmin:
                            select.update(translations["controls"]["V"])
                        else:
                            if prj.visible:
                                select.update(translations["controls"]["V"])
                            select.update(translations["controls"]["R"])
                        if prj.projid in can_access["Manage"] or isadmin:
                            select.update(translations["controls"]["M"])
                        attrvalue = select
                    else:
                        attrvalue = ""

                elif type(prj) == dict:
                    # data come from different types (if taxo it's  dict)
                    attrvalue = prj[column["field"]]

                else:
                    attrvalue = getattr(prj, column["field"])
                    if column["field"] in translations:
                        if attrvalue in translations[column["field"]]:
                            attrvalue = translations[column["field"]][attrvalue]

                if "request" in column:
                    if column["request"] == "about":
                        if (
                            isadmin
                            or (prj.status == "Annotate" or prj.status == "View")
                            and (
                                prj.projid
                                in can_access["View"]
                                + can_access["Manage"]
                                + can_access["Annotate"]
                            )
                        ):
                            attrvalue = list([attrvalue, 1])
                        else:
                            attrvalue = list([attrvalue, 0])
                if "hidden" in column:
                    if column["field"] == "contact":
                        if prj.contact:
                            attrvalue = prj.contact.to_dict()
                            attrvalue.update({"contact": 1})

                        elif len(prj.managers):
                            attrvalue = prj.managers[0].to_dict()
                        else:
                            attrvalue = ""

                jsonprj.append(attrvalue)
        jsonprjs.append(jsonprj)
    return jsonprjs


def render_prj_summary(prj: ProjectModel) -> dict:
    # for jobs
    return dict(
        {
            "projid": prj.projid,
            "title": prj.title,
            "contact": prj.contact,
        }
    )


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
