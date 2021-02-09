from flask import Blueprint, render_template
from flask_admin import helpers
from flask_admin.helpers import get_url

adminBlueprint = Blueprint(name='admin_custom',
                           import_name=__name__,
                           # Register the same base url as flask-admin, the first registered BP takes precedence
                           url_prefix="/admin/",
                           template_folder="templates",  # Apparently relative to current path
                           )

adminBlueprint.warn_on_modifications = True


def render_in_admin_blueprint(template, **kwargs):
    from .admin_from_flask import flaskAdmin
    render_ctx = {
        "admin_base_template": flaskAdmin.index_view.admin.base_template,
        "admin_view": flaskAdmin.index_view,
        "get_url": get_url,
        "h": helpers,
    }
    render_ctx.update(kwargs)
    return render_template(template, **render_ctx)


def GetAdminList():
    from appli.database import GetAll
    LstUsers = GetAll("""select name||'('||email||')' nom from users u
                        join users_roles r on u.id=r.user_id where r.role_id=1""")
    return ", ".join([r[0] for r in LstUsers])


@adminBlueprint.route('/')
def our_admin_root():
    return render_in_admin_blueprint('admin2/index_with_others.html',
                                     GetAdminList=GetAdminList)


# Import extra routes
# noinspection PyUnresolvedReferences
from .admin_db import *
# noinspection PyUnresolvedReferences
from .admin_misc import *
