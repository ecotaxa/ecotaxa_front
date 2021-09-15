# -*- coding: utf-8 -*-
import datetime
import time

from flask import render_template, g, redirect

from appli import PrintInCharte, gvg, XSSEscape
from appli.jobs.Job import Job
from appli.project import sharedfilter
from appli.tasks.importcommon import *
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ApiException
from to_back.ecotaxa_cli_py.api import ProjectsApi
from to_back.ecotaxa_cli_py.models import CreateProjectReq, SubsetReq, SubsetRsp, ProjectModel, JobModel


class SubsetJob(Job):
    """
        Subset, just GUI here, bulk of job is subcontracted to back-end.
    """
    UI_NAME = "Subset"

    @classmethod
    def initial_dialog(cls):
        """ In UI/flask, initial load, GET """
        prj_id = int(gvg("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid, XSSEscape(target_prj.title))

        filters = {}
        filtertxt = cls._extract_filters_from_url(filters, target_prj)

        formdata = {'subsetprojecttitle': (target_prj.title + " - Subset created on " +
                                           (datetime.date.today().strftime('%Y-%m-%d')))[0:255],
                    'grptype': 'C',
                    'valtype': 'P',
                    'vvaleur': "",
                    'pvaleur': "10",
                    'withimg': False}

        html = "<h3>Extract subset</h3>"
        return render_template('jobs/subset_create.html', header=html,
                               form=formdata, prj_id=prj_id,
                               filters=filters, filtertxt=filtertxt)

    @classmethod
    def create_or_update(cls):
        """ In UI/flask, display of initial page (GET) or submit/resubmit (POST) """
        method = request.method
        if method == 'GET':
            prj_id = int(gvg("p"))
        elif method == 'POST':
            prj_id = int(gvp("p"))
        with ApiClient(ProjectsApi, request) as api:
            try:
                target_prj: ProjectModel = api.project_query_projects_project_id_get(prj_id, for_managing=False)
            except ApiException as ae:
                if ae.status in (401, 403):
                    return PrintInCharte("ACCESS DENIED for this project")
        g.headcenter = "<h4><a href='/prj/{0}'>{1}</a></h4>".format(target_prj.projid, XSSEscape(target_prj.title))

        subsetprojecttitle = gvp("subsetprojecttitle")
        valtype = gvp("valtype")
        vvaleur = gvp("vvaleur")
        pvaleur = gvp("pvaleur")
        withimg = gvp("withimg")
        grptype = gvp("grptype")

        errors = []
        # Check data validity
        if len(subsetprojecttitle) < 5:
            errors.append("Project name too short")
        if valtype == 'V':
            try:
                valeur = int(vvaleur)
                if valeur <= 0:
                    errors.append("Absolute value not in range (>0)")
            except ValueError:
                errors.append("Invalid absolute value")
        elif valtype == 'P':
            try:
                valeur = int(pvaleur)
                if valeur <= 0 or valeur > 100:
                    errors.append("% value not in range (]0, 100])")
            except ValueError:
                errors.append("Invalid % value")
        else:
            errors.append("You must select the object selection parameter '% of values' or '# of objects'")

        filters = {}
        if method == 'GET':
            filtertxt = cls._extract_filters_from_url(filters, target_prj)
        elif method == 'POST':
            filtertxt = cls._extract_filters_from_form(filters, target_prj)

        if len(errors) > 0:
            for e in errors:
                flash(e, "error")
            html = "<h3>Extract subset</h3>"
            formdata = {'subsetprojecttitle': subsetprojecttitle,
                        'grptype': grptype,
                        'valtype': valtype,
                        'vvaleur': vvaleur if valtype == 'V' else '',
                        'pvaleur': pvaleur if valtype == 'P' else '',
                        'withimg': withimg}
            return render_template('jobs/subset_create.html', header=html,
                                   form=formdata, prj_id=prj_id,
                                   filters=filters, filtertxt=filtertxt)
        else:
            # Create the destination project
            with ApiClient(ProjectsApi, request) as api:
                req = CreateProjectReq(clone_of_id=prj_id,
                                       title=subsetprojecttitle,
                                       visible=False)
                # TODO: The new project has status ANNOTATE. Is it important?
                new_prj_id: int = api.create_project_projects_create_post(req)
            # Do the cloning
            with ApiClient(ProjectsApi, request) as api:
                req = SubsetReq(filters=filters,
                                dest_prj_id=new_prj_id,
                                group_type=grptype,
                                limit_type=valtype,
                                limit_value=valeur,
                                do_images=(withimg == 'Y'))
                rsp: SubsetRsp = api.project_subset_projects_project_id_subset_post(project_id=prj_id,
                                                                                    subset_req=req)
            return redirect("/Job/Monitor/%d" % rsp.job_id)

    # noinspection PyUnresolvedReferences
    @classmethod
    def final_action(cls, job: JobModel):
        # si le status est demandé depuis le monitoring ca veut dire que l'utilisateur est devant,
        # on efface donc la tache et on lui propose d'aller sur la classif manuelle
        prj_id = job.params["prj_id"]
        subset_prj_id = job.params["req"]["dest_prj_id"]
        time.sleep(1)
        # DoTaskClean(self.task.id)
        return ("""<a href='/prj/{0}' class='btn btn-primary btn-sm'  role=button>Go to Original project</a>
        <a href='/prj/{1}' class='btn btn-primary btn-sm'  role=button>Go to Subset Project</a> """
                .format(prj_id, subset_prj_id))
