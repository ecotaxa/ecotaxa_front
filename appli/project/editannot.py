from collections import OrderedDict
from typing import List, Dict

from flask import g, flash, request, render_template
from flask_login import login_required

from appli import app, PrintInCharte, gvg
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, UsersApi
from to_back.ecotaxa_cli_py.models import (
    ProjectModel,
    MinUserModel,
    ObjectSetRevertToHistoryRsp,
    HistoricalLastClassif,
)


######################################################################################################################
# noinspection PyPep8Naming,SpellCheckingInspection
@app.route("/prj/EditAnnot/<int:PrjId>", methods=["GET", "POST"])
@login_required
def PrjEditAnnot(PrjId):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exist"
            elif ae.status in (401, 403):
                flash("You cannot do mass annotation edition on this project", "error")
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(
        target_proj.projid, target_proj.title
    )

    header = "<h3>Project Edit / Erase annotation massively </h3>"

    # Store posted variables
    old_author_id = gvg(
        "OldAuthor"
    )  # Note: is an id or one of the special choices below
    new_author_id = gvg("NewAuthor")
    date_filter = gvg("filt_date")
    time_filter_hour = gvg("filt_hour")
    time_filter_minutes = gvg("filt_min")
    # ############### 1er Ecran
    if not (old_author_id and new_author_id):
        # Selection lists, special choices, in first
        LstUserOld = OrderedDict({"anyuser": "Any User"})
        LstUserNew = OrderedDict(
            {"lastannot": "Previous Annotation available, or prediction, or Nothing"}
        )
        # TODO: It would be nice to offer only relevant users as a choice
        with ApiClient(UsersApi, request) as api:
            all_users: List[MinUserModel] = api.search_user(by_name="%%")
        # No guaranteed order from API, so sort now, see #475 for the strip()
        all_users.sort(key=lambda user: user.name.strip())
        # Complete selection lists
        for usr in all_users:
            LstUserOld[usr.id] = usr.name
            LstUserNew[usr.id] = usr.name
        return PrintInCharte(
            render_template(
                "project/MassAnnotationEdition.html",
                header=header,
                old_authors=LstUserOld,
                new_authors=LstUserNew,
            )
        )

    # Use filtering on target
    filters: Dict[str, str] = {}

    # Define the to-be-modified set of objects
    if old_author_id == "anyuser":
        from_txt = "Replace any classification"
    else:
        with ApiClient(UsersApi, request) as api:
            # Let the eventual 404 propagate
            old_author: MinUserModel = api.get_user(user_id=int(old_author_id))
        # Only return objects classified by the requested user, and exclude him/her from history picking
        filters["filt_last_annot"] = old_author_id
        from_txt = (
            "Replace current classification, when done by <b>%s</b>" % old_author.name
        )
    if date_filter:
        filters["validfromdate"] = (
            date_filter
            + " "
            + (time_filter_hour if time_filter_hour else "00")
            + ":"
            + (time_filter_minutes if time_filter_minutes else "00")
        )
        # Ask for Predicted as well, for rollback of WoRMS migrations
        filters["statusfilter"] = "PVD"

    # Define how to modify them
    if new_author_id == "lastannot":
        target_for_api = None
        to_txt = "With previous classification "
        if old_author_id != "anyuser":
            to_txt += "of any other author, prediction if no other author, NOTHING as a fallback "
    else:
        with ApiClient(UsersApi, request) as api:
            # Let the eventual 404 propagate
            new_author: MinUserModel = api.get_user(user_id=int(new_author_id))
        target_for_api = new_author_id
        to_txt = (
            "With previous classification done by <b>%s</b>, except if already the case"
            % new_author.name
        )

    # ############### 2nd Ecran, affichage liste des categories & estimations
    if not gvg("Process"):
        # Query the filtered list in project, if no filter then it's the whole project
        with ApiClient(ObjectsApi, request) as api:
            # TODO: It's getting long these primitive names...
            call = api.revert_object_set_to_history
            res: ObjectSetRevertToHistoryRsp = call(
                project_id=PrjId,
                project_filters=filters,
                target=target_for_api,
                dry_run=True,
            )
        # Summarize/group changes
        data = _digest_changes(res)
        # Display categories choice
        return PrintInCharte(
            render_template(
                "project/MassAnnotationEdition.html",
                header=header,
                from_txt=from_txt,
                to_txt=to_txt,
                old_author=old_author_id,
                new_author=new_author_id,
                date_filter=date_filter,
                time_filter_hour=time_filter_hour,
                time_filter_minutes=time_filter_minutes,
                taxo_impact=data,
            )
        )

    # ############### 3eme Ecran Execution Requetes
    if gvg("Process") == "Y":
        selected_taxa = ",".join((x[4:] for x in request.form if x[0:4] == "taxo"))
        if selected_taxa == "":
            flash(
                "You must select at least one category to do the replacement", "error"
            )
            return PrintInCharte("<a href='#' onclick='history.back();'>Back</a>")
        filters["taxo"] = selected_taxa
        with ApiClient(ObjectsApi, request) as api:
            call = api.revert_object_set_to_history
            res2: ObjectSetRevertToHistoryRsp = call(
                project_id=PrjId,
                project_filters=filters,
                target=target_for_api,
                dry_run=False,
            )
        # Display change outcome
        return PrintInCharte(
            render_template(
                "project/MassAnnotationEdition.html",
                header=header,
                nb_rows=len(res2.last_entries),
                projid=target_proj.projid,
            )
        )


def _digest_changes(api_result):
    """
    From provided changes (full list!), do a summary of what will happen.
    """
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
