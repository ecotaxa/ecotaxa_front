from typing import List
from flask import flash, request, render_template
from flask_security import login_required
from flask_login import current_user
from appli import app, gvp, gvg
from appli.project import sharedfilter
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi
from to_back.ecotaxa_cli_py.models import ProjectModel, ObjectSetQueryRsp, MergeRsp

from appli.gui.commontools import is_partial_request, py_get_messages


@app.route("/gui/prj/purge/<int:projid>", methods=["GET", "POST"])
@login_required
def prj_purge(projid):
    backto = False
    objlist = []
    deleted = None
    py_messages = py_get_messages("project")
    from to_back.ecotaxa_cli_py.models import ObjectSetQueryRsp

    user: UserModelWithRights = current_user.api_user
    isadmin = user and (2 in user.can_do)
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return render_template("./v2/error.html", message="project404")
            elif ae.status in (401, 403):
                flash(py_messages["cannotpurgeprj"], "error")

    if gvp("objlist") == "":
        # Extract filter values
        filters = {}
        for k in sharedfilter.FilterList:
            if gvg(k):
                filters[k] = gvg(k, "")
        if len(filters):
            # Query objects, using filters, in project
            with ApiClient(ObjectsApi, request) as api:
                objectids: List[int] = api.get_object_set(projid, filters).object_ids
            objlist = (str(r) for r in objectids)
    else:
        if gvp("objlist") == "DELETEALL":
            # DELETE all objects

            with ApiClient(ProjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_project(
                    project_id=projid, only_objects=gvp("destroyproject") != "Y"
                )
            deleted = dict({"no": no, "noh": noh, "ni": ni, "nf": nbrfile})
        else:
            # DELETE some objects in project
            objs = [
                int(x.strip()) for x in gvp("objlist").splitlines() if x.strip() != ""
            ]
            err = None
            with ApiClient(ObjectsApi, request) as api:
                try:
                    res: ObjectSetQueryRsp = api.query_object_set_parents(objs)
                except ApiException as ae:
                    if ae.status in (401, 403):
                        err = py_messages["objectnotyours"]
                    else:
                        raise
            if err is None:
                nbnotinproject = 0
                for aprjid in res.project_ids:
                    if aprjid != projid:
                        nbnotinproject += 1
                if nbnotinproject > 0:
                    err = "%d " + py_messages["objsnotincurrentprj"] % nbnotinproject
            if err is not None:
                flash(err, "error")

            with ApiClient(ObjectsApi, request) as api:
                no, noh, ni, nbrfile = api.erase_object_set(objs)
                deleted = dict({"no": no, "noh": noh, "ni": ni, "nf": nbrfile})

        if gvp("objlist") == "DELETEALL" and gvp("destroyproject") == "Y":
            backto = True
            # flash(py_messages["prjdestroyed"], "success")

    return render_template(
        "./v2/project/purge.html",
        isadmin=isadmin,
        partial=is_partial_request,
        objlist=objlist,
        backto=backto,
        target_proj=target_proj,
        deleted=deleted,
    )


def prj_list_to_merge(target_proj: ProjectModel, excludeprjs: list = []) -> list:
    from appli.gui.project.projects_list import _prjs_list_api, list_privileges

    prjs = _prjs_list_api(
        listall=False,
        filt=dict({"title": None, "instrum": [target_proj.instrument], "subset": None}),
        for_managing=True,
    )
    prjstomerge = list([])

    for prj in prjs:
        r = True
        if prj["projid"] not in excludeprjs:
            for u in prj["managers"]:
                if current_user.id == u["id"]:
                    r = False
                    prjstomerge.append(prj)
        if r == True:
            prjs.remove(prj)
    return prjstomerge


@app.route("/gui/prj/merge/<int:projid>", methods=["GET", "POST"])
@login_required
def prj_merge(projid):
    # Security & sanity checks
    py_messages = py_get_messages("project")
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                err = py_messages["notfound"]
            elif ae.status in (401, 403):
                err = py_messages["cannotmergeprj"]
            else:
                raise
            flash(ae.status + " " + ae.reason, "error")

    excludeprjs = [target_proj.projid]
    prjstomerge = None
    srcprojid = 0
    source_proj = None
    if gvp("src"):
        srcprojid = int(gvp("src", 0))
    if srcprojid > 0:
        with ApiClient(ProjectsApi, request) as api:
            try:
                source_proj: ProjectModel = api.project_query(
                    srcprojid, for_managing=True
                )

                if not gvp("merge"):  # Ici la src à été choisie et vérifiée
                    # Validate the merge
                    with ApiClient(ProjectsApi, request.cookies.get("session")) as api:
                        rsp2: MergeRsp = api.project_merge(
                            project_id=target_proj.projid,
                            source_project_id=source_proj.projid,
                            dry_run=True,
                        )

                    for an_error in rsp2.errors:
                        flash(an_error, "error")

                    if len(rsp2.errors) == 0:
                        return render_template(
                            "/v2/project/merge.html",
                            target_proj=target_proj,
                            source_proj=source_proj,
                            processstep="ask",
                        )
                    else:
                        flash("Pick another source project.", "info")
                        excludeprjs.append(source_proj.projid)
            except ApiException as ae:
                if ae.status == 404:
                    flash("Source project doesn't exist", "warning")
                elif ae.status in (401, 403):
                    flash("You cannot merge from this project", "error")
                    excludeprjs.append(srcprojid)
            if gvp("merge") == "Y" and source_proj:
                # Do the real merge

                with ApiClient(ProjectsApi, request.cookies.get("session")) as api:
                    _rsp: MergeRsp = api.project_merge(
                        project_id=target_proj.projid,
                        source_project_id=source_proj.projid,
                        dry_run=False,
                    )
                    prjstomerge = None
                return render_template(
                    "/v2/project/merge.html", target_proj=target_proj, processstep="end"
                )
    # Fetch the potential merge sources
    prjstomerge = prj_list_to_merge(target_proj, excludeprjs=excludeprjs)
    return render_template(
        "./v2/project/merge.html",
        target_proj=target_proj,
        prjstomerge=prjstomerge,
    )


######################################################################################################################
# noinspection PyPep8Naming,SpellCheckingInspection
@app.route("/gui/prj/editannot/<int:projid>", methods=["GET", "POST"])
@login_required
def gui_prj_editannot(projid):
    from to_back.ecotaxa_cli_py.api import UsersApi

    # Security & sanity checks
    error = None
    authors = None
    target_for_api = None
    fromto = dict({"from": None, "to": None})
    taxoimpact = None
    nbrows = None
    # Store posted variables
    if request.method == "POST":
        from to_back.ecotaxa_cli_py.models import (
            MinUserModel,
            ObjectSetRevertToHistoryRsp,
        )

        old_author_id = gvp("oldauthor")
        # Note: is an id or one of the special choices below
        new_author_id = gvp("newauthor")
        date_filter = dict(
            {
                "date": gvp("filtdate"),
                "hour": gvp("filthour", "00"),
                "minutes": gvp("filtmin", "00"),
            }
        )
    else:
        old_author_id = None
        new_author_id = None
        date_filter = dict({"date": None, "hour": "00", "minutes": "00"})
        process = None

    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exist", "warning")
            elif ae.status in (401, 403):
                flash("You cannot do mass annotation edition on this project", "error")
            error = ae.status

    # ############### 1er Ecran
    if not (old_author_id and new_author_id):

        # Selection lists, special choices, in first

        authors = list([])
        # TODO: It would be nice to offer only relevant users as a choice
        # changed to annotators list of the project
        # with ApiClient(UsersApi, request) as api:
        #    all_users: List[MinUserModel] = api.search_user(by_name="%%")
        # from to_back.ecotaxa_cli_py.models import ProjectUserStatsModel

        with ApiClient(ProjectsApi, request) as api:
            all_users: List[ProjectUserStatsModel] = api.project_set_get_user_stats(
                ids=str(projid)
            )
            # No guaranteed order from API, so sort now, see #475 for the strip()
            if iter(all_users) and len(all_users):
                annotators = all_users[0].annotators
                # Complete selection lists
                for usr in annotators:
                    authors.append((usr.id, usr.name))
                authors.sort(key=lambda usr: usr[1].strip())

    # Use filtering on target
    filters: Dict[str, str] = {}

    # Define the to-be-modified set of objects
    if old_author_id != None and old_author_id != "anyuser":
        with ApiClient(UsersApi, request) as api:
            # Let the eventual 404 propagate
            old_author: MinUserModel = api.get_user(user_id=int(old_author_id))
        # Only return objects classified by the requested user, and exclude him/her from history picking
        filters["filt_last_annot"] = old_author_id
        fromto["from"] = old_author.name

    if date_filter["date"] != None and date_filter["date"] != "":
        filters["validfromdate"] = (
            date_filter["date"]
            + " "
            + (date_filter["hour"])
            + ":"
            + (date_filter["minutes"])
        )
        # Ask for Predicted as well, for rollback of WoRMS migrations
        filters["statusfilter"] = "PVD"

    # Define how to modify them
    if new_author_id == "lastannot":
        target_for_api = None
    elif new_author_id != None:
        with ApiClient(UsersApi, request) as api:
            # Let the eventual 404 propagate
            new_author: MinUserModel = api.get_user(user_id=int(new_author_id))
        target_for_api = new_author_id
        fromto["to"] = new_author.name

    # ############### 2nd Ecran, affichage liste des categories & estimations
    if new_author_id != None:
        if not gvp("process"):
            # Query the filtered list in project, if no filter then it's the whole project
            with ApiClient(ObjectsApi, request) as api:
                # TODO: It's getting long these primitive names...
                call = api.revert_object_set_to_history
                res: ObjectSetRevertToHistoryRsp = call(
                    project_id=projid,
                    project_filters=filters,
                    target=target_for_api,
                    dry_run=True,
                )
            # Summarize/group changes
            # Display categories choice
            taxoimpact = _gui_digest_changes(res)

        # ############### 3eme Ecran Execution Requetes
        if gvp("process") == "Y":
            selected_taxa = ",".join((x[4:] for x in request.form if x[0:4] == "taxo"))
            if selected_taxa == "":
                flash(
                    "You must select at least one category to do the replacement",
                    "error",
                )
                error = "nocat"
            else:
                filters["taxo"] = selected_taxa
                with ApiClient(ObjectsApi, request) as api:
                    call = api.revert_object_set_to_history
                    res2: ObjectSetRevertToHistoryRsp = call(
                        project_id=projid,
                        project_filters=filters,
                        target=target_for_api,
                        dry_run=False,
                    )
                    # Display change outcome
                nbrows = (len(res2.last_entries),)
        else:
            nbrows = None
    return render_template(
        "/v2/project/massannotation.html",
        target_proj=target_proj,
        fromto=fromto,
        oldauthor=old_author_id,
        newauthor=new_author_id,
        authors=authors,
        filtdate=date_filter,
        taxoimpact=taxoimpact,
        nbrows=nbrows,
        error=error,
    )


def _gui_digest_changes(api_result):
    """
    From provided changes (full list!), do a summary of what will happen.
    """
    from to_back.ecotaxa_cli_py.models import HistoricalLastClassif

    ret = []
    # noinspection PyUnresolvedReferences
    for classif_id, names in api_result.classif_info.items():
        classif_id = int(classif_id)  # No 'int' in dict keys for openapi?
        for_disp = {
            "id": classif_id,
            "name": names[0] + " (" + str(names[1]) + ")",
            "nbr": 0,
            "dest": {},
        }
        ret.append(for_disp)
    ret.append({"id": None, "name": "Nothing", "nbr": 0, "dest": {}})
    data_by_id = {dat["id"]: dat for dat in ret}
    an_entry: HistoricalLastClassif
    for an_entry in api_result.last_entries:
        summary = data_by_id[an_entry.classif_id]
        summary["nbr"] += 1
        # Determine the future classification ID & name
        future = summary["dest"]
        if an_entry.histo_classif_id is None:
            future_name = "Nothing"
        else:
            future_name = data_by_id[an_entry.histo_classif_id]["name"]
        if future_name in future:
            future[future_name] += 1
        else:
            future[future_name] = 1
    ret = [rec for rec in ret if rec["nbr"] > 0]
    ret.sort(key=lambda rec: rec["name"])
    return ret


######################################################################################################################
@app.route("/gui/prj/resettopredicted/<int:projid>", methods=["GET", "POST"])
@login_required
def prj_reset_to_predicted(projid):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504
    error = None
    processstep = None
    objectids = None
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exists", "warning")
            elif ae.status in (401, 403):
                flash("You cannot do reset to predicted on this project", "error")
            error = ae.status

    filters = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filters[k] = gvg(k, "")

    proceed = gvp("process")
    if proceed == "Y":
        # Do the job on back-end
        with ApiClient(ObjectsApi, request) as api:
            api.reset_object_set_to_predicted(projid, filters)

        flash("Data updated", "success")
    else:
        if len(filters):
            # Query the filtered list in project
            with ApiClient(ObjectsApi, request) as api:
                objectids: List[int] = api.get_object_set(projid, filters).object_ids
                # Warn the user

    # The eventual filter is in the URL (GET), so when POST-ed again after validation, the filter is preserved
    return render_template(
        "/v2/project/resettopredicted.html",
        target_proj=target_proj,
        proceed=proceed,
        objectids=objectids,
        error=error,
        warning=len(filters),
    )


######################################################################################################################
def _get_field_list(prj_model: ProjectModel) -> list:

    from to_back.ecotaxa_cli_py.models import ObjectHeaderModel

    fieldlist = []

    excluded = set()
    for k in ObjectHeaderModel.openapi_types.keys():
        # TODO: Hardcoded, not rename-friendly
        if k not in ("objid",):
            fieldlist.append({"id": "h" + k, "text": "object." + k})
        else:
            excluded.add(k)
    assert excluded == {"objid"}, "Attempt to exclude a non-existing column"

    # TODO: Hardcoded, not completely rename-friendly
    # 2 fields in object_fields
    fieldlist.append({"id": "f" "orig_id", "text": "object." "orig_id"})
    fieldlist.append({"id": "f" "object_link", "text": "object." "object_link"})
    # 1 field in sample
    fieldlist.append(
        {"id": "s" "dataportal_descriptor", "text": "sample." "dataportal_descriptor"}
    )
    # 1 field in acquisition
    fieldlist.append(
        {"id": "a" "instrument", "text": "acquis." "instrument" " (fixed)"}
    )

    map_list = (
        ("f", prj_model.obj_free_cols),
        ("s", prj_model.sample_free_cols),
        ("a", prj_model.acquisition_free_cols),
        ("p", prj_model.process_free_cols),
    )
    map_prefix = {"f": "object.", "s": "sample.", "a": "acquis.", "p": "process."}
    mapv: Dict[str, str]
    for mapk, mapv in map_list:
        for k in sorted(mapv.keys()):
            fieldlist.append({"id": mapk + mapv[k], "text": map_prefix[mapk] + k})
    return fieldlist


@app.route("/gui/prj/editdatamass/<int:projid>", methods=["GET", "POST"])
@login_required
def gui_prj_edit_datamass(projid):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exists", "warning")
            elif ae.status in (401, 403):
                flash("You cannot do mass data edition on this project", "error")

            error = ae.status

    objectids = None
    error = None
    filters = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filters[k] = gvg(k, "")

    # Get the field name from user input
    field = gvp("field")
    if field and gvp("newvalue"):
        from to_back.ecotaxa_cli_py.api import SamplesApi, ProcessesApi, AcquisitionsApi
        from to_back.ecotaxa_cli_py.models import BulkUpdateReq

        # First field lettre gives the entity to update
        tablecode = field[0]
        # What's left is field name
        field = field[1:]
        new_value = gvp("newvalue")
        # Query the filtered list in project, if no filter then it's the whole project
        with ApiClient(ObjectsApi, request) as api:
            res = api.get_object_set(projid, filters)
        # Call the back-end service, depending on the field to update
        updates = [{"ucol": field, "uval": new_value}]
        if tablecode in ("h", "f"):
            # Object update
            if field == "classif_id":
                updates.append({"ucol": "classif_when", "uval": "current_timestamp"})
                updates.append({"ucol": "classif_who", "uval": str(current_user.id)})
            try:
                with ApiClient(ObjectsApi, request) as api:
                    nb_rows = api.update_object_set(
                        BulkUpdateReq(target_ids=res.object_ids, updates=updates)
                    )
            except ApiException as ae:
                flash(ae.reason, "error")
                error = ae.status
        elif tablecode == "p":
            # Process update, same key as acquisitions
            tgt_processes = [
                a_parent for a_parent in set(res.acquisition_ids) if a_parent
            ]
            try:
                with ApiClient(ProcessesApi, request) as api:
                    nb_rows = api.update_processes(
                        BulkUpdateReq(target_ids=tgt_processes, updates=updates)
                    )
            except ApiException as ae:
                flash(ae.reason, "error")
                error = ae.status
        elif tablecode == "a":
            # Acquisition update
            tgt_acquisitions = [
                a_parent for a_parent in set(res.acquisition_ids) if a_parent
            ]
            try:
                with ApiClient(AcquisitionsApi, request) as api:
                    nb_rows = api.update_acquisitions(
                        BulkUpdateReq(target_ids=tgt_acquisitions, updates=updates)
                    )
            except ApiException as ae:
                flash(ae.reason, "error")
                error = ae.status
        elif tablecode == "s":
            # Sample update
            tgt_samples = [a_parent for a_parent in set(res.sample_ids) if a_parent]
            try:
                with ApiClient(SamplesApi, request) as api:
                    nb_rows = api.update_samples(
                        BulkUpdateReq(target_ids=tgt_samples, updates=updates)
                    )
            except ApiException as ae:
                flash(ae.reason, "error")
                error = ae.status
        if error == None:
            flash("%s data rows updated" % nb_rows, "success")

    if field == "latitude" or field == "longitude" or gvp("recompute") == "Y":
        try:
            with ApiClient(ProjectsApi, request) as api:
                api.project_recompute_geography(projid)
                flash("All samples latitude and longitude updated", "success")
        except ApiException as ae:
            flash(ae.reason, "error")
            error = ae.status
    if gvp("recompute2") == "Y":
        try:
            with ApiClient(ProjectsApi, request) as api:
                nb_upd = api.project_recompute_sunpos(projid)
                flash("%d sun position changed in the project" % nb_upd, "success")
        except ApiException as ae:
            flash(ae.reason, "error")
            error = ae.status

    if len(filters):
        # Query the filtered list in project
        with ApiClient(ObjectsApi, request) as api:
            objectids: List[int] = api.get_object_set(projid, filters).object_ids
        # Warn the user

    fieldlist = _get_field_list(target_proj)

    return render_template(
        "v2/project/editdatamass.html",
        target_proj=target_proj,
        lst=fieldlist,
        warning=len(filters),
        objectids=objectids,
        error=error,
    )


######################################################################################################################
@app.route("/gui/prj/taxofix/<int:projid>", methods=["GET", "POST"])
def gui_deprecation_management(projid):
    from to_back.ecotaxa_cli_py.api import ObjectsApi, TaxonomyTreeApi
    from to_back.ecotaxa_cli_py.models import TaxonModel, ProjectTaxoStatsModel

    # Security & sanity checks
    error = None
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(projid)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exists", "warning")

            elif ae.status in (401, 403):
                flash("You cannot do category fix on this project", "error")
            error = ae.status

    if request.method == "POST":
        # Posted form
        posted = request.form
        # Loop over source categories
        reclassifs = []
        for a_key, a_val in posted.items():
            if a_key.startswith("chc"):
                reclassifs.append((int(a_key[3:]), int(a_val)))
        # Build a reclassify query for each valid (src, tgt) pair
        # Call each reclassif
        nb_objs = 0
        for a_todo in reclassifs:
            src_id, tgt_id = a_todo
            with ApiClient(ObjectsApi, request) as api:
                filters = {"taxo": str(src_id)}
                nb_ok = api.reclassify_object_set(
                    project_id=prj_id,
                    forced_id=tgt_id,
                    project_filters=filters,
                    reason="W",
                )
            nb_objs += nb_ok
        # Tell user
        flash("%d objects fixed." % nb_objs)

    if True:

        # Get the list of taxa used in this project
        with ApiClient(ProjectsApi, request) as api:
            stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(
                ids=str(target_proj.projid), taxa_ids="all"
            )
            populated_taxa = {
                stat.used_taxa[0]: stat for stat in stats if stat.used_taxa[0] != -1
            }  # filter unclassified

        # Get full info on the deprecated ones
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join([str(x) for x in populated_taxa.keys()])
            used_taxa: List[TaxonModel] = api.query_taxa_set(ids=taxa_ids)
        renames = [taxon for taxon in used_taxa if taxon.renm_id is not None]
        renames.sort(key=lambda r: r.name)

        # Also get information about advised renaming targets
        advised_ids = [
            str(taxon.renm_id) for taxon in used_taxa if taxon.renm_id is not None
        ]
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join(advised_ids)
            advised_taxa: List[TaxonModel] = api.query_taxa_set(ids=taxa_ids)
        advised_targets = {taxon.id: taxon for taxon in advised_taxa}

        # From logs, determine what was done before by users
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join([str(x.id) for x in renames])
            community_taxa: List[TaxonModel] = api.reclassif_stats(taxa_ids=taxa_ids)
            assert len(renames) == len(community_taxa)
        community_targets = {}
        for a_src, a_tgt in zip(renames, community_taxa):
            if a_src.id != a_tgt.id:
                # Community (non-advised) choice
                community_targets[a_src.id] = a_tgt

        return render_template(
            "/v2/project/taxo_fix.html",
            target_proj=target_proj,
            renames=renames,
            advised_targets=advised_targets,
            community_targets=community_targets,
        )
