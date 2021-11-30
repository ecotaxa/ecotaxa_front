from flask import render_template
from flask_security import login_required

from ..app import part_app


@part_app.route('/privacy/')
@login_required
def privacy():
    return render_template('part/privacy.html')

@part_app.route('/login')
def login():
    return render_template('part/privacy.html')

@part_app.route('/logout')
def logout():
    return render_template('part/privacy.html')
