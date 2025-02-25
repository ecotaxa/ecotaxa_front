from typing import Optional
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user
from appli import gvp, gvpm
from appli.gui.staticlistes import py_messages

######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import CollectionsApi, UsersApi
from to_back.ecotaxa_cli_py.models import (
    CollectionModel,
    MinUserModel,
    CreateCollectionReq,
    CollectionAggregatedRsp,
)

from appli.gui.commontools import (
    possible_licenses,
    possible_models,
    possible_access,
    py_get_messages,
    is_partial_request,
)


###############################################common for create && edit  #######################################################################
def _user_format(uid: int) -> MinUserModel:
    with ApiClient(UsersApi, request) as api:
        user: MinUserModel = api.get_user(uid)
    return user


def _prj_format(projid: int) -> dict:
    from appli.gui.project.projectsettings import get_target_prj

    prj = get_target_prj(projid)
    if prj is not None:
        return dict({"id": prj.projid, "title": prj.title})
    else:
        return dict({"id": None, "title": None})


def get_collection(collection_id) -> Optional[CollectionModel]:
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
    title = ""
    project_ids = []
    if to_save == "Y":
        title = gvp("title")
        project_ids = [int(p) for p in gvpm("project_ids[]")]

        if title == "" or len(project_ids) == 0:
            flash("title and project id are required", "error")
            to_save = False
    if to_save:

        try:
            with ApiClient(CollectionsApi, request) as api:
                req = CreateCollectionReq(title=title, project_ids=project_ids)
                rsp: int = api.create_collection(req)
            return collection_edit(rsp, new=True)
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["project404"], "error")
            else:
                flash(py_messages["project404"], "error")
    licenses = possible_licenses()
    access = possible_access()
    return render_template(
        "v2/collection/settings.html",
        target_coll=None,
        new=True,
        possible_licenses=licenses,
        possible_access=access,
    )


def collection_aggregated(project_ids: str) -> dict:
    # who has the right to create a collection
    if not True:
        from werkzeug.exceptions import Forbidden
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    if len(project_ids):
        with ApiClient(CollectionsApi, request) as api:
            aggregated: CollectionAggregatedRsp = (
                api.collection_aggregated_projects_properties(project_ids)
            )
    privileges = {}
    ret = aggregated.to_dict()
    if "creator_users" in ret:
        creator_users = []
        for u in ret["creator_users"]:
            creator_users.append(u.to_dict())
        ret["creator_users"] = creator_users
    if "privileges" in ret:
        for key, privs in ret["privileges"].items():
            privlist = []
            for u in privs:
                privlist.append(u.to_dict())
            privileges[key] = privlist
        ret["privileges"] = privileges
    return ret


