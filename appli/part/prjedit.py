from flask import render_template, g, flash,json,redirect
from appli import app,PrintInCharte,database,gvg,gvp,user_datastore,DecodeEqualList,ScaleForDisplay,ntcv
from appli.database import GetAll,GetClassifQualClass,ExecSQL,db,GetAssoc
from flask_login import current_user
from flask import render_template,  flash,request,g
from pathlib import Path
import appli,logging,appli.part.uvp_sample_import as sample_import
import appli.part.database as partdatabase,collections,re,csv
from flask_security import login_required
from wtforms  import Form, BooleanField, StringField, validators,DateTimeField,IntegerField,FloatField,SelectField,TextAreaField

class UvpPrjForm(Form):
    ptitle = StringField("Particle Project title")
    rawfolder = StringField("rawfolder")
    ownerid = StringField("Project Owner name")
    projid = StringField("Ecotaxa Project")
    instrumtype = StringField("Instrument type")
    op_name = StringField("Operator name")
    op_email = StringField("Operator email")
    cs_name = StringField("Chief scientist name")
    cs_email = StringField("Chief scientist email")
    do_name = StringField("Data owner name")
    do_email = StringField("Data owner email")
    prj_acronym = StringField("Project acronym")
    cruise = StringField("Cruise")
    ship = StringField("Ship")
    default_instrumsn = StringField("default instrum SN")
    default_depthoffset = FloatField("Default depth offset",[validators.Optional(strip_whitespace=True)])
    prj_info = TextAreaField("Project information")


@app.route('/part/prjedit/<int:pprojid>',methods=['get','post'])
@login_required
def part_prjedit(pprojid):
    g.headcenter="<h3>Particle Project Metadata edition</h3>"
    if pprojid>0:
        model = partdatabase.part_projects.query.filter_by(pprojid=pprojid).first()
    else:
        model=partdatabase.part_projects()
        model.pprojid=0
        model.ownerid=current_user.id
        model.default_depthoffset=1.2
    UvpPrjForm.ownerid=SelectField('Project Owner',choices=database.GetAll("SELECT id,name FROM users ORDER BY trim(lower(name))"),coerce=int )
    UvpPrjForm.projid=SelectField('Ecotaxa Project',choices=[(0,''),(-1,'Create a new EcoTaxa project')]+database.GetAll("SELECT projid,concat(title,' (',cast(projid as varchar),')') FROM projects ORDER BY lower(title)"),coerce=int )
    form=UvpPrjForm(request.form,model)
    if gvp('delete')=='Y':
        try:
            db.session.delete(model)
            db.session.commit()
            return redirect("/part/prj/")
        except:
            flash("You can delete a project only if doesn't have any data (sample,...)",'error')
            db.session.rollback()
            return redirect("/part/prj/" + str(model.pprojid))
    if request.method == 'POST' and form.validate():
        if pprojid==0:
            model.pprojid = None
            db.session.add(model)
        for k,v in form.data.items():
            setattr(model,k,v)
        if model.projid==0: # 0 permet de dire aucun projet WTForm ne sait pas gére None avec coerce=int
            model.projid=None
        if model.projid == -1: # création d'un projet Ecotaxa
            model.projid = None
            EcotaxaProject=database.Projects()
            EcotaxaProject.title=model.ptitle # Nommé comme le projet Particle
            db.session.add(EcotaxaProject)
            db.session.commit()
            EcotaxaProjectMember=database.ProjectsPriv()
            EcotaxaProjectMember.projid=EcotaxaProject.projid # L'utilisateur courant est Manager de ce projet
            EcotaxaProjectMember.member=current_user.id
            EcotaxaProjectMember.privilege='Manage'
            db.session.add(EcotaxaProjectMember)
            model.projid = EcotaxaProject.projid # On affecte le nouveau projet au projet Particle.
        db.session.commit()
        return redirect("/part/prj/"+str(model.pprojid))
    return PrintInCharte(render_template("part/prjedit.html", form=form, prjid=model.pprojid))


@app.route('/part/readprojectmeta',methods=['get','post'])
@login_required
def part_readprojectmeta():
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
        res['cs_name']=CruiseInfoData.get('cs_name')
        res['cs_email'] = CruiseInfoData.get('cs_email')
        res['do_name']=CruiseInfoData.get('do_name')
        res['do_email'] = CruiseInfoData.get('do_email')
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
    res['default_depthoffset']=1.2
    return json.dumps(res)

