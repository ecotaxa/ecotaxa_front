import datetime

from typing import List

from flask import render_template, flash, session, request, Markup
from flask_security import login_required

from appli import app, PrintInCharte, gvg
######################################################################################################################
from appli.project.main import _manager_mail
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py.api import ProjectsApi, UsersApi, TaxonomyTreeApi
from to_back.ecotaxa_cli_py.models import ProjectModel, UserModelWithRights, TaxonomyTreeStatus, ProjectTaxoStatsModel


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

    with ApiClient(ProjectsApi, request) as apiProj:
        prjs: List[ProjectModel] = apiProj.search_projects(also_others=Others,
                                                           title_filter=filt_title,
                                                           instrument_filter=filt_instrum,
                                                           filter_subset=(filt_subset == 'Y'))
    # Sort for consistency
    prjs.sort(key=lambda prj: prj.title.strip().lower())

    with ApiClient(UsersApi, request) as apiUser:
        user: UserModelWithRights = apiUser.show_current_user()

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

    # https://pynative.com/make-python-class-json-serializable/
    # https://stackoverflow.com/questions/24719592/sending-data-as-json-object-from-python-to-javascript-with-jinja
    # Encode Object into JSON formatted Data using jsonpickle
    # https://www.npmjs.com/package/jsonpickle
    # https://github.com/cuthbertLab/jsonpickleJS/blob/master/tests/testUnpickle.html
    # See the cuthbertLab/music21 and cuthbertLab/music21j projects and especially the .show('vexflow') component for an example of how jsonpickleJS can be extremely useful for projects that have parallel data structures between Python and Javascript.
    # pl:List = [prjs[0]] # use pl instead of prjs if you want to test with only one project

    connectPythonToPrime:bool = False
    #connectPythonToPrime: bool = True
    if connectPythonToPrime:
        # from appli import PrintInCharte_bs5
        from appli import PrintInCharte_bs4
        import jsonpickle  # need of jsonpickle only in that case
        # Do all the "boring" work in the Python part.
        # Basically, everything that cannot be done easily on the HTML side should be done on the Python side ;-)
        # prjs is the list of projects
        # make some minor changes in some project fields
        for oneProj in prjs:
            if oneProj.pctvalidated != None:
                oneProj.pctvalidated = round(oneProj.pctvalidated, 2)
            if oneProj.pctclassified != None:
                oneProj.pctclassified = round(oneProj.pctclassified, 2)
        # Build a list of dictionnaries from this list of projects
        list_of_dicts = [project.to_dict() for project in prjs]
        # Enrich each dictionnary with new fields, like user_Status field
        for oneDict in list_of_dicts:
            oneDict['user_Status'] = findUserStatus(
                oneDict, user.id).value  # .value is important in Python

        # OK, now compute the numbers of taxa
        # 1) Fill a dictionnary with number of taxa for each project
        nb_taxa = {}
        computeNbTaxa(list_of_dicts, nb_taxa)
        # 2) Set this number of taxa to our dictionnary
        for proj in list_of_dicts:
            if proj.get('projid') != None:
                curVal = proj.get('nb_taxa')
                if curVal == None or curVal == 0:
                    proj['nb_taxa'] = nb_taxa.get(proj['projid']) # foresee the case where it is None

        # serialize my list
        varJSON = jsonpickle.encode(list_of_dicts, unpicklable=False)
        # varJSON = json.dumps(list_of_dicts) # ==> says "Object of type UserModel2 is not JSON serializable"
        # send it to HTML Datatable Prime component

        return PrintInCharte_bs4(
            render_template('project/projects_list.html', PrjList=varJSON, CanCreate=CanCreate,
                            filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                            Others=Others, isadmin=2 in user.can_do,
                            _manager_mail=_manager_mail))

        # boostrap 5 to come soon : maybe needs projects_list_bs4.html and projects_list_bs5.html ?
        #return PrintInCharte_bs5(
        #    render_template('project/projects_list.html', PrjList=varJSON, CanCreate=CanCreate,
        #                    filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
        #                    Others=Others, isadmin=2 in user.can_do,
        #                    _manager_mail=_manager_mail))
    else:  # "historic" code
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


def findUserStatus(oneDict: dict, userId: int):
    from enum import Enum

    class userStatus(Enum):  # from lower to higher "rights"
        _NONE = "None"
        _VIEWER = "Viewer"
        _ANNOTATOR = "Annotator"
        _MANAGER = "Manager"

    theUsers = oneDict.get('annotators')
    if theUsers != None:
        for element in theUsers:
            if element.id == userId:
                return userStatus._ANNOTATOR
    theUsers = oneDict.get('managers')
    if theUsers != None:
        for element in theUsers:
            if element.id == userId:
                return userStatus._MANAGER
    theUsers = oneDict.get('viewers')
    if theUsers != None:
        for element in theUsers:
            if element.id == userId:
                return userStatus._VIEWER
    return userStatus._NONE


MAX_REQUEST_LENGTH: int = 2000
SEPARATOR: str = "|"


def computeNbTaxa(theProjects: List[dict], nb_taxa: dict):
    try:
        projectIDlist: str = ""
        for oneProject in theProjects:
            pid = oneProject.get('projid')
            if (pid != None):
                projectIDlist += str(pid) + SEPARATOR
        # if it's a long project list, treat it in a loop
        if len(projectIDlist) > MAX_REQUEST_LENGTH:
            setProjectsAllCategories(projectIDlist, theProjects, nb_taxa)
        else:  # short project list
            setProjectsCategories(projectIDlist, theProjects, nb_taxa)
    except:
        # TODO : special case inside setProjectsCategories() function (regarding API call project_set_get_stats)
        print("Something went wrong when computing the projects numbers of taxa")
        nb_taxa = {}

def setProjectsAllCategories(projectIDlist: str, theProjects: List[dict], nb_taxa: dict):
    import math
    nbPackets: int = math.floor(len(projectIDlist) / MAX_REQUEST_LENGTH) + 1
    oldSmallStep: int = 0
    smallStep: int = MAX_REQUEST_LENGTH
    # Cut the projectIDlist in several pieces, and call setProjectsCategories for each one of them
    for curPacket in range(nbPackets):
        while smallStep < len(projectIDlist):
            # In JS it was for (; smallStep < projectIDlist.length; smallStep++)
            if projectIDlist[smallStep] == SEPARATOR:
                break  # found the separator, in order to get a full projectID
            smallStep += 1

        subProjectIDlist: str = projectIDlist[oldSmallStep:smallStep]
        setProjectsCategories(subProjectIDlist, theProjects, nb_taxa)

        oldSmallStep = smallStep + 1  # + 1 to swallow the separator
        smallStep += MAX_REQUEST_LENGTH
        if smallStep > len(projectIDlist):
            smallStep = len(projectIDlist)


def setProjectsCategories(projectIDlist: str, theProjects: List[dict], nb_taxa: dict):
    if projectIDlist != "":
        # initialize the nb_taxa dictionnary with default 0 values
        for proj in theProjects:
            nb_taxa.setdefault(proj['projid'],  0)

        with ApiClient(ProjectsApi, request) as apiProj:
            # We have an Array of ProjectTaxoStatsModel : projTaxa
            projTaxa: List[ProjectTaxoStatsModel] = apiProj.project_set_get_stats(
                projectIDlist, taxa_ids="all")
            # each time there is a reference of a taxon to the project, we increment the count
            for projTaxon in projTaxa:
                val: int = nb_taxa.get(projTaxon.projid)
                if (val == None):
                    val = 0
                nb_taxa[projTaxon.projid] = val + 1
