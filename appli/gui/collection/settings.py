from typing import Optional, Dict, Union, List, Iterable
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user
from appli import gvp, gvpm
from appli.gui.staticlistes import py_messages

######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import CollectionsApi, ProjectsApi, UsersApi, GuestsApi
from to_back.ecotaxa_cli_py.models import (
    CollectionModel,
    MinUserModel,
    GuestModel,
    CreateCollectionReq,
    CollectionAggregatedRsp,
    ProjectUserStatsModel,
)

from appli.gui.commontools import (
    possible_licenses,
    possible_models,
    possible_access,
    py_get_messages,
    is_partial_request,
    new_ui_error,
)


###############################################common for create && edit  #######################################################################
orgprefix = "org_"
doi_url = "https://doi.org/"


def _user_format(uid: int) -> Union[MinUserModel, GuestModel]:
    try:
        with ApiClient(UsersApi, request) as api:
            user: MinUserModel = api.get_user(uid)
        return user
    except ApiException:
        with ApiClient(GuestsApi, request) as api:
            guest: GuestModel = api.get_guest(uid)
        return guest


def _set_persons(persons: list) -> Dict[str, list]:
    plist = {"users": [], "organisations": []}
    for person in persons:
        if person[0 : len(orgprefix)] == orgprefix:
            plist["organisations"].append(int(person[len(orgprefix) :]))
        else:
            plist["users"].append(_user_format(int(person)))
    return plist


def _prj_format(projid: int) -> dict:
    from appli.gui.project.projectsettings import get_target_prj

    prj = get_target_prj(projid)
    if prj is not None:
        return dict({"id": prj.projid, "title": prj.title})
    else:
        return dict({"id": None, "title": None})


def _is_published(target_coll: CollectionModel) -> bool:
    return (
        target_coll.external_id is not None
        and target_coll.external_id.strip() not in ["", "?"]
    )


def get_collection(collection_id) -> Optional[CollectionModel]:
    with ApiClient(CollectionsApi, request) as api:
        try:
            collection: CollectionModel = api.get_collection(collection_id)
            return collection
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            elif ae.status == 404:
                flash(py_messages["collection404"], "error")
            return None


def collection_about(collection_id, partial: bool = True) -> Optional[CollectionModel]:
    collection = get_collection(collection_id)
    return render_template(
        "v2/collection/about.html", target_coll=collection, partial=partial
    )


def collection_create() -> str:
    # who has the right to create a collection
    if not True:
        from werkzeug.exceptions import Forbidden
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    to_save = gvp("save")
    title = ""
    project_ids = []
    target_coll = None
    if to_save == "Y":
        title = gvp("title")
        project_ids = [int(p) for p in gvpm("project_ids[]")]

    if title.strip() != "" and len(project_ids) > 0:

        try:
            with ApiClient(CollectionsApi, request) as api:
                req = CreateCollectionReq(title=title, project_ids=project_ids)
                rsp: Union[str, int] = api.create_collection(req)
            return collection_edit(rsp, new=True)
        except ApiException as ae:
            if ae.status in (401, 403):
                flash(py_messages["notauthorized"], "error")
            else:
                new_ui_error(ae)
        external_id = gvp("external_id", "?")
        target_coll = CollectionModel(
            0, external_id, "", title, "", "", "", "", "", project_ids
        )
        setattr(target_coll, "project_ids", project_ids)
        for key in [
            "short_title",
            "citation",
            "license",
            "description",
            "abstract",
            "provider_user",
            "contact_user",
        ]:
            setattr(target_coll, key, gvp(key, ""))
        persons = {}
        # for prefix in ["creator", "associate"]:
        #    persons[prefix] = {"users": [], "organisations": []}
        #    for person in gvpm(prefix + "_persons[]"):
        #        if person[0 : len(orgprefix)] == orgprefix:
        #            persons[prefix]["organisations"].append(
        #                {"id": int(person[len(orgprefix)])}
        #            )
        #        else:
        #            persons[prefix]["users"].append({"id": int(person)})
        #        for _typ in ["users", "organisations"]:
        #            setattr(target_coll, prefix + "_" + _typ, persons[prefix][_typ])
    projectlist = [_prj_format(int(p)) for p in project_ids]
    licenses = possible_licenses()
    access = possible_access()
    aggregated = dict({"possible_access": access})
    return render_template(
        "v2/collection/settings.html",
        target_coll=target_coll,
        new=True,
        possible_licenses=licenses,
        orgprefix=orgprefix,
        doi_url=doi_url,
        projectlist=projectlist,
        agg=aggregated,
    )


