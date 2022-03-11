import datetime
from typing import List

from flask import render_template, flash, session, request, Markup
from flask_login import current_user
from flask_security import login_required

from appli import app, PrintInCharte, gvg, gvgm
from appli.project.__init__ import connectPythonToPrime
######################################################################################################################
from appli.project.index_vue import vue_projects_index
from appli.project.main import _manager_mail
from appli.utils import ApiClient, BuildManagersMail
from to_back.ecotaxa_cli_py.api import ProjectsApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import ProjectModel, UserModelWithRights, TaxonomyTreeStatus


# noinspection PyPep8Naming
@app.route('/prj/')
@login_required
def indexProjects(Others=False):
    filt_title = gvg('filt_title', session.get('prjfilt_title', ''))
    session['prjfilt_title'] = filt_title

    if 'filt_instrum' not in request.args:
        sess_filt_instrum = session.get('prjfilt_instrum', '')
        if sess_filt_instrum:
            filt_instrum = sess_filt_instrum.split("|")
        else:
            filt_instrum = []
    else:
        filt_instrum = gvgm('filt_instrum')  # Get from posted
        session['prjfilt_instrum'] = "|".join(filt_instrum)

    # Les checkbox ne sont pas transmises si elles ne sont pas cochées...
    if 'filt_title' in request.args:  # ...donc si le filtre du titre est transmis on utilise le get
        filt_subset = gvg('filt_subset', "")
        session['prjfilt_subset'] = filt_subset
    else:  # Sinon on prend la valeur de la session.
        filt_subset = session.get('prjfilt_subset', '')

    prjs: List[ProjectModel] = []
    qry_filt_instrum = [''] if len(filt_instrum) == 0 else filt_instrum
    for an_instrument in qry_filt_instrum:
        with ApiClient(ProjectsApi, request) as apiProj:
            prjs.extend(apiProj.search_projects(also_others=Others,
                                                title_filter=filt_title,
                                                instrument_filter=an_instrument,
                                                filter_subset=(filt_subset == 'Y')))
    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())

    # current_user is either an ApiUserWrapper or an anonymous one from flask,
    # but we're in @login_required, so
    user: UserModelWithRights = current_user.api_user

    if Others:
        CanCreate = False
    else:
        CanCreate = 1 in user.can_do

    with ApiClient(TaxonomyTreeApi, request) as apiTaxo:
        status: TaxonomyTreeStatus = apiTaxo.taxa_tree_status()
        try:
            last_refresh = datetime.datetime.strptime(
                status.last_refresh, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            last_refresh = None
    if last_refresh is None or (datetime.datetime.now() - last_refresh).days > 7:
        fashtxt = "Taxonomy synchronization and Ecotaxa version check wasn’t done during the last 7 days, " \
                  "Ask application administrator to do it."  # +str(PDT.lastserverversioncheck_datetime)
        fashtxt += "  <a href='/taxo/browse/' class='btn btn-primary btn-xs'>Synchronize to check Ecotaxa version</a>"
        flash(Markup(fashtxt), 'warning')

    # Construct a mailto: link, in case the instrument is not found
    mailto_instrument = BuildManagersMail(link_text="Not in the list",
                                          subject="Request for adding an instrument to EcoTaxa",
                                          body="""**Information for creation**
                                          
Instrument name:
URL of the description in the BODC L22 vocabulary http://vocab.nerc.ac.uk/collection/L22/current/ :

**Reason for creation**
Explain how widely the instrument is distributed and why it should be added to the standard list.
""")
    if connectPythonToPrime:
        return vue_projects_index(PrjList=prjs, user=user, CanCreate=CanCreate,
                                  filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                                  Others=Others)
    else:  # "historic" code
        return PrintInCharte(
            render_template('project/list.html', PrjList=prjs, CanCreate=CanCreate,
                            filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                            Others=Others, isadmin=2 in user.can_do, mailto_instrument=mailto_instrument,
                            _manager_mail=_manager_mail))


######################################################################################################################


@app.route('/prjothers/')
@login_required
def ProjectsOthers():
    return indexProjects(Others=True)
