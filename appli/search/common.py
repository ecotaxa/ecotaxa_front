# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp,database
import psycopg2,psycopg2.extras
from pathlib import Path
import os,time

@app.route('/search/users')
def searchusers():
    term=gvg("q")
    if len(term)<2:
        return "[]"
    term=R"%"+term+R"%"
    res = database.GetAll("SELECT id, name FROM users WHERE  name ILIKE %s and active=true order by name limit 1000", (term,),debug=False)
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])


@app.route("/search/samples")
def searchsamples():
    projid=gvg("projid")
    term="%"+gvg("q")+"%"
    if projid=="":
        return "[]"
    res = database.GetAll("SELECT sampleid, orig_id FROM samples WHERE  projid =%s and orig_id like %s order by orig_id limit 2000", (projid,term),debug=True)
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])

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
    res.sort(key=lambda val: str.upper(val['id']),reverse=False)
    return json.dumps(res);
