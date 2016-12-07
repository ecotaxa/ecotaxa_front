from flask import Blueprint, render_template, g, flash,request,url_for,json
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ComputeLimitForImage,ntcv
from flask.ext.security import login_required
from flask_security.decorators import roles_accepted
import os,io

@app.route('/adminothers/edithomemessage', methods=['GET', 'POST'])
@login_required
@roles_accepted(database.AdministratorLabel)
def admin_edithomemessage():
    g.headcenter="Edit home page message<br><a href=/admin>Back to admin home</a>"
    txt="<script src='//cdn.ckeditor.com/4.6.0/full/ckeditor.js'></script>"
    message=""
    NomFichier='appli/static/home/appmanagermsg.html'
    if gvp("msg",None) is not None:
        with open(NomFichier, 'w',encoding='utf-8',newline = "\n") as f:
            f.write(gvp("msg"))
    if os.path.exists(NomFichier):
        with open(NomFichier, 'r',encoding='utf-8') as f:
            message=f.read()
    txt+= """<form action=? method=post>
    Enter bellow the message you want display :
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
    return PrintInCharte(txt)