
from urls import ECOTAXA_URL, PART_URL, PART_STORAGE_URL

from flask import Flask, Blueprint
from flask import g, request
from flask_sqlalchemy import SQLAlchemy

from remote import EcoTaxaInstance
part_app = Flask('part_app')  # Il faut donner le nom du module, le premier paramètre n'est pas libre _du tout_

part_app.config.from_pyfile('config.cfg')
part_app.warn_on_modifications = True

part_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# expire_on_commit évite d'avoir des select quand on manipule les objets aprés un commit.
db = SQLAlchemy(part_app, session_options={'expire_on_commit': True})

if 'PYTHONEXECUTABLE' in part_app.config:
    part_app.PythonExecutable = part_app.config['PYTHONEXECUTABLE']
else:
    part_app.PythonExecutable = "TBD"

vaultBP = Blueprint('vault', __name__,
                    static_url_path='/vault',
                    static_folder='../vault')
part_app.register_blueprint(vaultBP)


@part_app.before_request
def before_part_request():
    """
        Hook before each request.
    """
    g.db = None
    g.ecotaxa_if = EcoTaxaInstance(ECOTAXA_URL, request)
    # print(request.form)
    user_is_logged = False
    user_can_create = False
    user_can_administrate = False
    user_can_administrate_users = False
    user = g.ecotaxa_if.get_current_user()
    if user is not None:
        user_is_logged = True
        user_can_administrate = 2 in user.can_do
        user_can_administrate_users = 3 in user.can_do
    g.user = user
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


def JinjaFormatDateTime(d, format='%Y-%m-%d %H:%M:%S'):
    if d is None:
        return ""
    return d.strftime(format)


part_app.jinja_env.filters['datetime'] = JinjaFormatDateTime

# Importation des vues
from .views import * # noqa
from .tasks import *  # noqa
