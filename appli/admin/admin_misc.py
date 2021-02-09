import os

from flask_security import login_required
from flask_security.decorators import roles_accepted

from appli import database, gvp
from .admin_blueprint import adminBlueprint as admin_bp, render_in_admin_blueprint


@admin_bp.route('/others/edithomemessage', methods=['GET', 'POST'])
@login_required
@roles_accepted(database.AdministratorLabel)
def admin_edithomemessage():
    txt = "<h4>Edit home page message</h4>"
    txt += "<script src='//cdn.ckeditor.com/4.6.0/full/ckeditor.js'></script>"
    message = ""
    NomFichier = 'appli/static/home/appmanagermsg.html'
    if gvp("msg", None) is not None:
        with open(NomFichier, 'w', encoding='utf-8', newline="\n") as f:
            f.write(gvp("msg"))
    if os.path.exists(NomFichier):
        with open(NomFichier, 'r', encoding='utf-8') as f:
            message = f.read()
    txt += """<form action=? method=post>
    Enter below the message you want display :
    <button type=button class='btn btn-default btn-sm'  onclick='EnableCK()'>Enable HTML Editor</button><br>
    <textarea name=msg style='width:1000px;height:200px;'>{0}</textarea>

    <br><button type=submit class='btn btn-primary'>Save</button>
    </form>
    <script>
    function EnableCK() {{
        CKEDITOR.replace( 'msg' );
    }}
    </script>
    """.format(message)
    return render_in_admin_blueprint("admin2/admin_page.html", body=txt)
