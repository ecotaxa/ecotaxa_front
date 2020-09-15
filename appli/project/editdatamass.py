from typing import List, Dict

from flask import render_template, g, flash, request
from flask_login import current_user
from flask_security import login_required

import appli.project.sharedfilter as sharedfilter
from appli import app, PrintInCharte, gvg, gvp, XSSEscape
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, ObjectHeaderModel, ApiException, ObjectsApi, SamplesApi, \
    BulkUpdateReq, ProcessesApi, AcquisitionsApi


def GetFieldList(prj_model: ProjectModel):
    fieldlist = []

    excluded = set()
    for k in ObjectHeaderModel.openapi_types.keys():
        # TODO: Hardcoded, not rename-friendly
        if k not in ('objid', 'projid', 'img0id', 'imgcount'):
            fieldlist.append({'id': 'h' + k, 'text': 'object.' + k})
        else:
            excluded.add(k)
    assert excluded == {'objid', 'projid', 'img0id', 'imgcount'}, "Attempt to exclude a non-existing column"

    # TODO: Hardcoded, not completely rename-friendly
    # 2 fields in object_fields
    fieldlist.append({'id': 'f''orig_id', 'text': 'object.''orig_id'})
    fieldlist.append({'id': 'f''object_link', 'text': 'object.''object_link'})
    # 1 field in sample
    fieldlist.append({'id': 's''dataportal_descriptor', 'text': 'sample.''dataportal_descriptor'})
    # 1 field in acquisition
    fieldlist.append({'id': 'a''instrument', 'text': 'acquis.''instrument'' (fixed)'})

    MapList = (('f', prj_model.obj_free_cols), ('s', prj_model.sample_free_cols),
               ('a', prj_model.acquisition_free_cols), ('p', prj_model.process_free_cols))
    MapPrefix = {'f': 'object.', 's': 'sample.', 'a': 'acquis.', 'p': 'process.'}
    mapv: Dict[str, str]
    for mapk, mapv in MapList:
        for k in sorted(mapv.keys()):
            fieldlist.append({'id': mapk + mapv[k], 'text': MapPrefix[mapk] + k})
    return fieldlist


######################################################################################################################
@app.route('/prj/editdatamass/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjEditDataMass(PrjId):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot do mass data edition on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt = "<h3>Project Mass data edition </h3>"

    filtres = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filtres[k] = gvg(k, "")

    # Get the field name from user input
    field = gvp('field')
    if field and gvp('newvalue'):
        # First field lettre gives the entity to update
        tablecode = field[0]
        # What's left is field name
        field = field[1:]
        new_value = gvp('newvalue')
        # Query the filtered list in project, if no filter then it's the whole project
        with ApiClient(ObjectsApi, request) as api:
            res = api.get_object_set_object_set_project_id_query_post(PrjId, filtres)
        # Call the back-end service, depending on the field to update
        updates = [{"ucol": field, "uval": new_value}]
        if tablecode in ("h", "f"):
            # Object update
            if field == 'classif_id':
                updates.append({"ucol": "classif_when", "uval": "current_timestamp"})
                updates.append({"ucol": "classif_who", "uval": str(current_user.id)})
            with ApiClient(ObjectsApi, request) as api:
                nb_rows = api.update_object_set_object_set_update_post(BulkUpdateReq(target_ids=res.object_ids,
                                                                                     updates=updates))
        elif tablecode == "p":
            # Process update, i.e. parents
            processes = [a_parent for a_parent in set(res.process_ids) if a_parent]
            with ApiClient(ProcessesApi, request) as api:
                nb_rows = api.update_processes_process_set_update_post(BulkUpdateReq(target_ids=processes,
                                                                                     updates=updates))
        elif tablecode == "a":
            # Acquisition update
            acquisitions = [a_parent for a_parent in set(res.acquisition_ids) if a_parent]
            with ApiClient(AcquisitionsApi, request) as api:
                nb_rows = api.update_acquisitions_acquisition_set_update_post(BulkUpdateReq(target_ids=acquisitions,
                                                                                            updates=updates))
        elif tablecode == "s":
            # Sample update
            samples = [a_parent for a_parent in set(res.sample_ids) if a_parent]
            with ApiClient(SamplesApi, request) as api:
                nb_rows = api.update_samples_sample_set_update_post(BulkUpdateReq(target_ids=samples,
                                                                                  updates=updates))
        flash('%s data rows updated' % nb_rows, 'success')

    if field == 'latitude' or field == 'longitude' or gvp('recompute') == 'Y':
        with ApiClient(ProjectsApi, request) as api:
            api.project_recompute_geography_projects_project_id_recompute_geo_post(PrjId)
        flash('All samples latitude and longitude updated', 'success')

    if len(filtres):
        # Query the filtered list in project
        with ApiClient(ObjectsApi, request) as api:
            object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres).object_ids
        # Warn the user
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "USING Active Project Filters, {0} objects</span>". \
            format(len(object_ids))
    else:
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "Apply to ALL ENTITIES OF THE PROJECT (NO Active Filters)</span>"

    field_list = GetFieldList(target_proj)

    return PrintInCharte(render_template("project/prjeditdatamass.html",
                                         Lst=field_list, header=txt))


######################################################################################################################
@app.route('/prj/resettopredicted/<int:PrjId>', methods=['GET', 'POST'])
@login_required
def PrjResetToPredicted(PrjId):
    # noinspection PyStatementEffect
    request.form  # Force la lecture des données POST sinon il y a une erreur 504

    # Security & sanity checks
    with ApiClient(ProjectsApi, request) as api:
        try:
            target_proj: ProjectModel = api.project_query_projects_project_id_query_get(PrjId, for_managing=True)
        except ApiException as ae:
            if ae.status == 404:
                return "Project doesn't exists"
            elif ae.status == 403:
                flash('You cannot do reset to predicted on this project', 'error')
                return PrintInCharte("<a href=/prj/>Select another project</a>")

    g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_proj.projid, XSSEscape(target_proj.title))
    txt = "<h3>Reset status to predicted</h3>"

    filtres = {}
    for k in sharedfilter.FilterList:
        if gvg(k):
            filtres[k] = gvg(k, "")

    proceed = gvp('process')
    if proceed == 'Y':
        # Do the job on back-end
        with ApiClient(ObjectsApi, request) as api:
            api.reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post(PrjId, filtres)

        # flash('Data updated', 'success')
        txt += "<a href='/prj/%s' class='btn btn-primary'>Back to project</a> " % target_proj.projid

        return PrintInCharte(txt)

    if len(filtres):
        # Query the filtered list in project
        with ApiClient(ObjectsApi, request) as api:
            object_ids: List[int] = api.get_object_set_object_set_project_id_query_post(PrjId, filtres).object_ids
        # Warn the user
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "USING Active Project Filters, {0} objects</span>" \
            .format(len(object_ids))
    else:
        txt += "<span style='color:red;font-weight:bold;font-size:large;'>" \
               "Apply to ALL OBJECTS OF THE PROJECT (NO Active Filters)</span>"

    # The eventual filter is in the URL (GET), so when POST-ed again after validation, the filter is preserved
    return PrintInCharte(render_template("project/prjresettopredicted.html",
                                         header=txt))
