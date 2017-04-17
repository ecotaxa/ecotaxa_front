from flask import render_template, g, flash,json,redirect
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
from pathlib import Path
import appli,logging,appli.uvp.sample_import as sample_import
import appli.uvp.database as uvpdatabase,collections,re,csv
from flask_security import login_required
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField

class UvpPrjForm(Form):
    utitle = StringField("UVP Project title")
    rawfolder = StringField("rawfolder")
    ownerid = StringField("Project Owner")
    projid = StringField("Ecotaxa Project")
    instrumtype = StringField("instrumtype")
    op_name = StringField("OP name")
    op_email = StringField("OP email")
    cs_name = StringField("CS name")
    cs_email = StringField("CS email")
    do_name = StringField("DO name")
    do_email = StringField("DO email")
    prj_acronym = StringField("Project acronym")
    cruise = StringField("cruise")
    ship = StringField("ship")
    default_instrumsn = StringField("default instrum SN")
    default_aa = FloatField("default aa",[validators.Optional(strip_whitespace=True)])
    default_exp = FloatField("default exp",[validators.Optional(strip_whitespace=True)])
    default_volimage = FloatField("default volimage",[validators.Optional(strip_whitespace=True)])
    default_depthoffset = FloatField("default depthoffset",[validators.Optional(strip_whitespace=True)])
    prj_info = TextAreaField("prj_info")
    dataportal_desc = TextAreaField("dataportal_desc")


@app.route('/uvp/prjedit/<int:uprojid>',methods=['get','post'])
@login_required
def UVP_prjedit(uprojid):
    g.headcenter="<h3>UVP Project Metadata edition</h3>"
    if uprojid>0:
        model = uvpdatabase.uvp_projects.query.filter_by(uprojid=uprojid).first()
    else:
        model=uvpdatabase.uvp_projects()
        model.uprojid=0
        model.ownerid=current_user.id
    UvpPrjForm.ownerid=SelectField('Project Owner',choices=database.GetAll("SELECT id,name FROM users ORDER BY trim(lower(name))"),coerce=int )
    UvpPrjForm.projid=SelectField('Ecotaxa Project',choices=[(0,'')]+database.GetAll("SELECT projid,concat(title,' (',cast(projid as varchar),')') FROM projects ORDER BY lower(title)"),coerce=int )
    form=UvpPrjForm(request.form,model)
    if gvp('delete')=='Y':
        try:
            db.session.delete(model)
            db.session.commit()
            return redirect("/uvp/prj/")
        except:
            flash("You can delete a project only if doesn't have any data (sample,...)",'error')
            db.session.rollback();
            return redirect("/uvp/prj/" + str(model.uprojid))
    if request.method == 'POST' and form.validate():
        if uprojid==0:
            model.uprojid = None
            db.session.add(model)
        for k,v in form.data.items():
            setattr(model,k,v)
        if model.projid==0: model.projid=None
        db.session.commit()
        return redirect("/uvp/prj/"+str(model.uprojid))
    return PrintInCharte(render_template("uvp/prjedit.html", form=form,prjid=model.uprojid))


@app.route('/uvp/readprojectmeta',methods=['get','post'])
@login_required
def UVP_readprojectmeta():
    res={}
    ServerRoot = Path(app.config['SERVERLOADAREA'])
    DossierUVPPath = ServerRoot / gvg('path')
    DirName = DossierUVPPath.name
    CruiseFile=DossierUVPPath/"config/cruise_info.txt"
    # app.logger.info("CruiseFile=%s",CruiseFile.as_posix())
    if CruiseFile.exists():
        CruiseInfoData = appli.DecodeEqualList(CruiseFile.open('r').read())
        res['op_name']=CruiseInfoData.get('op_name')
        res['op_email'] = CruiseInfoData.get('op_email')
        res['cs_name']=CruiseInfoData.get('cc_name')
        res['cs_email'] = CruiseInfoData.get('cc_email')
        res['prj_info']=CruiseInfoData.get('gen_info')
        res['prj_acronym'] = CruiseInfoData.get('acron')
    # ConfigFile = DossierUVPPath / "config/uvp5_settings/uvp5_configuration_data.txt"
    # if ConfigFile.exists():
    #     ConfigInfoData = appli.DecodeEqualList(ConfigFile.open('r').read())
    #     res['default_aa']=ConfigInfoData.get('aa_calib')
    #     res['default_exp'] = ConfigInfoData.get('exp_calib')
    #     res['default_volimage'] = ConfigInfoData.get('img_vol')

    m = re.search(R"([^_]+)_(.*)", DirName)
    if m.lastindex == 2:
        FichierHeader = DossierUVPPath / "meta" / (m.group(1) + "_header_" + m.group(2) + ".txt")
        res['instrumtype'] = m.group(1)
        m = re.search(R"([^_]+)", m.group(2))
        res['default_instrumsn'] = m.group(1)
        if FichierHeader.exists():
            LstSamples=[]
            with FichierHeader.open() as FichierHeaderHandler:
                F = csv.DictReader(FichierHeaderHandler, delimiter=';')
                for r in F:
                    LstSamples.append(r)
                    # print(LstSamples)
            if len(LstSamples) > 0:
                res['cruise'] = LstSamples[0].get('cruise')
                res['ship'] = LstSamples[0].get('ship')
                res['default_volimage'] = LstSamples[0].get('volimage')
                res['default_aa'] = LstSamples[0].get('aa')
                res['default_exp'] = LstSamples[0].get('exp')
    res['default_depthoffset']=1.2
    return json.dumps(res)

