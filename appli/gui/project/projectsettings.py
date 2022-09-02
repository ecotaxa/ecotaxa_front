import collections
import os
import gettext
from pathlib import Path
from typing import List

from flask import render_template, flash, request, redirect
from flask_security import login_required
from flask_login import current_user
from appli import app, PrintInCharte, gvp, gvpm, XSSEscape
from appli.constants import MappableObjectColumns, MappableParentColumns

######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, TaxonomyTreeApi, MiscApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    MinUserModel,
    TaxonModel,
    ProjectTaxoStatsModel,
)

###############################################common for create && edit  #######################################################################


def get_target_prj(prjid) -> ProjectModel:

    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(prjid, for_managing=True)
            return target_proj

        except ApiException as ae:
            # description='<a href="/gui/prj/">Select another project</a>',
            if ae.status == 404:
                raise ApiException(
                    status=ae.status,
                    eason="Project doesn't exist",
                )

            elif ae.status in (401, 403):
                # description='<a href="/gui/prj/">Select another project</a>',
                raise ApiException(
                    status=ae.status,
                    reason="You cannot edit settings for this project",
                )
            else:
                raise ApiException(status=ae.status)


def _possible_models():
    try:
        with ApiClient(MiscApi, request) as api:
            possibles = api.query_ml_models()

        scn = {a_model.name: {"name": a_model.name} for a_model in possibles}
        return scn
    except ApiException as ae:
        if ae.status == 404:
            flash("No possible model", "error")
            # return PrintInCharte("<a href=/prj/>Select another project</a>")
        elif ae.status in (401, 403):
            flash("You cannot access this info", "error")
            # return PrintInCharte("<a href=/prj/>Select another project</a>")


def _possible_licenses():
    # TODO: Cache of course, it's constants!
    try:
        with ApiClient(MiscApi, request) as api:
            possibles = api.used_constants().license_texts
        return possibles
    except ApiException as ae:

        if ae.status == 404:
            raise ApiException(
                status=ae.status,
                reason="No possible model",
            )

        elif ae.status in (401, 403):
            raise ApiException(
                status=ae.status,
                reason="You cannot access this info",
            )

        else:
            raise ApiException(status=ae.status)


def _prj_users_list(ids):
    try:
        users_list = {}
        with ApiClient(UsersApi, request) as api:
            if ids == None:
                all_users: List[MinUserModel] = api.search_user(by_name="%%")
            else:
                all_users: List[MinUserModel] = api.get_users(ids=ids)
            for a_user in sorted(all_users, key=lambda u: u.name.strip().lower()):
                users_list[str(a_user.id)] = a_user
        return users_list
    except ApiException as ae:
        if ae.status == 404:
            raise ApiException(status=ae.status, reason="No users list")
            # return PrintInCharte("<a href=/prj/></a>")
        elif ae.status in (401, 403):
            raise ApiException(status=ae.status, reason="You cannot access this info")
        else:
            raise ApiException(status=ae.status)


def _proj_privileges(prjid):
    return []


def _cannot_do_message(autho, prjid=0):
    message = _("not autho")
    if autho == 1:
        if prjid == 0:
            message = _("Not_autho_prj_create")
        else:
            message = _("Not_autho_prj_edit")
    elif auto == 2:
        message = _("Not_autho_2")
    elif auto == 3:
        message = _("Not_autho_3")
    return message


def _user_cando(autho):
    user: UserModelWithRights = current_user.api_user
    if not user or not user.active or autho not in user.can_do:
        flash(_cannot_do_message(autho), "error")
        return False
    else:
        return True


######################################################################################################################

# @app.route("/gui/prj/create", methods=["GET", "POST"])
# @login_required
def prj_create() -> str:
    if not _user_cando(1):
        return render_template("v2/error.html", title="403")

    if gvp("save") == "Y":
        try:
            from to_back.ecotaxa_cli_py.models import CreateProjectReq

            with ApiClient(ProjectsApi, request) as api:
                title = gvp("title")
                instrument = gvp("instrument")
                req = CreateProjectReq(title=title, instrument=instrument)
                rsp: int = api.create_project(req)
                return prj_edit(rsp, new=True)

        except ApiException as ae:
            raise ApiException(status=ae.status, reason="Error in project creation")
    scn = _possible_models()
    possible_licenses = _possible_licenses()
    return render_template(
        "v2/project/projectsettings.html",
        target_proj=None,
        members=None,
        scn=scn,
        possible_licenses=possible_licenses,
    )


