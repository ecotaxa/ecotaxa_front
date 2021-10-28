# -*- coding: utf-8 -*-

from flask import render_template, g, redirect

from appli import PrintInCharte, gvg, XSSEscape
from appli.jobs.Job import Job
from appli.tasks.importcommon import *
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi, ObjectsApi
from to_back.ecotaxa_cli_py.models import ExportReq, ExportRsp, ProjectModel, JobModel


class ExportJob(Job):
    """
        Subset, just GUI here, bulk of job is subcontracted to back-end.
    """
    UI_NAME = "GenExport"

    @classmethod
    def initial_dialog(cls):
        """ In UI/flask, initial load, GET """
        prj_id = int(gvg("projid"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid, XSSEscape(target_prj.title))

        filters = {}
        filtertxt = cls._extract_filters_from_url(filters, target_prj)

        formdata = {"what": "TSV",
                    "objectdata": "1",
                    "processdata": "1",
                    "acqdata": "1",
                    "sampledata": "1",
                    "splitcsvby": "",
                    "latin1": ""
                    }

        html = "<h3>Data Export</h3>"
        return render_template('jobs/export_create.html', header=html,
                               form=formdata, filtertxt=filtertxt)

    @classmethod
    def create_or_update(cls):
        """ In UI/flask, submit/resubmit of initial page, POST """
        prj_id = int(gvg("projid"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid, XSSEscape(target_prj.title))

        what = gvp("what")
        objectdata = 'O' if gvp("objectdata") == "1" else ""
        processdata = 'P' if gvp("processdata") == "1" else ""
        acqdata = 'A' if gvp("acqdata") == "1" else ""
        sampledata = 'S' if gvp("sampledata") == "1" else ""
        histodata = 'H' if gvp("histodata") == "1" else ""
        commentsdata = 'C' if gvp("commentsdata") == "1" else ""
        usecomasepa = gvp("usecomasepa") == "1"
        formatdates = gvp("formatdates") == "1"
        sumsubtotal = gvp("sumsubtotal")
        internalids = gvp("internalids") == "1"
        exportimages = gvp("exportimages") != ""
        only_first_image = gvp("exportimages") == "1"
        splitcsvby = gvp("splitcsvby")
        putfileonftparea = gvp("putfileonftparea") == "Y"
        latin1 = gvp("latin1") == "1"

        tsv_entities = objectdata + processdata + acqdata + sampledata + histodata + commentsdata

        errors = []
        # Check data validity
        # if len(subsetprojecttitle) < 5:
        #     errors.append("Project name too short")

        filters = {}
        filtertxt = cls._extract_filters_from_url(filters, target_prj)

        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            html = "<h3>Export</h3>"
            formdata = {}
            return render_template('jobs/export_create.html', header=html,
                                   form=formdata, filtertxt=filtertxt)
        else:
            # Do the export on back-end side
            req = ExportReq(project_id=prj_id,
                            exp_type=what,
                            split_by=splitcsvby,
                            coma_as_separator=usecomasepa,
                            format_dates_times=formatdates,
                            with_images=exportimages,
                            with_internal_ids=internalids,
                            only_first_image=only_first_image,
                            sum_subtotal=sumsubtotal,
                            out_to_ftp=putfileonftparea,
                            tsv_entities=tsv_entities,
                            use_latin1=latin1)
            export_req = {"filters": filters,
                          "request": req}
            with ApiClient(ObjectsApi, request) as api:
                rsp: ExportRsp = api.export_object_set(export_req)
            return redirect("/Job/Monitor/%d" % rsp.job_id)

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        prj_id = job.params["req"]["project_id"]
        out_file = job.result["out_file"]
        return cls.final_download_action(job.id, prj_id, out_file)
