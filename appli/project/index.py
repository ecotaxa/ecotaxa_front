import datetime

from typing import List

from flask import render_template, flash, session, request, Markup
from flask_security import login_required

from appli import app, PrintInCharte, gvg
######################################################################################################################
from appli.project.main import _manager_mail
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import ProjectModel, UserModelWithRights, TaxonomyTreeStatus


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
        prjs: List[ProjectModel] = api.search_projects(also_others=Others,
                                                       title_filter=filt_title,
                                                       instrument_filter=filt_instrum,
                                                       filter_subset=(filt_subset == 'Y'))
    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())

    with ApiClient(UsersApi, request) as api:
        user: UserModelWithRights = api.show_current_user()

    if Others:
        CanCreate = False
    else:
        CanCreate = 1 in user.can_do

    with ApiClient(TaxonomyTreeApi, request) as api:
        status: TaxonomyTreeStatus = api.taxa_tree_status()
        try:
            last_refresh = datetime.datetime.strptime(status.last_refresh, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            last_refresh = None
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:
        fashtxt = "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, " \
                  "Ask application administrator to do it."  # +str(PDT.lastserverversioncheck_datetime)
        fashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(fashtxt), 'warning')

    # https://pynative.com/make-python-class-json-serializable/
    # https://stackoverflow.com/questions/24719592/sending-data-as-json-object-from-python-to-javascript-with-jinja
    # Encode Object into JSON formatted Data using jsonpickle
    # https://www.npmjs.com/package/jsonpickle
    # https://github.com/cuthbertLab/jsonpickleJS/blob/master/tests/testUnpickle.html
    # See the cuthbertLab/music21 and cuthbertLab/music21j projects and especially the .show('vexflow') component for an example of how jsonpickleJS can be extremely useful for projects that have parallel data structures between Python and Javascript.    
    # pl:List = [prjs[0]] # use pl instead of prjs if you want to test with only one project
    #connectPythonToPrime:bool = True
    connectPythonToPrime:bool = False
    if (connectPythonToPrime):
        import jsonpickle # need of jsonpickle only in that case
        # Do all the "boring" work in the Python part.
        # Basically, everything that cannot be done easily on the HTML side should be done on the Python side ;-)
        for oneProj in prjs:
            if (oneProj.pctvalidated != None):
                oneProj.pctvalidated = round(oneProj.pctvalidated, 2)
            if (oneProj.pctclassified != None):
                oneProj.pctclassified = round(oneProj.pctclassified, 2)            
        varJSON = jsonpickle.encode(prjs, unpicklable=False)
        return PrintInCharte(
            render_template('project/projects_list.html', PrjList=varJSON, CanCreate=CanCreate,
            filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                        Others=Others, isadmin=2 in user.can_do,
                        _manager_mail=_manager_mail))
    else: # "historic" code
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