# @app.route("/gui/prj/edit/<int:prjid>", methods=["GET", "POST"])
# @login_required
def prj_edit(prjid: int, new: bool = False) -> str:
    # Security & sanity checks
    # get target_proj
    target_proj = get_target_prj(prjid)
    if not target_proj:
        return
    # Reconstitute members list with privs
    # data structure used in both display & submit

    if gvp("save") == "Y":
        # Load posted variables
        previous_cnn = target_proj.cnn_network_id
        posted_contact_id = None

        for a_var in request.form:
            print(a_var)
            # Update the project (from API call) with posted variables

            if a_var in dir(target_proj):
                # TODO: Big assumption here, variables need to have same name as Model fields
                setattr(target_proj, a_var, gvp(a_var))
            if a_var == "contact_user_id":
                posted_contact_id = gvp(a_var)
            elif a_var == "inittaxo[]":
                posted_classif_list = gvpm(a_var)
                posted_classif_list = ",".join(posted_classif_list)
                # The original list is displayed using str(list), so there is a bit of formatting inside
                posted_classif_list = posted_classif_list.replace(" ", "")
                if posted_classif_list and posted_classif_list[0] == "[":
                    posted_classif_list = posted_classif_list[1:]
                if posted_classif_list and posted_classif_list[-1] == "]":
                    posted_classif_list = posted_classif_list[:-1]
                target_proj.init_classif_list = [
                    int(cl_id)
                    for cl_id in posted_classif_list.split(",")
                    if cl_id.isdigit()
                ]
        target_proj.visible = gvp("visible") == "Y"
        if previous_cnn != target_proj.cnn_network_id:
            flash("SCN features erased", "success")
            do_update = True
        # process members privileges results - members_by_right is empty as backend records are deleted on every update
        do_update = True
        contact_user = None
        err_msg = []
        data = {"member": [], "privilege": []}
        members_by_right = {
            "Manage": target_proj.managers,
            "Annotate": target_proj.annotators,
            "View": target_proj.viewers,
        }

        # empty target_proj privileges field
        for priv in members_by_right.keys():
            for m in members_by_right[priv].copy():
                members_by_right[priv].remove(m)

        for key in data:
            values = gvpm("members[" + key + "]")
            data[key] = values

        # list all privileges in list_users key:'id'
        if len(data["member"]):
            ids = ",".join(data["member"])

            users_list = _prj_users_list(ids=ids)
        else:
            users_list = []
            do_update = False

        for i in range(len(data["member"])):
            member = data["member"][i]
            if member in users_list.keys():
                priv = data["privilege"][i]
                if priv in members_by_right.keys():
                    member_to_add = users_list[member]
                    for right, members_added in members_by_right.items():
                        if member_to_add in members_added:
                            if right != priv:
                                # check duplicates with diff rights - but impossible with the new front js (does not send duplicates or elements to delete )
                                err_msg.append(
                                    "Member already registered with differents privileges "
                                    + users_list[member].name
                                )
                                do_update = False
                            member_to_add = 0
                            break

                    if priv == "Manage" and member == posted_contact_id:
                        contact_user = users_list[member]
                    if member_to_add != 0:
                        members_by_right[priv].append(users_list[member])
                else:
                    # privilege empty
                    err_msg.append(
                        "Privileges are not set for member " + users_list[member].name
                    )

            else:
                # member is not in users list
                err_msg.append(
                    "Error member to be added is no more in users list "
                    + users_list[member].name
                )
                do_update = False
        for msg in err_msg:
            flash(msg)
        if contact_user == None:
            flash(
                "A contact person needs to be designated among the current project managers. "
                'Use the "Edit privileges only" button or scroll down to bottom of the page.',
                "error",
            )
            do_update = False
        else:
            # OK we have someone
            target_proj.contact = contact_user
        # Managers sanity check
        if len(target_proj.managers) == 0:
            flash("At least one manager is needed", "error")
            do_update = False

        # Update on back-end
        with ApiClient(ProjectsApi, request) as api:
            try:
                if do_update:
                    api.update_project(
                        project_id=target_proj.projid, project_model=target_proj
                    )
                flash(
                    "Project "
                    + target_proj.title
                    + " updated. redirect to import or classif ",
                    "success",
                )
                return redirect("/gui/prj")
            except ApiException as ae:
                raise ApiException(status=ae.status, reason="Update problem: %s" % ae)
    lst = [str(tid) for tid in target_proj.init_classif_list]
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(lst))
    predeftaxo = [(r.id, r.display_name) for r in res]
    predeftaxo.sort(key=lambda r: r[1].lower())
    # TODO: Get from metadata

    maplist = list(MappableParentColumns)
    maplist.extend(list(MappableObjectColumns))
    maplist.extend(target_proj.obj_free_cols.keys())

    scn = _possible_models()

    # TODO: Cache of course, it's constants!
    possible_licenses = _possible_licenses()
    members_by_right = {
        "Manage": target_proj.managers.copy(),
        "Annotate": target_proj.annotators.copy(),
        "View": target_proj.viewers.copy(),
    }
    # members_by_rights = members_by_right.copy()
    return render_template(
        "v2/project/projectsettings.html",
        target_proj=target_proj,
        members_by_right=members_by_right,
        scn=scn,
        maplist=maplist,
        predeftaxo=predeftaxo,
        possible_licenses=possible_licenses,
        new=new,
    )


