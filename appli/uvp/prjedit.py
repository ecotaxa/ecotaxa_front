from flask import render_template, g, flash,json,redirect
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
import appli,logging,appli.uvp.sample_import as sample_import
import appli.uvp.database as uvpdatabase,collections
from flask_security import login_required
# from flask_wtf import Form
# from wtforms.ext.sqlalchemy.orm import model_form
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField

class UvpPrjForm(Form):
    utitle = StringField("utitle")
    rawfolder = StringField("rawfolder")
    ownerid = StringField("ownerid")
    projid = StringField("projid")
    instrumtype = StringField("instrumtype")
    op_name = StringField("op_name")
    op_email = StringField("op_email")
    cs_name = StringField("cs_name")
    cs_email = StringField("cs_email")
    do_name = StringField("do_name")
    do_email = StringField("do_email")
    prj_acronym = StringField("prj_acronym")
    cruise = StringField("cruise")
    ship = StringField("ship")
    default_instrumsn = StringField("default_instrumsn")
    default_aa = FloatField("default_aa",[validators.Optional(strip_whitespace=True)])
    default_exp = FloatField("default_exp",[validators.Optional(strip_whitespace=True)])
    default_volimage = FloatField("default_volimage",[validators.Optional(strip_whitespace=True)])
    default_depthoffset = FloatField("default_depthoffset",[validators.Optional(strip_whitespace=True)])
    prj_info = TextAreaField("prj_info")
    dataportal_desc = TextAreaField("dataportal_desc")


@app.route('/uvp/prjedit/<int:uprojid>',methods=['get','post'])
@login_required
def UVP_prjedit(uprojid):
    model = uvpdatabase.uvp_projects.query.filter_by(uprojid=uprojid).first()
    UvpPrjForm.ownerid=SelectField('Project Owner',choices=database.GetAll("SELECT id,name FROM users ORDER BY lower(name)"),coerce=int )
    UvpPrjForm.projid=SelectField('Ecotaxa Project',choices=database.GetAll("SELECT projid,concat(title,' (',cast(projid as varchar),')') FROM projects ORDER BY lower(title)"),coerce=int )
    form=UvpPrjForm(request.form,model)
    if request.method == 'POST' and form.validate():
        for k,v in form.data.items():
            setattr(model,k,v)
        db.session.commit()
        return redirect("/uvp/prj/"+str(model.uprojid))
    return PrintInCharte(render_template("uvp/prjedit.html", form=form,prjid=model.uprojid))