def collection_edit(collection_id: int, new: bool = False):
    # Security & sanity checks
    # get target_proj

    from appli.gui.collection.staticlistes import py_messages

    collection = get_collection(collection_id)
    # from appli.gui.collection.collist import collection

    if collection is None:
        flash(py_messages["selectothercollection"], "info")
        return redirect(url_for("gui_collection_noright", collection_id=collection_id))
    # Reconstitute members list with privs
    # data structure used in both display & submit
    if gvp("save") == "Y":
        # Load posted variables
        for a_var in request.form:
            if a_var in dir(collection):
                if a_var in ["provider_user", "contact_user"]:
                    u = gvp(a_var, "")
                    if u != "":
                        setattr(collection, a_var, _user_format(int(u)))
                elif a_var == "short_title":
                    short_title = gvp(a_var)
                    if short_title.strip() != "":
                        old_short_title = gvp("old_short_title")
                        if old_short_title.strip() == "":
                            setattr(collection, "short_title", short_title)
                elif a_var != "id":
                    setattr(collection, a_var, gvp(a_var))
            elif a_var[len(a_var) - 2 :] == "[]" and a_var[0:-2] in dir(collection):
                if a_var[0:-2] in ["creator_users", "associate_users"]:
                    ulist = [_user_format(int(u)) for u in gvpm(a_var)]
                    setattr(collection, a_var[0:-2], ulist)
                elif a_var[0:-2] in ["project_ids"]:

                    setattr(collection, a_var[0:-2], [int(p) for p in gvpm(a_var)])
                else:
                    setattr(collection, a_var[0:-2], gvpm(a_var))
        try:
            with ApiClient(CollectionsApi, request) as api:
                api.patch_collection(
                    collection_id=collection_id, collection_req=collection
                )
                if new:
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
    # licenses[0] licenses texts , licenses[1] licenses restriction
    from appli.gui.commontools import crsf_token

    projectlist = [_prj_format(int(p)) for p in collection.project_ids]
    prjlist = [str(p) for p in collection.project_ids]
    aggregated = collection_aggregated(",".join(prjlist))
    if "initclassiflist" in aggregated:
        initclassiflist = aggregated["initclassiflist"].split(",")
    else:
        initclassiflist = []
    lst = [str(tid) for tid in initclassiflist]
    if "classiffieldlist" in aggregated:
        classiffieldlist = aggregated["classiffieldlist"]
    else:
        classiffieldlist = ""

    if "privileges" in aggregated:
        privileges = aggregated["privileges"]

    else:
        privileges = None
    if "freecols" in aggregated:
        freecols = aggregated["freecols"]
    else:
        freecols = None
    # common func used in project stats
    from appli.gui.taxonomy.tools import taxo_with_names

    predeftaxo = taxo_with_names(lst)

    scn = possible_models()
    access = possible_access()
    return render_template(
        "v2/collection/settings.html",
        target_coll=collection,
        projectlist=projectlist,
        classiffieldlist=classiffieldlist,
        predeftaxo=predeftaxo,
        status=aggregated["status"],
        access=aggregated["access"],
        excluded=aggregated["excluded"],
        members_by_right=privileges,
        freecols=freecols,
        crsf_token=crsf_token(),
        possible_licenses=licenses,
        possible_access=access,
        scn_network_id=scn,
        new=new,
        # redir=redir,
    )


######################################################################################################################
#     properties evaluation from  projects list                                                                   #
######################################################################################################################    backto = False
def collection_erase(collection_id: int, erase: bool = False):
    messages = py_get_messages("collection")
    isadmin = current_user.is_app_admin
    target_coll = get_collection(collection_id)
    if target_coll is None:
        return redirect(url_for("gui_collection_noright", collection_id=collection_id))
    print("will erase " + target_coll.title, erase)
    if erase:
        with ApiClient(CollectionsApi, request) as api:
            try:
                _ = api.erase_collection(collection_id)
            except ApiException as ae:
                if ae.status in (401, 403):
                    message = messages["collectionnotyours"]
                elif ae.status == 409:
                    message = messages["collectionpublished"]
                else:
                    message = messages["collectioneraseerror"] + " - " + str(ae.status)
                flash(message, "error")
                return redirect(
                    url_for("gui_collection_noright", collection_id=collection_id)
                )
    published = target_coll.external_id != "?" or target_coll.short_title is not None
    return render_template(
        "./v2/collection/erase.html",
        isadmin=isadmin,
        partial=is_partial_request(request),
        target_coll=target_coll,
        published=published,
        erase=erase,
    )


######################################################################################################################
#     properties evaluation from  projects list                                                                   #
######################################################################################################################
# def collection_status(project_ids: List[int]) -> str:
#    return status

# def collection_license(project_ids: List[int]) -> str:
#    return license

# def collection_creators(project_ids: List[int]) -> str:
#    return creators

# def collection_creators_organisations(project_ids: List[int]) -> str:
#    return creators_organisations

# def collection_associates(project_ids: List[int]) -> str:
#    return associates

# def collection_associates_organisations(project_ids: List[int]) -> str:
#    return associates_organisations
