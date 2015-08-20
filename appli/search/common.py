# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp,database
import psycopg2,psycopg2.extras

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

