import json
import re
import sys
import urllib.parse
import urllib.request

from flask import render_template, g, request, flash, make_response
from flask_security.utils import encrypt_password

from appli import app, database, db, gvp, ErrorFormat
from appli import gvg
from appli.back_config import get_country_names
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi


@app.route('/register')
def logincreate():
    # update users set organisation=trim(organisation) where organisation is not null;
    txt = ""
    g.reCaptchaID = app.config.get('RECAPTCHAID')
    return render_template('security/logincreate.html',
                           txt=txt, title="EcoTaxa: Create an account")


@app.route('/dologincreate', methods=['POST'])
def dologincreate():
    txt = ""
    try:
        reCaptchaID = app.config.get('RECAPTCHAID')
        reCaptchaSecret = app.config.get('RECAPTCHASECRET')
        if reCaptchaID:
            response = gvp('g-recaptcha-response')
            remoteip = request.remote_addr
            api_url = "https://www.google.com/recaptcha/api/siteverify?" + \
                      urllib.parse.urlencode({"response": response,
                                              "secret": reCaptchaSecret,
                                              "remoteip": remoteip})

            with urllib.request.urlopen(api_url) as f:
                decoded = json.loads(f.read().decode('utf8'))
                # txt+="<br>decoded="+str(decoded)
                if decoded.get('success') != True:
                    txt += "Captcha error try again\n"
                    app.logger.error("reCaptcha error =" + str(decoded))
        values = {}
        for f in ("firstname", "lastname", "email", "organisation", "country"):
            values[f] = gvp(f).strip()
            if len(values[f]) <= 1:
                txt += "Value for {} is too short\n".format(f)
            if re.search(r'[<"\\]', values[f]) is not None:
                txt += "Forbidden symbols found in field {} \n".format(f)

        ExistingUser = database.users.query.filter_by(email=values["email"]).first()
        if ExistingUser:
            txt += "This email is already used on an {} account\n".format(
                "Active" if ExistingUser.active else "Inactive")
        else:
            FullName = values["firstname"] + " " + values["lastname"]
            ExistingUser = database.users.query.filter_by(name=FullName).first()
            if ExistingUser:
                txt += "This name is already used with the email : {}. If you register with another email, please add add a complement to your name.\n".format(
                    ExistingUser.email)
            else:
                Usr = database.users()
                Usr.name = FullName
                Usr.email = values["email"]
                Usr.password = encrypt_password(gvp("password"))
                Usr.organisation = values["organisation"]
                Usr.country = values["country"]
                Usr.usercreationreason = gvp('usercreationreason').replace("<", '_')
                Usr.active = True
                db.session.add(Usr)
                db.session.commit()
                flash("User created, you can login now !!!", 'success')
                return "<script>window.location='/login'</script>"


    except:
        txt += "User creation error\n"
        app.logger.error("dologincreate error =" + str(sys.exc_info()))
    # update users set organisation=trim(organisation) where organisation is not null;
    if txt:
        txt = ErrorFormat(txt.replace('\n', '\n<br>'))
        txt += "<script>runrecaptcha()</script>"
    # txt+="<br>"+json.dumps(request.form)
    return txt


@app.route('/ajaxorganisationlist')
def ajaxorganisationlist():
    with ApiClient(UsersApi, request) as api:
        lst_orgs = api.search_organizations(name='%' + gvg('term', '') + '%')
    lst_orgs.sort()
    return json.dumps(lst_orgs)


@app.route('/ajaxcountrylist')
def ajaxcountrylist():
    # TODO: Use same method as the form in admin, i.e. full list to browser, once
    q = gvg('term', '')
    Lst = filter(lambda cntry: q in cntry, get_country_names(request))
    res = [{'id': o, 'text': o} for o in Lst]
    res.append({'id': 'Other', 'text': 'Other'})
    return json.dumps({"results": res})


@app.route('/privacy')
def privacy():
    g.google_analytics_id = app.config.get('GOOGLE_ANALYTICS_ID', '')
    return render_template('security/privacy.html', cookieGAOK=g.cookieGAOK)


@app.route('/setprivacy/<choice>')
def setprivacy(choice):
    cookieGAOK = 'Y' if choice == 'Y' else 'N'
    resp = make_response(cookieGAOK)
    if choice == 'D':
        resp.set_cookie('GAOK', cookieGAOK, expires=0)
    else:
        resp.set_cookie('GAOK', cookieGAOK, max_age=3600 * 24 * 365 * 10)  # 10 years
    return resp
