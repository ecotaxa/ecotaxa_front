from flask import render_template
from flask_security import login_required

from appli.part.ecopart_blueprint import part_app


@part_app.route('/privacy/')
@login_required
def privacy():
    return render_template('part/privacy.html')
