# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,database,gvg,gvp
from pathlib import Path
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_security.decorators import roles_accepted
import os,time

# Load default config and override config from an environment variable
# app.config.update(dict(
# DEBUG=True,
# SECRET_KEY='development key',
# USERNAME='admin',
# PASSWORD='default'
# ))
# definition d'un second répertoire traité en statique en plus de static
vaultBP = Blueprint('vault', __name__, static_url_path='/vault', static_folder='../vault')
app.register_blueprint(vaultBP)


@app.route('/')
def index():
    flash('Flash Test Info','info')
    flash('Flash Test Erreur','error')
    flash('Flash Test warning','warning')
    #flash('Flash Message')
    txt = "<a href=/Task/Create/TaskTest>Task/Create/TaskTest</a><br>"
    txt += "<a href=/Task/Create/TaskTaxoSync>Task/Create/TaskTaxoSync</a><br>"
    txt += "<a href="+url_for("test1")+">Test 1</a><br>"
    txt += "<a href="+url_for("test2")+">Test 2 : Layout seul</a><br>"
    txt += "<a href="+url_for("test3")+">Test 3 : Recherche et affichage</a><br>"
    txt += "<a href=/Task/Create/TaskImport?p=1>Create task Import</a><br>"

    return PrintInCharte(txt)
    # return render_template('layout.html',bodycontent=txt)


@app.route('/test1')
def test1():
    txt = """Hello World! <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
            <font color=red><span class="glyphicon glyphicon-search" aria-hidden="true"></span></font>
            <span class="glyphicon glyphicon-user" style="color:blue"></span>
            X<br>

           """
    txt += "Name =" + getattr(current_user,'name',"???")+"<br>"
    txt += "Id ="+str(getattr(current_user,'id',-1))+"<br>"
    txt += ObjectToStr(current_user)
    txt += "<br><img src='vault/test.jpg' width=500>"
    return render_template('layout.html',bodycontent=txt)

@app.route('/test2')
def test2():
    return render_template('layout.html',bodycontent="Contenu du Haut",bodyleft="<b>Contenu de gauche",bodyright="<h1>Contenu de droite")

@app.route('/test3')
def test3():
    left=render_template('search/leftsearchbar.html')
    return render_template('layout.html',bodycontent="Contenu du Haut",bodyleft=left,bodyright="<h1>Contenu de droite</h1> "
    +"<img id=IMG10 data-src='/vault/0000/41201_mini.JPG?1' data-zoom-image='0000/41201.JPG?1 ' width=90 height=150 class='lazy'>"
    # +"<img id=IMG1 src='/vault/0000/41201_mini.JPG?1' data-zoom-image='0000/41201.JPG?1' width=90 height=150 class='lazyx'>"
    +"""  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img id=IMG2 src='/vault/0000/41200.JPG?1' data-zoom-image='0000/41200.JPG?1' class='lazy'>

<script>
    $(document).ready(function() {
        AddZoom($('#IMG2'))
    });
</script>
    """
    # +"\n<script> $('img.lazyx').elevateZoom({scrollZoom : true});</script>"
    # +"\n<script> $('img.lazyx').elevateZoom({ zoomType	: 'lens', lensShape : 'round', lensSize : 200 });</script>"

    # +appli.search.taxo.taxofinal()
    )


@app.route('/testadmin')
@roles_accepted(database.AdministratorLabel)
def testadmin():
    return "Admin OK"


@app.route('/common/ServerFolderSelect')
def ServerFolderSelect():
    ServerRoot=app.config['SERVERLOADAREA']
    res = []
    print(res)
    return render_template('common/fileserverpopup.html',root_elements=res,targetid=gvg("target","ServerPath"))
    return "Admin OK : "+ServerRoot

@app.route('/common/ServerFolderSelectJSON')
def ServerFolderSelectJSON():
    ServerRoot=Path(app.config['SERVERLOADAREA'])
    CurrentPath=ServerRoot
    parent=gvg("id")
    if parent!='#':
        CurrentPath=ServerRoot.joinpath(Path(parent))
    res=[]
    for x in CurrentPath.iterdir():
        rr=x.relative_to(ServerRoot).as_posix()
        rc=x.relative_to(CurrentPath).as_posix()
        if x.is_dir():
            res.append(dict(id=rr,text="<span class=v>"+rc+"</span> <span class='TaxoSel label label-default'>Select</span>",parent=parent,children=True))
        if x.suffix.lower()==".zip":
            fi=os.stat( x.as_posix())
            res.append(dict(id=rr,text="<span class=v>"+"%s (%.1f Mb : %s)"%(rc,fi.st_size/1048576,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fi.st_mtime)))+"</span> <span class='TaxoSel label label-default'>Select</span>",parent=parent,children=False))
    return json.dumps(res);

@app.before_request
def before_request_security():
    # time.sleep(0.1)
    # print("URL="+request.url)
    if "/static" in request.url:
        return
    # print(request.form)
    current_user.is_authenticated()
    g.menu = []
    g.menu.append((url_for("index"),"Home / Explore"))
    g.menu.append(("/prj/","Select Project"))
    if current_user.has_role(database.AdministratorLabel):
        g.menu.append(("/admin","Admin Screen"))
    g.menu.append(("","SEP"))
    g.menu.append(("/change","Change Password"))
    # g.machaine="ABC"+str(current_user)
