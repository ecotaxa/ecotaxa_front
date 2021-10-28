import collections
import os
from pathlib import Path
from typing import List

from flask import render_template, g, flash, request, json
from flask_security import login_required

from appli import app, PrintInCharte, gvp, XSSEscape, TempTaskDir
from appli.constants import MappableObjectColumns, MappableParentColumns
######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import (ProjectsApi, UsersApi, TaxonomyTreeApi, MiscApi)
from to_back.ecotaxa_cli_py.models import (ProjectModel, UserModel, TaxonModel, ProjectTaxoStatsModel)


@app.route('/prj/edit/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEdit(PrjId, privs_only=False):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exist", 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")
            elif ae.status in (401, 403):
                flash('You cannot edit settings for this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    g.privs_only = privs_only

    # User names for display & search in select box
    g.users = collections.OrderedDict()
    users_by_id = {}
    with ApiClient(UsersApi, request) as api:
        all_users: List[UserModel] = api.search_user(by_name="%%")
    for a_user in sorted(all_users, key=lambda u: u.name.strip().lower()):
        g.users[str(a_user.id)] = a_user.name.strip()
        users_by_id[a_user.id] = a_user

    # data structure used in both display & submit
    members_by_right = {'Manage': target_proj.managers,
                        'Annotate': target_proj.annotators,
                        'View': target_proj.viewers}

    if gvp('save') == "Y":
        # Load posted variables
        previous_cnn = target_proj.cnn_network_id
        posted_contact_id = None

        for a_var in request.form:
            # Update the project (from API call) with posted variables
            if a_var in dir(target_proj):
                # TODO: Big assumption here, variables need to have same name as Model fields
                setattr(target_proj, a_var, gvp(a_var))
            if a_var == 'contact_user_id':
                posted_contact_id = gvp(a_var)
            if a_var == 'initclassiflist':
                posted_classif_list = gvp('initclassiflist')
                # The original list is displayed using str(list), so there is a bit of formatting inside
                posted_classif_list = posted_classif_list.replace(" ", "")
                if posted_classif_list and posted_classif_list[0] == "[":
                    posted_classif_list = posted_classif_list[1:]
                if posted_classif_list and posted_classif_list[-1] == "]":
                    posted_classif_list = posted_classif_list[:-1]
                target_proj.init_classif_list = [int(cl_id) for cl_id in posted_classif_list.split(",")
                                                 if cl_id.isdigit()]

        # Absent means "not checked"
        target_proj.visible = gvp('visible') == 'Y'

        if previous_cnn != target_proj.cnn_network_id:
            flash("SCN features erased", "success")

        # Update (in place) lists by right for permission update
        for a_priv, members_for_priv in members_by_right.items():
            for a_member in members_for_priv.copy():
                a_member_id = a_member.id
                if gvp('priv_%s_delete' % a_member_id) == 'Y':
                    members_for_priv.remove(a_member)
                    continue
                member_id_posted = gvp('priv_%s_member' % a_member_id)
                if member_id_posted != '':
                    priv_posted = gvp('priv_%s_privilege' % a_member_id)
                    if member_id_posted != a_member_id or priv_posted != a_priv:
                        new_member = users_by_id[int(member_id_posted)]
                        members_for_priv.remove(a_member)
                        members_by_right[priv_posted].append(new_member)
                else:
                    # Small cross in user select -> no more user name
                    members_for_priv.remove(a_member)
        # Add new member(s) which were added in the list by a previous failed Save
        for a_var, a_val in request.form.items():
            if a_var.startswith("priv_") and a_var.endswith("_member"):
                if a_var == 'priv_new_member':
                    continue
                a_member_id = int(a_var[5:-7])
                if gvp('priv_%s_delete' % a_member_id) == 'Y':
                    continue
                priv_posted = gvp('priv_%s_privilege' % a_member_id)
                for a_user_there in members_by_right[priv_posted]:
                    if a_user_there.id == a_member_id:
                        a_member_id = None
                        break
                if a_member_id:
                    new_member = users_by_id[int(a_member_id)]
                    members_by_right[priv_posted].append(new_member)
        new_member = gvp('priv_new_member')
        if new_member != '':
            priv_for_new_member = gvp('priv_new_privilege')
            members_by_right[priv_for_new_member].append(users_by_id[int(new_member)])

        do_update = True
        # Pick the contact from managers
        contact_user = None
        for a_user in members_by_right['Manage']:
            if str(a_user.id) == posted_contact_id:
                contact_user = a_user
                break
        else:
            flash('A contact person needs to be designated among the current project managers. '
                  'Use the "Edit privileges only" button or scroll down to bottom of the page.',
                  "error")
            do_update = False
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
                    api.update_project(project_id=target_proj.projid,
                                       project_model=target_proj)
            except ApiException as ae:
                flash("Update problem: %s" % ae, "error")

    # Reconstitute members list with levels
    g.members = []
    for a_priv, members_for_priv in members_by_right.items():
        for a_user in members_for_priv:
            g.members.append({"member_id": str(a_user.id), "privilege": a_priv})

    g.contact_user_id = str(target_proj.contact.id) if target_proj.contact else None

    lst = [str(tid) for tid in target_proj.init_classif_list]
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set(ids=" ".join(lst))
    g.predeftaxo = [(r.id, r.display_name) for r in res]
    g.predeftaxo.sort(key=lambda r: r[1].lower())

    # TODO: Get from metadata
    g.maplist = list(MappableParentColumns)
    g.maplist.extend(list(MappableObjectColumns))
    g.maplist.extend(target_proj.obj_free_cols.keys())

    # TODO: move to back-end
    g.scn = _GetSCNNetworks()

    # TODO: Cache of course, it's constants!
    with ApiClient(MiscApi, request) as api:
        possible_licenses = api.used_constants().license_texts

    return render_template('project/editproject.html', data=target_proj,
                           possible_licenses=possible_licenses)


######################################################################################################################
# noinspection PyUnusedLocal
@app.route('/prj/popupeditpreset/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def Prjpopupeditpreset(PrjId):
    # Query accessible projects
    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects(also_others=False,
                                                       filter_subset=False)
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
        # Inject taxon lists for display
        result = []
        prj_initclassif_list = set(a_prj.init_classif_list)
        try:
            objtaxon = set(stats_per_project[a_prj.projid])
        except KeyError:
            # No stats
            objtaxon = set()
        # 'Extra' are the taxa used, but not in the classification preset
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
        prjs_pojo.append(a_prj)

    # render the table
    return render_template('project/popupeditpreset.html', Prj=prjs_pojo, txt=txt)


######################################################################################################################
def _GetSCNNetworks():
    models = {}
    model_folder = (Path(TempTaskDir) / "../SCN_networks")
    model_folder = Path(os.path.normpath(model_folder.as_posix()))
    if model_folder.exists():
        model_folder = model_folder.resolve()
        for a_dir in model_folder.glob("*"):
            if a_dir.is_dir() and (a_dir / "meta.json").is_file():
                models[a_dir.name] = json.load((a_dir / "meta.json").open("r"))
                # Models[dir.name] = json.load((dir / "meta.json").open("r")).get('name',dir.name)
    return models


######################################################################################################################
@app.route('/prj/editpriv/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditPriv(PrjId):
    return PrjEdit(PrjId, privs_only=True)
