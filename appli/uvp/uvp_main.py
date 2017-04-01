from flask import render_template, g, flash,json
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv


@app.route('/uvp/')
def indexUVP():
    return PrintInCharte(
        render_template('uvp/index.html' ))
