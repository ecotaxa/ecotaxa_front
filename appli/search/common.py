# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, flash,request,url_for,json
from flask.ext.login import current_user
from appli import app,ObjectToStr,PrintInCharte,gvg,db,gvp
import psycopg2,psycopg2.extras


def GetAll(sql,params=None,debug=False):
    cur = db.engine.raw_connection().cursor()
    try:
        if debug:
            app.logger.debug("GetAll SQL = %s",sql)
        cur.execute(sql,params)
        res = cur.fetchall()
    finally:
        cur.close()  #TODO ajouter un Finaly
    return res


@app.route('/search/users')
def searchusers():
    term=gvg("q")
    if len(term)<2:
        return "[]"
    term=R"%"+term+R"%"
    res = GetAll("SELECT id, name FROM users WHERE  name ILIKE %s and active=true order by name limit 1000", (term,),debug=True)
    return json.dumps([dict(id=r[0],text=r[1]) for r in res])