######################################################################################################################
# noinspection PyUnusedLocal
def prj_import_taxo(prjid=0):
    # Query accessible projects
    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects(
            also_others=False, filter_subset=False
        )
    # And their statistics
    prj_ids = " ".join([str(a_prj.projid) for a_prj in prjs])
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats(ids=prj_ids)

    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())
    # Collect id for each taxon to show
    taxa_ids_for_all = set()
    stats_per_project = {}
    for a_prj in prjs:
        taxa_ids_for_all.update(a_prj.init_classif_list)
    for a_stat in stats:
        taxa_ids_for_all.update(a_stat.used_taxa)
        stats_per_project[a_stat.projid] = a_stat.used_taxa
    # Collect name for each existing id
    lst = [str(tid) for tid in taxa_ids_for_all if tid != -1]
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(lst))
    taxo_map = {taxon_rec.id: taxon_rec.display_name for taxon_rec in res}

    txt = ""
    prjs_pojo = []
    for a_prj in prjs:
        # exclude current prj
        if a_prj.projid != prjid:
            # Inject taxon lists for display
            prj_initclassif_list = set(a_prj.init_classif_list)
            try:
                objtaxon = set(stats_per_project[a_prj.projid])
            except KeyError:
                # No stats
                objtaxon = set()
            # 'Extra' are the taxa used, but not in the classification preset
            result = []
            objtaxon.difference_update(prj_initclassif_list)
            for t in prj_initclassif_list:
                resolved = taxo_map.get(t, None)
                if resolved:
                    result.append(resolved)
            a_prj = a_prj.to_dict()  # immutable -> to_dict()
            a_prj["presetids"] = ",".join([str(x) for x in prj_initclassif_list])
            a_prj["preset"] = ", ".join(sorted(result))

            result = []
            for t in objtaxon:
                resolved = taxo_map.get(int(t), None)
                if resolved:
                    result.append(resolved)
            a_prj["objtaxonnotinpreset"] = ", ".join(sorted(result))
            a_prj["objtaxonids"] = ",".join([str(x) for x in objtaxon])
            # show only projects with classif preset or extra
            if len(prj_initclassif_list) or len(objtaxon):
                prjs_pojo.append(a_prj)

    # render the table
    return render_template(
        "v2/project/_listimport.html",
        prjlist=prjs_pojo,
        typeimport="taxo",
        txt=txt,
    )
