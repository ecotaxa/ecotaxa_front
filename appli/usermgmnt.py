import json

from flask import render_template, g, request, flash, make_response

from appli import app, gvp, ErrorFormat
from appli import gvg
from appli.back_config import get_country_names
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi, UserModelWithRights, ApiException


@app.route("/register")
def logincreate():
    # update users set organisation=trim(organisation) where organisation is not null;
    txt = ""
    reCaptchaID = app.config.get("RECAPTCHAID")
    return render_template(
        "security/logincreate.html",
        txt=txt,
        title="EcoTaxa: Create an account",
        reCaptchaID=reCaptchaID,
    )


@app.route("/dologincreate", methods=["POST"])
def dologincreate():
    reCaptchaID = app.config.get("RECAPTCHAID")
    fields = [
        "firstname",
        "lastname",
        "email",
        "organisation",
        "country",
        "password",
        "usercreationreason",
    ]
    posted = {a_field: gvp(a_field).strip() for a_field in fields}
    # Compose the name
    full_name = posted["firstname"] + " " + posted["lastname"]
    posted["name"] = full_name
    del posted["firstname"]
    del posted["lastname"]
    posted["id"] = -1
    # Ignored on back-end for anonymous, but needed for model conformance
    new_user = UserModelWithRights(**posted)

    # Treat reCAPTCHA
    no_bot = None
    if reCaptchaID:
        response = gvp("g-recaptcha-response")
        remoteip = request.remote_addr
        no_bot = [remoteip, response]
    errs = ""
    try:
        with ApiClient(UsersApi, request) as api:
            user_id = api.create_user(new_user, no_bot=no_bot)
    except ApiException as ae:
        errs = ae.body

    if errs:
        errs = ErrorFormat(errs.replace("\n", "\n<br>"))
        if reCaptchaID:
            errs += "<script>runrecaptcha()</script>"
    else:
        flash("User created, you can login now !!!", "success")
        return "<script>window.location='/login'</script>"
    # txt+="<br>"+json.dumps(request.form)
    return errs


@app.route("/ajaxorganisationlist")
def ajaxorganisationlist():
    with ApiClient(UsersApi, request) as api:
        lst_orgs = api.search_organizations(name="%" + gvg("term", "") + "%")
    lst_orgs.sort()
    return json.dumps(lst_orgs)


@app.route("/ajaxcountrylist")
def ajaxcountrylist():
    # TODO: Use same method as the form in admin, i.e. full list to browser, once
    q = gvg("term", "")
    Lst = filter(lambda cntry: q in cntry, get_country_names(request))
    res = [{"id": o, "text": o} for o in Lst]
    res.append({"id": "Other", "text": "Other"})
    return json.dumps({"results": res})


@app.route("/privacy")
def privacy():
    g.google_analytics_id = app.config.get("GOOGLE_ANALYTICS_ID", "")
    return render_template("security/privacy.html", cookieGAOK=g.cookieGAOK)


@app.route("/setprivacy/<choice>")
def setprivacy(choice):
    cookieGAOK = "Y" if choice == "Y" else "N"
    resp = make_response(cookieGAOK)
    if choice == "D":
        resp.set_cookie("GAOK", cookieGAOK, expires=0)
    else:
        resp.set_cookie("GAOK", cookieGAOK, max_age=3600 * 24 * 365 * 10)  # 10 years
    return resp