def collection_aggregated(project_ids: str, simulate: str = "") -> dict:
    # who has the right to create a collection
    if not True:
        from werkzeug.exceptions import Forbidden
        from appli.gui.staticlistes import py_user

        raise Forbidden(py_user["notauthorized"])
    if len(project_ids) == 0:
        return {}
    if simulate == "y":
        with ApiClient(ProjectsApi, request) as api:
            try:
                prjstats: List[ProjectUserStatsModel] = api.project_set_get_user_stats(
                    ids=project_ids
                )
                annotators = []
                for prjst in prjstats:
                    annotators = list(set(annotators + prjst.annotators))
                if isinstance(annotators, Iterable) and len(annotators) > 0:

                    return {
                        "creator_users": [
                            {
                                "id": r.id,
                                "name": r.name,
                                "email": "",
                                "organisation": "",
                                # "email": r.email,
                                # "organisation": r.organisation,
                            }
                            for r in annotators
                        ]
                    }

            except ApiException as ae:
                flash("error in getting user stats " + str(ae.status), "error")

    with ApiClient(CollectionsApi, request) as api:
        aggregated: CollectionAggregatedRsp = (
            api.collection_aggregated_projects_properties(project_ids)
        )
    ret = aggregated.to_dict()
    privileges = {}
    for attrname in [
        "creator_users",
        "creator_organisations",
        "associate_users",
        "associate_organisations",
    ]:
        if attrname in ret:
            ret[attrname] = [u.to_dict() for u in ret[attrname]]

    if "privileges" in ret:
        for key, privs in ret["privileges"].items():
            privlist = []
            for u in privs:
                privlist.append(u.to_dict())
            privileges[key] = privlist
        ret["privileges"] = privileges
    # other props
    if not aggregated or not hasattr(aggregated, "initclassiflist"):
        ret["initclassiflist"] = []
    else:
        from appli.gui.taxonomy.tools import taxo_with_names

        ret["initclassiflist"] = ret["initclassiflist"].split(",")
        lst = [str(tid) for tid in aggregated.initclassiflist]
        ret["predeftaxo"] = taxo_with_names(lst)
    if not aggregated or not hasattr(aggregated, "classiffieldlist"):
        ret["classiffieldlist"] = ""
    ret["scn"] = possible_models()
    ret["possible_access"] = possible_access()
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
        varlist = dir(collection)
        for prefix in ["creator_", "associate_"]:
            varlist.remove(prefix + "users")
            varlist.remove(prefix + "organisations")
        varlist.extend(["creator_persons", "associate_persons"])
        for a_var in request.form:
            if a_var in varlist:
                if a_var in ["provider_user", "contact_user"]:
                    u = gvp(a_var, "")
                    if u != "":
                        setattr(collection, a_var, _user_format(int(u)))
                elif a_var == "short_title":
                    short_title = gvp(a_var, "")
                    if short_title.strip() != "":
                        old_short_title = gvp("old_short_title")
                        # TODO - check why "None" is set for short_title
                        if old_short_title.strip() == "" and short_title != "None":
                            setattr(collection, "short_title", short_title)
                elif a_var != "id":
                    setattr(collection, a_var, gvp(a_var, ""))
            elif a_var[len(a_var) - 2 :] == "[]" and a_var[0:-2] in varlist:
                if a_var[0:-2] in ["creator_persons", "associate_persons"]:
                    plist = _set_persons(gvpm(a_var))

                    for attrname in ["users", "organisations"]:
                        setattr(
                            collection,
                            a_var[0:-2].replace("persons", attrname),
                            plist[attrname],
                        )
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
            new_ui_error(ae)

    licenses = possible_licenses()
    # licenses[0] licenses texts , licenses[1] licenses restriction
    from appli.gui.commontools import crsf_token

    projectlist = [_prj_format(int(p)) for p in collection.project_ids]
    published = _is_published(collection)
    aggregated = {}
    return render_template(
        "v2/collection/settings.html",
        target_coll=collection,
        projectlist=projectlist,
        crsf_token=crsf_token(),
        possible_licenses=licenses,
        new=False,
        orgprefix=orgprefix,
        published=published,
        agg=aggregated,
        doi_url=doi_url,
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
    published = _is_published(target_coll)
    return render_template(
        "./v2/collection/erase.html",
        isadmin=isadmin,
        partial=is_partial_request(),
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
