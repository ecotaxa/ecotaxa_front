import datetime
from typing import List

from flask import render_template, flash, session, request, Markup
from flask_security import login_required

from appli import app, PrintInCharte, gvg
######################################################################################################################
from appli.project.main import _manager_mail
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import ProjectsApi, ProjectModel, UsersApi, UserModelWithRights, TaxonomyTreeApi, \
    TaxonomyTreeStatus


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

    with ApiClient(UsersApi, request) as api:
        user: UserModelWithRights = api.show_current_user_users_me_get()

    if Others:
        CanCreate = False
    else:
        CanCreate = 1 in user.can_do

    with ApiClient(TaxonomyTreeApi, request) as api:
        status: TaxonomyTreeStatus = api.taxa_tree_status_taxa_status_get()
        try:
            last_refresh = datetime.datetime.strptime(status.last_refresh, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            last_refresh = None
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:
        fashtxt = "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, " \
                  "Ask application administrator to do it."  # +str(PDT.lastserverversioncheck_datetime)
        fashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(fashtxt), 'warning')

    return PrintInCharte(
        render_template('project/list.html', PrjList=prjs, CanCreate=CanCreate,
                        filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                        Others=Others, isadmin=2 in user.can_do,
                        _manager_mail=_manager_mail))


######################################################################################################################
@app.route('/prjothers/')
@login_required
def ProjectsOthers():
    return indexProjects(Others=True)
