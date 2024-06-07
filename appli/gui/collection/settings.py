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
from to_back.ecotaxa_cli_py.api import (
    CollectionsApi,
    UsersApi,
    TaxonomyTreeApi,
    MiscApi,
)
from to_back.ecotaxa_cli_py.models import (
    CollectionModel,
    MinUserModel,
    TaxonModel,
)
from appli.gui.commontools import possible_licenses

###############################################common for create && edit  #######################################################################
def _user_format(uid: int) -> dict:
    with ApiClient(UsersApi, request) as api:
        user: MinUserModel = api.get_user(uid)
    return user


def _prj_format(projid: int) -> dict:
    from appli.gui.project.projectsettings import get_target_prj

    prj = get_target_prj(projid)
    if prj != None:
        return dict({"id": prj.projid, "title": prj.title})
    else:
        return dict({"id": p, "title": None})


def get_collection(collection_id) -> CollectionModel:
    with ApiClient(CollectionsApi, request) as api:
        try:
            collection: CollectionModel = api.get_collection(collection_id)
            return collection
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["project404"], "error")
            return None


def collection_create() -> str:
    # who has the right to create a collection
    if not True:
        from werkzeug.exceptions import Forbidden
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    to_save = gvp("save")
    if to_save == "Y":
        title = gvp("title")
        project_ids = [int(p) for p in gvpm("project_ids[]")]
        print("--------------------project_ids", project_ids)
        if title == "" or len(project_ids) == 0:
            flash("title and project id are required", "error")
            to_save = False
    if to_save:
        from to_back.ecotaxa_cli_py.models import CreateCollectionReq

        with ApiClient(CollectionsApi, request) as api:
            req = CreateCollectionReq(title=title, project_ids=project_ids)
            rsp: int = api.create_collection(req)

        return collection_edit(rsp, new=True)
    licenses = possible_licenses()
    return render_template(
        "v2/collection/settings.html",
        target_coll=None,
        members=None,
        new=True,
        possible_licenses=licenses,
    )


def collection_edit(collection_id: int, new: bool = False) -> str:
    # Security & sanity checks
    # get target_proj

    from appli.gui.staticlistes import py_messages

    collection = get_collection(collection_id)
    # from appli.gui.collection.collist import collection

    if collection is None:
        flash(py_messages["selectothercollection"], "info")
        return redirect(url_for("gui_collection_noright", collection_id=collection_id))
    # Reconstitute members list with privs
    # data structure used in both display & submit
    redir = ""
    if gvp("save") == "Y":
        # Load posted variables
        for a_var in request.form:
            if a_var in dir(collection):
                if a_var in ["provider_user", "contact_user"]:
                    u = gvp(a_var, "")
                    if u != "":
                        setattr(collection, a_var, _user_format(int(u)))
                else:
                    setattr(collection, a_var, gvp(a_var))
            elif a_var[len(a_var) - 2 :] == "[]" and a_var[0:-2] in dir(collection):
                if a_var[0:-2] in ["creator_users", "associate_users"]:
                    ulist = [_user_format(int(u)) for u in gvpm(a_var)]
                    setattr(collection, a_var[0:-2], ulist)
                elif a_var[0:-2] in ["project_ids"]:

                    setattr(collection, a_var[0:-2], [int(p) for p in gvpm(a_var)])
                else:
                    setattr(collection, a_var[0:-2], gvpm(a_var))
        do_update = True
        if do_update:
            try:
                with ApiClient(CollectionsApi, request) as api:
                    api.update_collection(
                        collection_id=collection.id, collection_model=collection
                    )
                    if new == True:
                        message = py_messages["collectioncreated"]
                    else:
                        message = py_messages["collectionupdated"]
                    flash(
                        message + " " + collection.title,
                        "success",
                    )
                return redirect(request.referrer)
            except ApiException as ae:
                flash(py_messages["updateexception"] + "%s" % ae.reason)

    licenses = possible_licenses()

    from appli.gui.commontools import crsf_token

    projectlist = [_prj_format(int(p)) for p in collection.project_ids]

    return render_template(
        "v2/collection/settings.html",
        target_coll=collection,
        projectlist=projectlist,
        crsf_token=crsf_token(),
        possible_licenses=licenses,
        new=new,
        # redir=redir,
    )


######################################################################################################################
