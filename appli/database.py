# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from appli import db,app,g
from flask_security import  UserMixin, RoleMixin
from flask_login import current_user
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR,TIMESTAMP,REAL
from sqlalchemy import Index,Sequence,func
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import foreign,remote
import json,psycopg2.extras,datetime,os,time

AdministratorLabel="Application Administrator"
UserAdministratorLabel="Users Administrator"
ParticleProjectCreatorLabel="Particle module project creator"

ClassifQual={'P':'predicted','D':'dubious','V':'validated'}
DayTimeList={'A':'Dawn','D':'Day','U':'Dust','N':'Night'}
ClassifQualRevert={}
for(k,v) in ClassifQual.items():
    ClassifQualRevert[v]=k
def GetClassifQualClass(q):
    if q in ClassifQual:
        return 'status-'+ClassifQual[q]
    return 'status-unknown'

users_roles = db.Table('users_roles',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id'), primary_key=True),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'), primary_key=True))

class roles(db.Model, RoleMixin ):
    id = db.Column(db.Integer(), primary_key=True)  #,db.Sequence('seq_roles')
    name = db.Column(db.String(80), unique=True,nullable=False)
#    description = db.Column(db.String(255))
    def __str__(self):
        return self.name

class users(db.Model, UserMixin):
    id = db.Column(db.Integer,db.Sequence('seq_users'), primary_key=True)
    email = db.Column(db.String(255), unique=True,nullable=False)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255),nullable=False)
    organisation = db.Column(db.String(255))
    active = db.Column(db.Boolean(),default=True)
    roles = db.relationship('roles', secondary=users_roles,
                            backref=db.backref('users', lazy='dynamic')) #
    preferences= db.Column(db.String(40000))
    def __str__(self):
        return "{0} ({1})".format(self.name,self.email)
    def GetPref(self,prjid,name,defval):
        try:
            prjid = str(prjid)
            tmp=json.loads(self.preferences)
            if prjid not in tmp:
                return defval
            if isinstance(defval, int):
                return int(tmp[prjid].get(name,defval))
            if isinstance(defval, (float)):
                return float(tmp[prjid].get(name,defval))
            return tmp[prjid].get(name,defval)
        except:
            return defval
    def SetPref(self,prjid,name,newval):
        try:
            prjid=str(prjid)
            tmp=json.loads(self.preferences)
            if prjid not in tmp:
                tmp[prjid] = {}
            if tmp.get(name,-99999)==newval:
                return 0# déjà la bonne valeur donc il n'y a rien à faire
        except:
            tmp={}
        if prjid not in tmp:
            tmp[prjid]={}
        tmp[prjid][name]=newval
        tmp[prjid]['ts']=time.time()
        if len(tmp)>75: # si des settings pour plus de 50 projets on ne garde que les 25 plus recents
            newpref={k:v for k,v in tmp.items() if isinstance(v,dict) and 'ts' in v}
            ChronoSorted=[[k,v['ts']] for k,v in newpref.items()]
            sorted(ChronoSorted,key=lambda r:r[1],reverse=True)
            tmp={}
            for id,ts in ChronoSorted[0:50]:
                tmp[id]=newpref[id]
        self.preferences=json.dumps(tmp)
        return 1

class Taxonomy(db.Model):
    __tablename__ = 'taxonomy'
    id  = db.Column(INTEGER,db.Sequence('seq_taxonomy'), primary_key=True)
    parent_id  = db.Column(INTEGER)
    name   = db.Column(VARCHAR(100),nullable=False)
    id_source  = db.Column(VARCHAR(20))
    nbrobj  = db.Column(INTEGER)
    nbrobjcum  = db.Column(INTEGER)
    def __str__(self):
        return "{0} ({1})".format(self.name,self.id)
Index('IS_TaxonomyParent',Taxonomy.__table__.c.parent_id)
Index('IS_TaxonomySource',Taxonomy.__table__.c.id_source)
Index('IS_TaxonomyNameLow',func.lower(Taxonomy.__table__.c.name))

