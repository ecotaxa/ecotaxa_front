from flask import render_template, g, flash,json,redirect
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
import appli,logging,appli.part.uvp_sample_import as sample_import
import appli.part.database as partdatabase
from flask_security import login_required
# from flask_wtf import Form
# from wtforms.ext.sqlalchemy.orm import model_form
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,TextAreaField

class UvpSampleForm(Form):
    pprojid = StringField("UVP Project ID",[validators.required()])
    profileid = StringField("Profile ID",[validators.required()])
    filename = StringField("filename", [validators.required(),validators.Length(min=5)])
    sampleid = IntegerField("Ecotaxa SampleID",[validators.Optional(strip_whitespace=True)])
    latitude = FloatField("latitude",[validators.Optional(strip_whitespace=True)])
    longitude = FloatField("longitude",[validators.Optional(strip_whitespace=True)])
    organizedbydeepth = BooleanField("organizedbydeepth")
    histobrutavailable = BooleanField("histobrutavailable")
    qualitytaxo = StringField("qualitytaxo")
    qualitypart = StringField("qualitypart")
    daterecalculhistotaxo = DateTimeField("daterecalculhistotaxo",[validators.Optional(strip_whitespace=True)])
    winddir = IntegerField("winddir",[validators.Optional(strip_whitespace=True)])
    winspeed = IntegerField("winspeed",[validators.Optional(strip_whitespace=True)])
    seastate = IntegerField("seastate",[validators.Optional(strip_whitespace=True)])
    nebuloussness = StringField("nebuloussness")
    comment = StringField("comment")
    stationid = StringField("stationid")
    firstimage = IntegerField("firstimage",[validators.Optional(strip_whitespace=True)])
    lastimg = IntegerField("lastimg",[validators.Optional(strip_whitespace=True)])
    lastimgused = IntegerField("lastimgused",[validators.Optional(strip_whitespace=True)])
    bottomdepth = IntegerField("bottomdepth",[validators.Optional(strip_whitespace=True)])
    yoyo = BooleanField("yoyo")
    sampledate = DateTimeField("sampledate",[validators.Optional(strip_whitespace=True)])
    ctd_desc = TextAreaField("ctd_desc")
    ctd_origfilename = StringField("ctd_origfilename")
    ctd_import_name = StringField("ctd_import_name")
    ctd_import_email = StringField("ctd_import_email")
    ctd_import_datetime = DateTimeField("ctd_import_datetime",[validators.Optional(strip_whitespace=True)])
    ctd_status = StringField("ctd_status")
    instrumsn = StringField("instrumsn")
    acq_aa = FloatField("acq_aa",[validators.Optional(strip_whitespace=True)])
    acq_exp = FloatField("acq_exp",[validators.Optional(strip_whitespace=True)])
    acq_volimage = FloatField("acq_volimage",[validators.Optional(strip_whitespace=True)])
    acq_depthoffset = FloatField("acq_depthoffset",[validators.Optional(strip_whitespace=True)])
    acq_pixel = FloatField("acq_pixel",[validators.Optional(strip_whitespace=True)])
    acq_shutterspeed = IntegerField("acq_shutterspeed",[validators.Optional(strip_whitespace=True)])
    acq_smzoo = IntegerField("acq_smzoo",[validators.Optional(strip_whitespace=True)])
    acq_exposure = IntegerField("acq_exposure",[validators.Optional(strip_whitespace=True)])
    acq_gain = IntegerField("acq_gain",[validators.Optional(strip_whitespace=True)])
    acq_filedescription = StringField("acq_filedescription",[validators.Optional(strip_whitespace=True)])
    acq_eraseborder = IntegerField("acq_eraseborder",[validators.Optional(strip_whitespace=True)])
    acq_tasktype = IntegerField("acq_tasktype",[validators.Optional(strip_whitespace=True)])
    acq_threshold = IntegerField("acq_threshold",[validators.Optional(strip_whitespace=True)])
    acq_choice = IntegerField("acq_choice",[validators.Optional(strip_whitespace=True)])
    acq_disktype = IntegerField("acq_disktype",[validators.Optional(strip_whitespace=True)])
    acq_smbase = IntegerField("acq_smbase",[validators.Optional(strip_whitespace=True)])
    acq_ratio = IntegerField("acq_ratio",[validators.Optional(strip_whitespace=True)])
    acq_descent_filter = BooleanField("acq_descent_filter",[validators.Optional(strip_whitespace=True)])
    acq_presure_gain = FloatField("acq_presure_gain",[validators.Optional(strip_whitespace=True)])
    acq_xsize = IntegerField("acq_xsize",[validators.Optional(strip_whitespace=True)])
    acq_ysize = IntegerField("acq_ysize",[validators.Optional(strip_whitespace=True)])
    acq_barcode = StringField("acq_barcode")
    proc_datetime = DateTimeField("proc_datetime",[validators.Optional(strip_whitespace=True)])
    proc_gamma = FloatField("proc_gamma",[validators.Optional(strip_whitespace=True)])
    proc_soft = StringField("proc_soft")
    op_sample_name = StringField("op_sample_name")
    op_sample_email = StringField("op_sample_email")

@app.route('/part/sampleedit/<int:psampleid>',methods=['get','post'])
@login_required
def part_sampleedit(psampleid):
    model = partdatabase.part_samples.query.filter_by(psampleid=psampleid).first()
    form=UvpSampleForm(request.form,model)
    if gvp('delete')=='Y':
        for t in ('part_histopart_reduit','part_histopart_det','part_histocat','part_histocat_lst','part_ctd'):
            database.ExecSQL("delete from "+t+" where psampleid="+str(model.psampleid))
        db.session.delete(model)
        db.session.commit()
        return redirect("/part/prj/" + str(model.pprojid))
    if request.method == 'POST' and form.validate():
        for k,v in form.data.items():
            setattr(model,k,v)
        db.session.commit()
        return redirect("/part/prj/"+str(model.pprojid))
    return PrintInCharte(render_template("part/sampleedit.html", form=form, prjid=model.pprojid, psampleid=model.psampleid))
