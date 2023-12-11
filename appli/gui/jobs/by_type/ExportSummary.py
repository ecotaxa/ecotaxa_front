# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash
from appli import gvg, gvp
from appli.gui.jobs.staticlistes import py_messages
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi, UsersApi
from to_back.ecotaxa_cli_py.models import ExportReq, ExportRsp, ProjectModel, JobModel
from appli.back_config import get_app_manager_mail


class ExportSummaryJob(Job):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME = "SumExport"
    STEP0_TEMPLATE = "/v2/jobs/export_summary.html"
    STEP1_TEMPLATE = "/v2/jobs/_final_download.html"
    EXPORT_TYPE = "SUM"

    @classmethod
    def initial_dialog(cls) -> str:
        """In UI/flask, initial load, GET"""
        prj_id = int(gvg("projid"))
        target_proj = cls.get_target_prj(prj_id, full=True)
        if target_proj == None:
            return render_template(cls.NOPROJ_TEMPLATE, projid=prj_id)
        # Get stored last server path value for this project, if any
        with ApiClient(UsersApi, request) as uapi:
            server_path = uapi.get_current_user_prefs(prj_id, "cwd")
        return render_template(
            cls.STEP0_TEMPLATE,
            ServerPath=server_path,
            TxtTaxoMap="",
            target_proj=dict(
                {
                    "title": target_proj.title,
                    "projid": target_proj.projid,
                }
            ),
            prjmanagermail=target_proj.managers[0].email,
            appmanagermailto=get_app_manager_mail(request),
            referer=request.referrer,
        )

    @classmethod
    def create_or_update(cls):
        """In UI/flask, submit/resubmit of initial page, POST"""
        prj_id = int(gvg("projid"))
        target_proj = cls.get_target_prj(prj_id)

        what = gvp("what")
        objectdata = "O" if gvp("objectdata") == "1" else ""
        processdata = "P" if gvp("processdata") == "1" else ""
        acqdata = "A" if gvp("acqdata") == "1" else ""
        sampledata = "S" if gvp("sampledata") == "1" else ""
        histodata = "H" if gvp("histodata") == "1" else ""
        commentsdata = "C" if gvp("commentsdata") == "1" else ""
        usecomasepa = gvp("usecomasepa") == "1"
        formatdates = gvp("formatdates") == "1"
        sumsubtotal = gvp("sumsubtotal")
        internalids = gvp("internalids") == "1"
        exportimages = gvp("exportimages") != ""
        only_first_image = gvp("exportimages") == "1"
        splitcsvby = gvp("splitcsvby")

        tsv_entities = (
            objectdata + processdata + acqdata + sampledata + histodata + commentsdata
        )

        errors = []
        # Check data validity
        # if len(subsetprojecttitle) < 5:
        #     errors.append("Project name too short")

        filters = {}
        filtertxt = cls._extract_filters_from_url(filters)

        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            formdata = {}
            return render_template(
                cls.STEP0_TEMPLATE,
                form=formdata,
                filtertxt=filtertxt,
                target_proj=target_proj,
            )
        else:
            # Do the export on back-end side
            req = ExportReq(
                project_id=prj_id,
                exp_type=what,
                split_by=splitcsvby,
                coma_as_separator=usecomasepa,
                format_dates_times=formatdates,
                with_images=exportimages,
                with_internal_ids=internalids,
                only_first_image=only_first_image,
                sum_subtotal=sumsubtotal,
                out_to_ftp=False,
                tsv_entities=tsv_entities,
                use_latin1=False,
            )
            export_req = {"filters": filters, "request": req}
            with ApiClient(ObjectsApi, request) as api:
                rsp: ExportRsp = api.export_object_set(export_req)
            return redirect(url_for("gui_job_show", job_id=rsp.job_id))

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        if job.state == "F":
            projid = job.params["req"]["project_id"]
            target_proj = cls.get_target_prj(projid)
            return render_template(
                cls.STEP1_TEMPLATE,
                jobid=job.id,
                projid=projid,
                outfile=job.result["out_file"],
            )
        else:
            return ""