class Projects(db.Model):
    __tablename__ = 'projects'
    projid  = db.Column(INTEGER,db.Sequence('seq_projects'), primary_key=True)
    title   = db.Column(VARCHAR(255),nullable=False)
    visible = db.Column(db.Boolean(),default=True)
    status = db.Column(VARCHAR(40),default="Annotate") # Annotate, ExploreOnly, Annotate No Prediction
    mappingobj   = db.Column(VARCHAR)
    mappingsample   = db.Column(VARCHAR)
    mappingacq   = db.Column(VARCHAR)
    mappingprocess   = db.Column(VARCHAR)
    objcount = db.Column(DOUBLE_PRECISION)
    pctvalidated = db.Column(DOUBLE_PRECISION)
    pctclassified = db.Column(DOUBLE_PRECISION)
    classifsettings  = db.Column(VARCHAR) # Settings for Automatic classification.
    initclassiflist  = db.Column(VARCHAR) # Initial list of categories
    classiffieldlist  = db.Column(VARCHAR) # Fields available on sort & displayed field of Manual classif screen
    popoverfieldlist  = db.Column(VARCHAR) # Fields available on popover of Manual classif screen
    comments  = db.Column(VARCHAR)
    projtype  = db.Column(VARCHAR(50))
    fileloaded  = db.Column(VARCHAR)
    rf_models_used = db.Column(VARCHAR)
    cnn_network_id=db.Column(VARCHAR(50))

    def __str__(self):
        return "{0} ({1})".format(self.title,self.projid)
    def CheckRight(self,Level,userid=None): # Level -1=Read public, 0 = Read, 1 = Annotate, 2 = Admin . userid=None = current user
        # pp=self.projmembers.filter(member=userid).first()
        if userid is None:
            u=current_user
            userid=getattr(u,'id',None)
            if userid is None: # correspond à anonymous
                if Level<=-1 and self.visible: # V1.2 tout projet visible est visible par tous
                    return True
                return False
        else:
            u=users.query.filter_by(id=userid).first()
        if len([x for x in u.roles if x=='Application Administrator'])>0:
            return True # Admin à tous les droits
        pp=[x for x in self.projmembers if x.member==userid]
        if len(pp)==0: # pas de privileges pour cet utilisateur
            if Level <= -1 and self.visible:  # V1.2 tout projet visible est visible par tous
                return True
            return False
        pp=pp[0] #on recupere la premiere ligne seulement.
        if pp.privilege=='Manage':
            return True
        if pp.privilege=='Annotate' and Level<=1:
            return True
        if Level<=0:
            return True
        return False
    def GetFirstManager(self):
        # retourne le utilisateur créé avec un privilege Manage
        lst=sorted([(r.id,r.memberrel.email,r.memberrel.name) for r in self.projmembers if r.privilege=='Manage'],key=lambda r: r[0])
        if lst:
            return lst[0]
        return None
    def GetFirstManagerMailto(self):
        r=self.GetFirstManager()
        if r:
            return "<a href='mailto:{1}'>{2} ({1})</a>".format(*r)
        return ""


