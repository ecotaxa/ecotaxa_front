import flask
from flask import request, render_template, redirect, flash
from flask_security import login_required
from flask_login import current_user
from appli import app, gvp
from appli.gui.commontools import is_partial_request


@app.route("/gui/me/")
@login_required
def my_page():
    return render_template(
        "/v2/me/home.html",
        partial=is_partial_request(request),
    )


@app.route("/gui/me/files/", methods=["GET", "POST"])
@login_required
async def my_files_operations(subdir: str = ""):
    from appli.gui.jobs.main import files_operations

    return files_operations(subdir)


@app.route("/gui/me/profile", methods=["GET", "POST"])
@login_required
def gui_profile() -> str:
    from appli.gui.users.commontools import user_edit, account_page, ACCOUNT_USER_EDIT

    if not current_user:
        return redirect(url_for("gui_home"))
    if request.method == "POST":
        [user, err] = user_edit(current_user.api_user.id, isfrom=None)
        if err != None:
            flash(err, "error")
        else:
            flash("success :  account modified ", "success")
            if gvp("email") != current_user.api_user.email:
                flash("Mail modified - Reconnect please", "info")
                return redirect("/logout")

    return account_page(
        action=ACCOUNT_USER_EDIT,
        usrid=current_user.api_user.id,
        isfrom=None,
        template="v2/me/profile.html",
    )
