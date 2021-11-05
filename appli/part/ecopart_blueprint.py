from flask import Blueprint

part_app = Blueprint(name='ecopart',
                     import_name=__name__,
                     # Register the same base url as flask-admin, the first registered BP takes precedence
                     url_prefix="/part/",
                     template_folder="toto/templates",  # Apparently relative to current path
                     static_folder="static"
                     )

part_app.warn_on_modifications = True
