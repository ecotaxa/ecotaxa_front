# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for
from appli import gvg, gvp
from appli.gui.jobs.staticlistes import py_messages
from appli.gui.jobs.Job import Job
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi
from to_back.ecotaxa_cli_py.models import ExportReq, ExportRsp, ProjectModel, JobModel


class ExportJob(Job):
    """
    Subset, just GUI here, bulk of job is subcontracted to back-end.
    """

    UI_NAME = "GenExport"
    STEP0_TEMPLATE = "/v2/jobs/export.html"
    STEP1_TEMPLATE = "/v2/jobs/_final_download.html"
    EXPORT_TYPE = "TSV"

    @classmethod
    def initial_dialog(cls):
        """In UI/flask, initial load, GET"""
        prj_id = int(gvg("projid"))
        target_proj = cls.get_target_prj(prj_id)
        if target_proj == None:
            return render_template(cls.NOPROJ_TEMPLATE, projid=prj_id)
        from appli.gui.jobs.job_interface import export_format_options

        filters = {}
        filtertxt = cls.extract_filters_from_url(filters)

        formatoptions = export_format_options(cls.EXPORT_TYPE)

        return render_template(
            cls.STEP0_TEMPLATE,
            formatoptions=formatoptions,
            formdata=dict({"what": cls.EXPORT_TYPE}),
            filters=filters,
            target_proj=target_proj,
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

        filters = {}
        filtertxt = cls.extract_filters_from_url(filters)

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
                target_proj=target_proj,
            )
        else:
            return ""
