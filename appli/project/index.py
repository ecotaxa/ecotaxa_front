import datetime
from typing import List

from flask import render_template, flash, session, request, Markup
from flask_login import current_user
from flask_security import login_required

import appli
from appli import app, PrintInCharte, database, gvg
######################################################################################################################
from appli.project.main import _manager_mail
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel


# noinspection PyPep8Naming
@app.route('/prj/')
@login_required
def indexProjects(Others=False):
    filt_title = gvg('filt_title', session.get('prjfilt_title', ''))
    session['prjfilt_title'] = filt_title

    filt_instrum = gvg('filt_instrum', session.get('prjfilt_instrum', ''))
    session['prjfilt_instrum'] = filt_instrum

    # Les checkbox ne sont pas transmises si elle ne sont pas coché,
    if 'filt_title' in request.args:  # donc si le filtre du titre est transmis on utilise le get
        filt_subset = gvg('filt_subset', "")
        session['prjfilt_subset'] = filt_subset
    else:  # Sinon on prend la valeur de la session.
        filt_subset = session.get('prjfilt_subset', '')

    with ApiClient(ProjectsApi, request) as api:
        prjs: List[ProjectModel] = api.search_projects_projects_search_get(also_others=Others,
                                                                           title_filter=filt_title,
                                                                           instrument_filter=filt_instrum,
                                                                           filter_subset=(filt_subset == 'Y'))
    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())

    CanCreate = False
    if not Others:
        if current_user.has_role(database.AdministratorLabel) or current_user.has_role(database.ProjectCreatorLabel):
            CanCreate = True

    PDT = database.PersistantDataTable.query.first()
    if PDT is None or PDT.lastserverversioncheck_datetime is None or (
            datetime.datetime.now() - PDT.lastserverversioncheck_datetime).days > 7:
        fashtxt = "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, " \
                  "Ask application administrator to do it."  # +str(PDT.lastserverversioncheck_datetime)
        fashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(fashtxt), 'warning')

    return PrintInCharte(
        render_template('project/list.html', PrjList=prjs, CanCreate=CanCreate,
                        AppManagerMailto=appli.GetAppManagerMailto(),
                        filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum, Others=Others,
                        isadmin=current_user.has_role(database.AdministratorLabel),
                        _manager_mail=_manager_mail))


######################################################################################################################
@app.route('/prjothers/')
@login_required
def ProjectsOthers():
    return indexProjects(Others=True)
