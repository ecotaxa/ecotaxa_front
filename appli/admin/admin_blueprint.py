from typing import Dict, Any

from flask import Blueprint, render_template
from flask_admin import helpers
from flask_admin.helpers import get_url

adminBlueprint: Blueprint = Blueprint(name='admin_custom',
                                      import_name=__name__,
                                      # Register the same base url as flask-admin, the first registered BP takes precedence
                                      url_prefix="/admin/",
                                      template_folder="templates",  # Apparently relative to current path
                                      )

adminBlueprint.warn_on_modifications = True


def render_in_admin_blueprint(template: str, **kwargs: Any) -> str:
    from .admin_from_flask import flaskAdmin
    render_ctx = {
        "admin_base_template": flaskAdmin.index_view.admin.base_template,
        "admin_view": flaskAdmin.index_view,
        "get_url": get_url,
        "h": helpers,
    }
    render_ctx.update(kwargs)
    return render_template(template, **render_ctx)


@adminBlueprint.route('/')
def our_admin_root() -> str:
    return render_in_admin_blueprint('admin2/index_with_others.html')


# Import extra routes
# noinspection PyUnresolvedReferences
from .admin_db import *
# noinspection PyUnresolvedReferences
from .admin_misc import *