class ProjectsPriv(db.Model):
    __tablename__ = 'projectspriv'
    id = db.Column(db.Integer,db.Sequence('seq_projectspriv'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid',ondelete="CASCADE"),nullable=False)
    member = db.Column(db.Integer,db.ForeignKey('users.id'))
    privilege = db.Column(VARCHAR(255),nullable=False)
    memberrel=db.relationship("users")
    refproject=db.relationship('Projects',backref=db.backref('projmembers',cascade="all, delete-orphan", single_parent=True)) # ,cascade='delete'

    def __str__(self):
        return "{0} ({1})".format(self.member,self.privilege)
Index('IS_ProjectsPriv',ProjectsPriv.__table__.c.projid,ProjectsPriv.__table__.c.member, unique=True)

class ProjectsTaxoStat(db.Model):
    __tablename__ = 'projects_taxo_stat'
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid',ondelete="CASCADE"), primary_key=True)
    id  = db.Column(INTEGER, primary_key=True)
    nbr  = db.Column(INTEGER)
    nbr_v  = db.Column(INTEGER)
    nbr_d  = db.Column(INTEGER)
    nbr_p  = db.Column(INTEGER)


class Samples(db.Model):
    __tablename__ = 'samples'
    sampleid = db.Column(BIGINT,db.Sequence('seq_samples'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    dataportal_descriptor= db.Column(VARCHAR(8000))
    def __str__(self):
        return "{0} ({1})".format(self.orig_id,self.processid)
for i in range(1,31):
    setattr(Samples,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_SamplesProject',Samples.__table__.c.projid)

class Acquisitions(db.Model):
    __tablename__ = 'acquisitions'
    acquisid = db.Column(BIGINT,db.Sequence('seq_acquisitions'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    instrument = db.Column(VARCHAR(255))
    def __str__(self):
        return "{0} ({1})".format(self.orig_id,self.processid)
for i in range(1,31):
    setattr(Acquisitions,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_AcquisitionsProject',Acquisitions.__table__.c.projid)

class Process(db.Model):
    __tablename__ = 'process'
    processid = db.Column(BIGINT,db.Sequence('seq_process'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    def __str__(self):
        return "{0} ({1})".format(self.orig_id,self.processid)
for i in range(1,31):
    setattr(Process,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_ProcessProject',Process.__table__.c.projid)

class Objects(db.Model):
    __tablename__ = 'obj_head'
    objid = db.Column(BIGINT,db.Sequence('seq_objects'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'),nullable=False)
    project=db.relationship("Projects")
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    objdate = db.Column(DATE)
    objtime = db.Column(TIME)
    depth_min = db.Column(FLOAT)
    depth_max = db.Column(FLOAT)
    images=db.relationship("Images")
    classif_id = db.Column(INTEGER)
    classif=db.relationship("Taxonomy",primaryjoin="Taxonomy.id==Objects.classif_id",foreign_keys="Taxonomy.id" ,uselist=False,)
    classif_qual = db.Column(CHAR(1))
    classif_who = db.Column(db.Integer,db.ForeignKey('users.id'))
    classiffier=db.relationship("users",primaryjoin="users.id==Objects.classif_who",foreign_keys="users.id" ,uselist=False,)
    classif_when = db.Column(TIMESTAMP)
    classif_auto_id = db.Column(INTEGER)
    classif_auto_score = db.Column(DOUBLE_PRECISION)
    classif_auto_when = db.Column(TIMESTAMP)
    classif_auto=db.relationship("Taxonomy",primaryjoin="Taxonomy.id==foreign(Objects.classif_auto_id)",uselist=False,)
    classif_crossvalidation_id = db.Column(INTEGER)
    img0id = db.Column(BIGINT)
    img0=db.relationship("Images",foreign_keys="Images.objid")
    imgcount = db.Column(INTEGER)
    complement_info = db.Column(VARCHAR)
    similarity = db.Column(DOUBLE_PRECISION)
    sunpos = db.Column(CHAR(1))  # position du soleil
    random_value = db.Column(INTEGER)
    sampleid = db.Column(INTEGER,db.ForeignKey('samples.sampleid'))
    sample=db.relationship("Samples")
    acquisid = db.Column(INTEGER,db.ForeignKey('acquisitions.acquisid'))
    acquis=db.relationship("Acquisitions")
    processid = db.Column(INTEGER,db.ForeignKey('process.processid'))
    processrel=db.relationship("Process")

class ObjectsFields(db.Model):
    __tablename__ = 'obj_field'
    objfid = db.Column(BIGINT,db.ForeignKey('obj_head.objid',ondelete="CASCADE"), primary_key=True)
    objhrel=db.relationship("Objects",foreign_keys="Objects.objid",primaryjoin="ObjectsFields.objfid==Objects.objid" ,uselist=False, backref="objfrel")
    orig_id = db.Column(VARCHAR(255))
    object_link= db.Column(VARCHAR(255))

# Ajout des colonnes numériques & textuelles libres
for i in range(1,501):
    setattr(ObjectsFields,"n%02d"%i,db.Column(FLOAT))
for i in range(1,21):
    setattr(ObjectsFields,"t%02d"%i,db.Column(VARCHAR(250)))

class Objects_cnn_features(db.Model):
    __tablename__ = 'obj_cnn_features'
    objcnnid = db.Column(BIGINT,db.ForeignKey('obj_head.objid',ondelete="CASCADE"), primary_key=True)
    objhrel=db.relationship("Objects",foreign_keys="Objects.objid",primaryjoin="Objects_cnn_features.objcnnid==Objects.objid" ,uselist=False, backref="objcnnrel")

# Ajout des colonnes numériques & textuelles libres
for i in range(1,51):
    setattr(Objects_cnn_features,"cnn%02d"%i,db.Column(REAL))


# Index('IS_ObjectsProject',Objects.__table__.c.projid,Objects.__table__.c.classif_qual)
#utile pour home de  classif manu, car PG ne sait pas utiliser les Skip scan index.
Index('is_objectsprojectonly',Objects.__table__.c.projid)
Index('is_objectsprojclassifqual',Objects.__table__.c.projid,Objects.__table__.c.classif_id,Objects.__table__.c.classif_qual)
Index('is_objectslatlong',Objects.__table__.c.latitude,Objects.__table__.c.longitude)
Index('is_objectssample',Objects.__table__.c.sampleid)
Index('is_objectsdepth',Objects.__table__.c.depth_max,Objects.__table__.c.depth_min,Objects.__table__.c.projid)
Index('is_objectstime',Objects.__table__.c.objtime,Objects.__table__.c.projid)
Index('is_objectsdate',Objects.__table__.c.objdate,Objects.__table__.c.projid)
Index('is_objectsprojrandom',Objects.__table__.c.projid,Objects.__table__.c.random_value,Objects.__table__.c.classif_qual)
Index('is_objectfieldsorigid',ObjectsFields.__table__.c.orig_id)

class ObjectsClassifHisto(db.Model):
    __tablename__ = 'objectsclassifhisto'
    objid = db.Column(BIGINT,db.ForeignKey('obj_head.objid',ondelete="CASCADE"), primary_key=True)
    classif_date = db.Column(TIMESTAMP, primary_key=True)
    classif_type = db.Column(CHAR(1)) # A : Auto, M : Manu
    classif_id = db.Column(INTEGER)
    classif_qual = db.Column(CHAR(1))
    classif_who = db.Column(db.Integer,db.ForeignKey('users.id'))
    classif_score = db.Column(DOUBLE_PRECISION)


class Images(db.Model):
    __tablename__ = 'images'
    imgid = db.Column(BIGINT,db.Sequence('seq_images'), primary_key=True) # manuel ,db.Sequence('seq_images')
    objid = db.Column(BIGINT, db.ForeignKey('obj_head.objid'))
    imgrank=db.Column(INTEGER)
    file_name = db.Column(VARCHAR(255))
    orig_file_name = db.Column(VARCHAR(255))
    width = db.Column(INTEGER)
    height = db.Column(INTEGER)
    thumb_file_name = db.Column(VARCHAR(255))
    thumb_width = db.Column(INTEGER)
    thumb_height = db.Column(INTEGER)
Index('IS_ImagesObjects',Images.__table__.c.objid)
#Sequence("seq_images",1,1)

class TempTaxo(db.Model):
    __tablename__ = 'temp_taxo'
    idtaxo = db.Column(VARCHAR(20), primary_key=True)
    idparent = db.Column(VARCHAR(20))
    name = db.Column(VARCHAR(100))
    status = db.Column(CHAR(1))
    typetaxo = db.Column(VARCHAR(20))
    idfinal = db.Column(INTEGER)
Index('IS_TempTaxoParent',TempTaxo.__table__.c.idparent)
Index('IS_TempTaxoIdFinal',TempTaxo.__table__.c.idfinal)

GlobalDebugSQL=False
GlobalDebugSQL=True
def GetAssoc(sql,params=None,debug=False,cursor_factory=psycopg2.extras.DictCursor,keyid=0):
    if g.db is None:
        g.db=db.engine.raw_connection()
    cur = g.db.cursor(cursor_factory=cursor_factory)
    # cur = db.engine.raw_connection().cursor(cursor_factory=cursor_factory)
    try:
        starttime=datetime.datetime.now()
        cur.execute(sql,params)
        res=dict()
        for r in cur:
            res[r[keyid]]=r
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:
        app.logger.debug("GetAssoc Exception SQL = %s %s",sql,params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("GetAssoc (%s) SQL = %s %s",(datetime.datetime.now()-starttime).total_seconds(),sql,params)
        cur.close()
    return res

def GetAssoc2Col(sql,params=None,debug=False,dicttype=dict):
    if g.db is None:
        g.db=db.engine.raw_connection()
    cur = g.db.cursor()
    # cur = db.engine.raw_connection().cursor()
    try:
        starttime=datetime.datetime.now()
        cur.execute(sql,params)
        res=dicttype()
        for r in cur:
            res[r[0]]=r[1]
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:
        app.logger.debug("GetAssoc2Col  Exception SQL = %s %s",sql,params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("GetAssoc2Col (%s) SQL = %s %s",(datetime.datetime.now()-starttime).total_seconds(),sql,params)
        cur.close()
    return res

# Les parametres doivent être passés au format (%s)
def GetAll(sql,params=None,debug=False,cursor_factory=psycopg2.extras.DictCursor):
    if g.db is None:
        g.db=db.engine.raw_connection()
    cur = g.db.cursor(cursor_factory=cursor_factory)
    # cur = db.engine.raw_connection().cursor(cursor_factory=cursor_factory)
    try:
        starttime=datetime.datetime.now()
        cur.execute(sql,params)
        res = cur.fetchall()
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:
        app.logger.debug("GetAll Exception SQL = %s %s",sql,params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("GetAll (%s) SQL = %s %s",(datetime.datetime.now()-starttime).total_seconds(),sql,params)
        cur.close()
    return res

def ExecSQL(sql,params=None,debug=False):
    if g.db is None:
        g.db=db.engine.raw_connection()
    cur = g.db.cursor()
    # cur = db.engine.raw_connection().cursor()
    try:
        starttime=datetime.datetime.now()
        cur.execute(sql,params)
        LastRowCount=cur.rowcount
        cur.connection.commit()
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:
        app.logger.debug("ExecSQL Exception SQL = %s %s",sql,params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("ExecSQL (%s) SQL = %s %s",(datetime.datetime.now()-starttime).total_seconds(),sql,params)
        cur.close()
    return LastRowCount

def GetDBToolsDir():
    toolsdir=app.config['DB_TOOLSDIR']
    if len(toolsdir)>0:
        if toolsdir[0]=='.': # si chemin relatif on calcule le path absolu par rapport à la racine de l'appli
            toolsdir=os.path.join( os.path.dirname(os.path.realpath(__file__)),"..",toolsdir)
            toolsdir=os.path.normpath(toolsdir)
    return toolsdir

def CSVIntStringToInClause(InStr):
    if InStr is None:
        return ""
    return ",".join([str(int(x)) for x in InStr.split(',')])


def GetTaxoNameFromIdList(IdList):
    sql = """SELECT tf.id, tf.name||case when p1.name is not null and tf.name not like '%% %%'  then ' ('||p1.name||')' else ' ' end as name
             FROM taxonomy tf
            left join taxonomy p1 on tf.parent_id=p1.id
            WHERE  tf.id = any (%s) 
            order by tf.name """
    return GetAll(sql,[IdList])
