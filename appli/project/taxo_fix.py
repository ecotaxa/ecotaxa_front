from typing import List

from flask import render_template, g, flash, request
from flask_security import login_required

from appli import app, PrintInCharte, XSSEscape
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException, ProjectTaxoStatsModel, TaxonomyTreeApi, TaxonModel, ObjectsApi
from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py.models import ProjectModel


######################################################################################################################
@app.route('/prj/taxo_fix/<int:prj_id>', methods=['GET', 'POST'])
@login_required
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
        renames = [taxon for taxon in used_taxa if taxon.renm_id is not None]
        renames.sort(key=lambda r: r.name)

        # Also get information about known-in-advance potential renaming targets
        target_ids = [str(taxon.renm_id) for taxon in used_taxa if taxon.renm_id is not None]
        with ApiClient(TaxonomyTreeApi, request) as api:
            taxa_ids = "+".join(target_ids)
            target_taxa: List[TaxonModel] = api.query_taxa_set_taxon_set_query_get(ids=taxa_ids)
        targets = {taxon.id: taxon for taxon in target_taxa}
        target_names = {taxon.id: taxon.name for taxon in target_taxa}

        # # Get the field name from user input
        # field = gvp('field')
        # if field and gvp('newvalue'):
        #     # First field lettre gives the entity to update
        #     tablecode = field[0]
        #     # What's left is field name
        #     field = field[1:]
        #     new_value = gvp('newvalue')
        #     # Query the filtered list in project, if no filter then it's the whole project
        #     with ApiClient(ObjectsApi, request) as api:
        #         res = api.get_object_set_object_set_project_id_query_post(PrjId, filtres)
        #     # Call the back-end service, depending on the field to update
        #     updates = [{"ucol": field, "uval": new_value}]
        #     if tablecode in ("h", "f"):
        #         # Object update
        #         if field == 'classif_id':
        #             updates.append({"ucol": "classif_when", "uval": "current_timestamp"})
        #             updates.append({"ucol": "classif_who", "uval": str(current_user.id)})
        #         with ApiClient(ObjectsApi, request) as api:
        #             nb_rows = api.update_object_set_object_set_update_post(BulkUpdateReq(target_ids=res.object_ids,
        #                                                                                  updates=updates))
        #     elif tablecode == "p":
        #         # Process update, same key as acquisitions
        #         tgt_processes = [a_parent for a_parent in set(res.acquisition_ids) if a_parent]
        #         with ApiClient(ProcessesApi, request) as api:
        #             nb_rows = api.update_processes_process_set_update_post(BulkUpdateReq(target_ids=tgt_processes,
        #                                                                                  updates=updates))
        #     elif tablecode == "a":
        #         # Acquisition update
        #         tgt_acquisitions = [a_parent for a_parent in set(res.acquisition_ids) if a_parent]
        #         with ApiClient(AcquisitionsApi, request) as api:
        #             nb_rows = api.update_acquisitions_acquisition_set_update_post(BulkUpdateReq(target_ids=tgt_acquisitions,
        #                                                                                         updates=updates))
        #     elif tablecode == "s":
        #         # Sample update
        #         tgt_samples = [a_parent for a_parent in set(res.sample_ids) if a_parent]
        #         with ApiClient(SamplesApi, request) as api:
        #             nb_rows = api.update_samples_sample_set_update_post(BulkUpdateReq(target_ids=tgt_samples,
        #                                                                               updates=updates))
        #     flash('%s data rows updated' % nb_rows, 'success')
        #
        # if field == 'latitude' or field == 'longitude' or gvp('recompute') == 'Y':
        #     with ApiClient(ProjectsApi, request) as api:
        #         api.project_recompute_geography_projects_project_id_recompute_geo_post(PrjId)
        #     flash('All samples latitude and longitude updated', 'success')
        #
        # if len(filtres):
        #     # Query the filtered list in project
        #     with ApiClient(ObjectsApi, request) as api:
        #         object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres).object_ids
        #     # Warn the user
        #     txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
        #            "USING Active Project Filters, {0} objects</span>". \
        #         format(len(object_ids))
        # else:
        #     txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
        #            "Apply to ALL ENTITIES OF THE PROJECT (NO Active Filters)</span>"
        #
        # field_list = GetFieldList(target_proj)

        return PrintInCharte(render_template("project/taxo_fix.html",
                                             renames=renames,
                                             targets=targets,
                                             target_names=target_names))
