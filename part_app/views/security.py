from flask import redirect, flash

from ..app import part_app
from ..http_utils import gvp
from ..remote import log_in_ecotaxa, ECOTAXA_COOKIE


# @part_app.route('/privacy/', methods=['POST'])
# def privacy():
#     return render_template('part/privacy.html')

@part_app.route('/login', methods=['POST'])
def login():
    email = gvp("email")
    password = gvp("password")
    token = log_in_ecotaxa(email, password)
    response = redirect('/')
    if token is not None:
        response.set_cookie(ECOTAXA_COOKIE, token)
    else:
        flash("Could not log in", 'error')
    return response


@part_app.route('/logout', methods=['GET'])
def logout():
    response = redirect('/')
    response.set_cookie(ECOTAXA_COOKIE, '')
    return response
