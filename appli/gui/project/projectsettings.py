import collections
import os
from pathlib import Path
from typing import List

from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_required
from appli import app, gvp, gvpm
from appli.gui.staticlistes import py_messages

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


def get_target_prj(prjid, for_managing: bool = False) -> ProjectModel:
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(
                prjid, for_managing=for_managing
            )
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["project404"], "error")
            return None
    return target_proj


def _possible_models():
    with ApiClient(MiscApi, request) as api:
        possibles = api.query_ml_models()

    scn = {a_model.name: {"name": a_model.name} for a_model in possibles}
    return scn


def _possible_licenses():
    # TODO: Cache of course, it's constants!
    with ApiClient(MiscApi, request) as api:
        possibles = api.used_constants().license_texts
    return possibles


def _prj_users_list(ids: list) -> dict:
    users_list = {}
    with ApiClient(UsersApi, request) as api:
        all_users: List[MinUserModel] = api.search_user(by_name="%%")
        for a_user in sorted(all_users, key=lambda u: u.name.strip().lower()):
            if (str(a_user.id)) in ids:
                users_list[str(a_user.id)] = a_user
    return users_list


def _proj_privileges(prjid):
    return []


def _cannot_do_message(autho, prjid=0):
    message = "notautho"

    if autho == 1:
        if prjid == 0:
            message = "noauthoprjcreate"
        else:
            message = "noauthoprjedit"
    elif autho == 2:
        message = "noautho2"  # ???
    elif autho == 3:
        message = "noautho3"  # ???
    return message


def _user_cando(autho):
    user: UserModelWithRights = current_user.api_user
    if not user or not current_user.is_active or autho not in user.can_do:
        flash(_cannot_do_message(autho), "error")
        return False
    else:
        return True


def prj_create() -> str:
    if not _user_cando(1):
        from werkzeug.exceptions import Forbidden
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    to_save = gvp("save")
    if to_save == "Y":
        title = gvp("title")
        instrument = gvp("instrument")
        if title == "" or instrument == "":
            flash("titleinstrumentrequired", "error")
            to_save = False
    if to_save:
        from to_back.ecotaxa_cli_py.models import CreateProjectReq

        with ApiClient(ProjectsApi, request) as api:
            req = CreateProjectReq(title=title, instrument=instrument)
            rsp: int = api.create_project(req)
        return prj_edit(rsp, new=True)
    scn = _possible_models()
    possible_licenses = _possible_licenses()
    return render_template(
        "v2/project/projectsettings.html",
        target_proj=None,
        members=None,
        new=True,
        scn=scn,
        possible_licenses=possible_licenses,
    )


def prj_edit(prjid: int, new: bool = False) -> str:
    # Security & sanity checks
    # get target_proj

    from appli.gui.staticlistes import py_messages

    target_proj = get_target_prj(prjid, for_managing=True)
    if target_proj is None:
        flash(py_messages["selectotherproject"], "info")
        return redirect(url_for("gui_prj_noright", projid=prjid))
    # Reconstitute members list with privs
    # data structure used in both display & submit
    redir = ""
    if gvp("save") == "Y":
        # Load posted variables
        previous_cnn = target_proj.cnn_network_id
        posted_contact_id = None
        # Update the project (from API call) with posted variables

        # same names as in target_proj
        for a_var in request.form:
            if a_var in dir(target_proj):
                setattr(target_proj, a_var, gvp(a_var))

        # other
        posted_classif_list = gvpm("inittaxo[]")
        # The original list is displayed using str(list), so there is a bit of formatting inside
        posted_classif_list = ",".join(posted_classif_list).replace(" ", "")
        target_proj.init_classif_list = [
            int(cl_id) for cl_id in posted_classif_list.split(",") if cl_id.isdigit()
        ]

        posted_contact_id = gvp("contact_user_id")
        target_proj.visible = gvp("visible") == "Y"
        if previous_cnn != target_proj.cnn_network_id:
            flash("scnerased", "success")
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
            ids = data["member"]

            users_list = _prj_users_list(ids=ids)
        else:
            users_list = {}
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
                                # check duplicates with diff rights - must be impossible with the new front js (does not send duplicates or elements to delete )
                                err_msg.append(
                                    py_messages["memberexistdifferentpriv"]
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
                        py_messages["privnotsetfor"] + users_list[member].name
                    )

            else:
                # member is not in users list
                err_msg.append(py_messages["membernomoreinlist"] + member)
                do_update = False
        for msg in err_msg:
            flash(msg, "error")
        if contact_user == None:
            flash(
                "getcontactuserinmanagers",
                "error",
            )
            do_update = False
        else:
            # OK we have someone
            target_proj.contact = contact_user
        # Managers sanity check
        if len(target_proj.managers) == 0:
            flash("managerrequired", "error")
            do_update = False

        # Update on back-end

        if do_update:
            try:
                with ApiClient(ProjectsApi, request) as api:
                    api.update_project(
                        project_id=target_proj.projid, project_model=target_proj
                    )
                    if new == True:
                        message = py_messages["projectcreated"]
                    else:
                        message = py_messages["projectupdated"]
                    flash(
                        message + " " + target_proj.title,
                        "success",
                    )
                    # if new == True:
                    # redirect to import after 3 s
                    # redir = "/Job/Create/FileImport?p=" + str(target_proj.projid)
                    # redir = "/prj/" + str(target_proj.projid) + "?next=import"
                    # else:
                    # redirect to classif
                    # redir = "/prj/" + str(target_proj.projid) + "?next=classif"
                    # return redirect(redir)
                    return redirect(request.referrer)
            except ApiException as ae:
                flash(py_messages["updateexception"] + "%s" % ae.reason)
    lst = [str(tid) for tid in target_proj.init_classif_list]
    # common func used in project stats
    from appli.gui.taxonomy.tools import taxo_with_names

    predeftaxo = taxo_with_names(lst)

    scn = _possible_models()

    # TODO: Cache of course, it's constants!
    possible_licenses = _possible_licenses()
    members_by_right = {
        "Manage": target_proj.managers.copy(),
        "Annotate": target_proj.annotators.copy(),
        "View": target_proj.viewers.copy(),
    }
    from appli.gui.commontools import crsf_token

    return render_template(
        "v2/project/projectsettings.html",
        target_proj=target_proj,
        members_by_right=members_by_right,
        scn=scn,
        crsf_token=crsf_token(),
        predeftaxo=predeftaxo,
        possible_licenses=possible_licenses,
        new=new,
        # redir=redir,
    )


######################################################################################################################
