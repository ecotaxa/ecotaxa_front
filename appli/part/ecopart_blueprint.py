from flask import Blueprint, g, render_template, request

from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi, UserModelWithRights, ApiException
from .db_utils import GetAssoc2Col
from .remote import EcoTaxaInstance

PART_URL = "/part/"
ECOTAXA_URL = "http://localhost:5001/"
PART_STORAGE_URL = "/vault/"

part_app = Blueprint(name='ecopart',
                     import_name=__name__,
                     # Register the same base url as flask-admin, the first registered BP takes precedence
                     url_prefix=PART_URL,
                     template_folder="templates",  # Apparently relative to current path
                     static_folder="static"
                     )

part_app.warn_on_modifications = True


def part_AddTaskSummaryForTemplate(ecotaxa_if: EcoTaxaInstance):
    """
        Set in global 'g' a structure to show what is currently ongoing on task side.
        @see appli/part/templates/part/layout.html
    """
    ecotaxa_user = ecotaxa_if.get_current_user()
    if ecotaxa_user is not None:
        g.tasksummary = GetAssoc2Col(
            "SELECT taskstate,count(*) from temp_tasks WHERE owner_id=%(owner_id)s group by taskstate"
            , {'owner_id': ecotaxa_user.id})
    # TODO (or not) g.google_analytics_id = app.config.get('GOOGLE_ANALYTICS_ID', '')


def part_PrintInCharte(ecotaxa_if: EcoTaxaInstance, txt, title=None):
    """
    Permet d'afficher un texte (qui ne sera pas echapé dans la charte graphique
    :param txt: Texte à affiche
    :return: Texte rendu
    """
    part_AddTaskSummaryForTemplate(ecotaxa_if)
    if not title:
        title = 'EcoPart'
    return render_template('part/layout.html', bodycontent=txt, title=title)


# Called from main as there is no per-blueprint hook
# @part_app.before_request
def before_part_request():
    """
        Hook before each request.
    """
    g.db = None
    # print(request.form)
    user_is_logged = False
    user_can_create = False
    user_can_administrate = False
    user_can_administrate_users = False
    mru_projects = []
    # TODO: The API will not, in the future, provide current user as EcoPart is separated completely
    with ApiClient(UsersApi, request) as api:
        try:
            user: UserModelWithRights = api.show_current_user()
            user_is_logged = True
            user_can_create = 1 in user.can_do
            user_can_administrate = 2 in user.can_do
            user_can_administrate_users = 3 in user.can_do
            mru_projects = user.last_used_projects
        except ApiException as ae:
            if ae.status in (401, 403):
                pass
    g.cookieGAOK = request.cookies.get('GAOK', '')
    g.menu = []
    g.menu.append((ECOTAXA_URL, "Home"))
    g.menu.append((PART_URL, "Particle Module"))
    if user_is_logged:
        g.menu.append((PART_URL + "prj/", "Particle projects management"))
    g.menu.append(("", "SEP"))
    g.menu.append((PART_URL + "Task/listall", "Task Manager"))

    g.useradmin = user_can_administrate_users
    g.appliadmin = user_can_administrate
    # g.menu.append(("", "SEP"))
    # g.menu.append(("/change", "Change Password"))
