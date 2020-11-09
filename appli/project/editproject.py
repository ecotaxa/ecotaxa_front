import collections
import os
from pathlib import Path
from typing import List

from flask import render_template, g, flash, request, json
from flask_security import login_required

from appli import app, PrintInCharte, gvp, XSSEscape, TempTaskDir
######################################################################################################################
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ApiException, UserModel, UsersApi, \
    TaxonomyTreeApi, TaxonModel, ProjectStatsModel, MiscApi


@app.route('/prj/edit/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEdit(PrjId, privs_only=False):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                flash("Project doesn't exist", 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")
            elif ae.status == 403:
                flash('You cannot edit settings for this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.useselect4 = True
    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    g.privs_only = privs_only

    # User names for display & search in select box
    g.users = collections.OrderedDict()
    users_by_id = {}
    with ApiClient(UsersApi, request) as api:
        all_users: List[UserModel] = api.search_user_users_search_get(by_name="%%")
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
        for f in request.form:
            if f in dir(target_proj):
                setattr(target_proj, f, gvp(f))
        if previous_cnn != target_proj.cnn_network_id:
            flash("SCN features erased", "success")
        target_proj.visible = True if gvp('visible') == 'Y' else False
        posted_classif_list = gvp('initclassiflist')
        # The original list is displayed using str(list), so there is a bit of formatting inside
        posted_classif_list = posted_classif_list.replace(" ", "")
        if posted_classif_list and posted_classif_list[0] == "[":
            posted_classif_list = posted_classif_list[1:]
        if posted_classif_list and posted_classif_list[-1] == "]":
            posted_classif_list = posted_classif_list[:-1]
        target_proj.init_classif_list = [int(cl_id) for cl_id in posted_classif_list.split(",")
                                         if cl_id.isdigit()]
        # Update lists by right
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
        new_member = gvp('priv_new_member')
        if new_member != '':
            priv_for_new_member = gvp('priv_new_privilege')
            members_by_right[priv_for_new_member].append(users_by_id[int(new_member)])

        # Sanity check
        if len(target_proj.managers) == 0:
            flash("At least one manager is needed", "error")

        # # Point owner to the right manager
        # owner_id = int(gvp('owner_id','0'))
        # for a_member in target_proj.managers:
        #     if a_member.id == owner_id:
        #         target_proj.owner = a_member
        #         break
        # else:
        #     flash("Owner has to be a Manager", "error")

        # Update on back-end
        with ApiClient(ProjectsApi, request) as api:
            try:
                api.update_project_projects_project_id_put(project_id=target_proj.projid,
                                                           project_model=target_proj)
            except ApiException as ae:
                flash("Update problem: %s" % ae, "error")

    # Reconstitute members list with levels
    g.members = []
    for a_priv, members_for_priv in members_by_right.items():
        for a_user in members_for_priv:
            g.members.append({"member_id": str(a_user.id), "privilege": a_priv})

    # g.managers_by_id = {mgr.id:mgr.name for mgr in target_proj.managers}

    lst = [str(tid) for tid in target_proj.init_classif_list]
    with ApiClient(TaxonomyTreeApi, request) as api:
        res: List[TaxonModel] = api.query_taxa_set_taxa_set_query_get(ids=" ".join(lst))
    g.predeftaxo = [(r.id, r.display_name) for r in res]

    # TODO: Get from metadata
    g.maplist = ['objtime', 'objdate', 'latitude', 'longitude', 'depth_min', 'depth_max']
    g.maplist.extend(target_proj.obj_free_cols.keys())

    # TODO: move to back-end
    g.scn = _GetSCNNetworks()

    # TODO: Cache of course, it's constants!
    with ApiClient(MiscApi, request) as api:
        possible_licenses = api.used_constants_constants_get().license_texts

    return render_template('project/editproject.html', data=target_proj,
                           possible_licenses=possible_licenses)


######################################################################################################################
# noinspection PyUnusedLocal
@app.route('/prj/popupeditpreset/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def Prjpopupeditpreset(PrjId):
    # Query accessible projects
    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects_projects_search_get(also_others=False,
                                                                           filter_subset=False)
    # And their statistics
    prj_ids = " ".join([str(a_prj.projid) for a_prj in prjs])
    with ApiClient(ProjectsApi, request) as api:
        stats: List[ProjectStatsModel] = api.project_stats_project_set_stats_get(ids=prj_ids)

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
        res: List[TaxonModel] = api.query_taxa_set_taxa_set_query_get(ids=" ".join(lst))
    taxo_map = {taxon_rec.id: taxon_rec.display_name for taxon_rec in res}

    txt = ""
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
        a_prj.presetids = ",".join([str(x) for x in prj_initclassif_list])
        a_prj.preset = ", ".join(sorted(result))

        result = []
        for t in objtaxon:
            resolved = taxo_map.get(int(t), None)
            if resolved:
                result.append(resolved)
        a_prj.objtaxonnotinpreset = ", ".join(sorted(result))
        a_prj.objtaxonids = ",".join([str(x) for x in objtaxon])

    # render the table
    return render_template('project/popupeditpreset.html', Prj=prjs, txt=txt)


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
