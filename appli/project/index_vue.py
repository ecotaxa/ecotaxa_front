from typing import List, Optional, Dict

import jsonpickle  # need of jsonpickle only in that case
from flask import render_template, request

from appli import AddJobsSummaryForTemplate, ApiClient
from appli.project.main import _manager_mail
from to_back.ecotaxa_cli_py import UserModelWithRights, ProjectsApi, ProjectTaxoStatsModel

from enum import Enum


class userStatus(Enum):  # from lower to higher "rights"
    _NONE = "None"
    _VIEWER = "Viewer"
    _ANNOTATOR = "Annotator"
    _MANAGER = "Manager"


def findUserStatus(oneDict: dict, userId: int):
    theUsers = oneDict.get('annotators')
    if theUsers is not None:
        for element in theUsers:
            if element.id == userId:
                return userStatus._ANNOTATOR
    theUsers = oneDict.get('managers')
    if theUsers is not None:
        for element in theUsers:
            if element.id == userId:
                return userStatus._MANAGER
    theUsers = oneDict.get('viewers')
    if theUsers is not None:
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
        nb_taxa.clear()


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
            nb_taxa.setdefault(proj['projid'], 0)

        with ApiClient(ProjectsApi, request) as apiProj:
            # We have an Array of ProjectTaxoStatsModel : projTaxa
            projTaxa: List[ProjectTaxoStatsModel] = apiProj.project_set_get_stats(
                projectIDlist, taxa_ids="all")
            # each time there is a reference of a taxon to the project, we increment the count
            for projTaxon in projTaxa:
                val: Optional[int] = nb_taxa.get(projTaxon.projid)
                if val is None:
                    val = 0
                nb_taxa[projTaxon.projid] = val + 1


def PrintInCharte_bs5(txt, title=None) -> str:  # for bootstrap 5
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddJobsSummaryForTemplate()
    if not title:
        title = 'EcoTaxa'
    return render_template('layout_bs5.html', bodycontent=txt, title=title)


# https://pynative.com/make-python-class-json-serializable/
# https://stackoverflow.com/questions/24719592/sending-data-as-json-object-from-python-to-javascript-with-jinja
# Encode Object into JSON formatted Data using jsonpickle
# https://www.npmjs.com/package/jsonpickle
# https://github.com/cuthbertLab/jsonpickleJS/blob/master/tests/testUnpickle.html
# See the cuthbertLab/music21 and cuthbertLab/music21j projects and especially the .show('vexflow') component for an example of how jsonpickleJS can be extremely useful for projects that have parallel data structures between Python and Javascript.
# pl:List = [prjs[0]] # use pl instead of prjs if you want to test with only one project

def vue_projects_index(PrjList, user: UserModelWithRights, CanCreate, filt_title, filt_subset,
                       filt_instrum, Others) -> str:
    # from appli import PrintInCharte_bs4
    # Do all the "boring" work in the Python part.
    # Basically, everything that cannot be done easily on the HTML side should be done on the Python side ;-)
    # prjs is the list of projects
    # make some minor changes in some project fields
    for oneProj in PrjList:
        if oneProj.pctvalidated is not None:
            oneProj.pctvalidated = round(oneProj.pctvalidated, 2)
        if oneProj.pctclassified is not None:
            oneProj.pctclassified = round(oneProj.pctclassified, 2)
    # Build a list of dictionnaries from this list of projects
    list_of_dicts = [project.to_dict() for project in PrjList]
    # Enrich each dictionary with new fields, like user_Status field
    for oneDict in list_of_dicts:
        oneDict['user_Status'] = findUserStatus(oneDict, user.id).value  # .value is important in Python

    # OK, now compute the numbers of taxa
    # 1) Fill a dictionary with number of taxa for each project
    nb_taxa: Dict[int, int] = dict()
    computeNbTaxa(list_of_dicts, nb_taxa)
    # 2) Set this number of taxa to our dictionnary
    for proj in list_of_dicts:
        if proj.get('projid') is not None:
            curVal = proj.get('nb_taxa')
            if curVal is None or curVal == 0:
                proj['nb_taxa'] = nb_taxa.get(proj['projid'])  # foresee the case where it is None

    # serialize my list
    varJSON = jsonpickle.encode(list_of_dicts, unpicklable=False)
    # varJSON = json.dumps(list_of_dicts) # ==> says "Object of type UserModel2 is not JSON serializable"
    # send it to HTML Datatable Prime component

    # return PrintInCharte_bs4(
    #    render_template('project/projects_list.html', PrjList=varJSON, CanCreate=CanCreate,
    #                    filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
    #                    Others=Others, isadmin=2 in user.can_do,
    #                    _manager_mail=_manager_mail))

    return PrintInCharte_bs5(
        render_template('project/projects_list_bs5.html', PrjList=varJSON, CanCreate=CanCreate,
                        filt_title=filt_title, filt_subset=filt_subset, filt_instrum=filt_instrum,
                        Others=Others, isadmin=2 in user.can_do,
                        _manager_mail=_manager_mail))


def PrintInCharte_bs4(txt, title=None):  # for bootstrap 4
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    AddJobsSummaryForTemplate()
    if not title:
        title = 'EcoTaxa'
    return render_template('layout_bs4.html', bodycontent=txt, title=title)
