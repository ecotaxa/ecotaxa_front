from typing import List

from flask import render_template, g, flash, request

from appli import app, PrintInCharte, XSSEscape
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import ProjectModel, TaxonModel, ProjectTaxoStatsModel


######################################################################################################################
@app.route('/prj/taxo_fix/<int:prj_id>', methods=['GET', 'POST'])
def deprecation_management(prj_id):
    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_get(prj_id)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status in (401, 403):
                flash('You cannot do category fix on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

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
                nb_ok = api.reclassify_object_set_object_set_project_id_reclassify_post(project_id=prj_id,
                                                                                        forced_id=tgt_id,
                                                                                        project_filters=filters,
                                                                                        reason='W')
            nb_objs += nb_ok
        # Tell user
        flash("%d objects fixed." % nb_objs)

    if True:
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))

        # Get the list of taxa used in this project
        with ApiClient(ProjectsApi, request) as api:
            stats: List[ProjectTaxoStatsModel] = api.project_set_get_stats_project_set_taxo_stats_get(
                ids=str(target_proj.projid),
                taxa_ids="all")
            populated_taxa = {stat.used_taxa[0]: stat
                              for stat in stats
                              if stat.used_taxa[0] != -1}  # filter unclassified

        # Get full info on the deprecated ones
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join([str(x) for x in populated_taxa.keys()])
            used_taxa: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=taxa_ids)
        renames = [taxon for taxon in used_taxa
                   if taxon.renm_id is not None]
        renames.sort(key=lambda r: r.name)

        # Also get information about advised renaming targets
        advised_ids = [str(taxon.renm_id) for taxon in used_taxa
                       if taxon.renm_id is not None]
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join(advised_ids)
            advised_taxa: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=taxa_ids)
        advised_targets = {taxon.id: taxon for taxon in advised_taxa}

        # From logs, determine what was done before by users
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join([str(x.id) for x in renames])
            community_taxa: List[TaxonModel] = api.reclassif_stats_taxa_reclassification_stats_get(taxa_ids=taxa_ids)
            assert len(renames) == len(community_taxa)
        community_targets = {}
        for a_src, a_tgt in zip(renames, community_taxa):
            if a_src.id != a_tgt.id:
                # Community (non-advised) choice
                community_targets[a_src.id] = a_tgt

        return PrintInCharte(render_template("project/taxo_fix.html",
                                             renames=renames,
                                             advised_targets=advised_targets,
                                             community_targets=community_targets))
