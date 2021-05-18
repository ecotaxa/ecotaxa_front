from flask import request
from flask_security import login_required

from appli import app, gvp
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ObjectsApi
from to_back.ecotaxa_cli_py.models import ClassifyReq, BulkUpdateReq


@app.route('/prj/ManualClassif/<int:_PrjId>', methods=['GET', 'POST'])
@login_required
def PrjManualClassif(_PrjId):
    object_ids = []
    classifications = []
    # Sanitize & convert input
    for k, v in request.form.items():
        # e.g. changes[160030063]: -1
        if k[0:7] != "changes":
            continue
        try:
            obj_id = int(k[8:-1])
            if v not in ("-1", ""):
                _tst = int(v)
            else:
                v = -1
        except ValueError:
            app.logger.info("ManualClassif: Bad form variable %s %s", k, v)
            continue
        object_ids.append(obj_id)
        classifications.append(v)
    if len(object_ids) == 0:
        return '<span class="label label-warning">No pending change to update</span>'
    # The needed classif_qual, i.e., as it comes from UI, 'V' for validated or 'D' for dubious
    wanted_qualif = gvp('qual')

    try:
        with ApiClient(ObjectsApi, request) as api:
            req = ClassifyReq(target_ids=object_ids,
                              classifications=classifications,
                              wanted_qualification=wanted_qualif)
            nb_upd = api.classify_object_set_object_set_classify_post(req)
        if nb_upd < 0:
            # Not all was done
            ret = '<span class="label label-danger">Unable to save _all_ changes</span>'
        elif nb_upd == 0:
            ret = '<span class="label label-success">Nothing found to update</span>'
        else:
            ret = '<span class="label label-success">Database update Successful</span>'
    except ApiException as ae:
        if ae.status in (401, 403):
            ret = '<span class="label label-danger">You cannot Annotate this project</span>'
        else:
            app.logger.exception(ae)
            ret = '<span class="label label-danger">Changes NOT saved (see logs)</span>'
    except Exception as e:  # noqa
        app.logger.exception(e)
        ret = '<span class="label label-danger">Changes NOT saved (see logs)</span>'
    return ret


@app.route('/prj/UpdateComment/<int:ObjId>', methods=['GET', 'POST'])
@login_required
def PrjUpdateComment(ObjId):
    # Update single field of object
    updates = [{"ucol": "complement_info", "uval": gvp('comment')}]
    with ApiClient(ObjectsApi, request) as api:
        try:
            nb_rows = api.update_object_set_object_set_update_post(BulkUpdateReq(target_ids=[ObjId],
                                                                                 updates=updates))
        except ApiException as ae:
            if ae.status == 404:
                return "Object doesn't exists"
            elif ae.status in (401, 403):
                return "You cannot write data in this project"

    if nb_rows == 1:
        return '<span class="label label-success">Database update Successful</span>'
    else:
        return '<span class="label label-warning">Database update failed</span>'
