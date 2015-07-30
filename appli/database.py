# -*- coding: utf-8 -*-
from appli import db,app
from flask.ext.security import  UserMixin, RoleMixin
from flask.ext.login import current_user
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR,TIMESTAMP
from sqlalchemy import Index,Sequence
import json,psycopg2.extras

AdministratorLabel="Application Administrator"
ClassifQual={'P':'predicted','D':'dubious','V':'validated'}
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
    preferences= db.Column(db.String(2000))
    def __str__(self):
        return "{0} ({1})".format(self.name,self.email)
    def GetPref(self,name,defval):
        try:
            tmp=json.loads(self.preferences)
            if isinstance(defval, (int)):
                return int(tmp.get(name,defval))
            if isinstance(defval, (float)):
                return float(tmp.get(name,defval))
            return tmp.get(name,defval)
        except:
            return defval
    def SetPref(self,name,newval):
        try:
            tmp=json.loads(self.preferences)
            if tmp.get(name,-99999)==newval:
                return 0# déjà la bonne valeur donc il n'y a rien à faire
        except:
            tmp={}
        tmp[name]=newval
        self.preferences=json.dumps(tmp)
        return 1

class Taxonomy(db.Model):
    __tablename__ = 'taxonomy'
    id  = db.Column(INTEGER,db.Sequence('seq_taxonomy'), primary_key=True)
    parent_id  = db.Column(INTEGER)
    name   = db.Column(VARCHAR(100),nullable=False)
    id_source  = db.Column(VARCHAR(20))
    def __str__(self):
        return "{0} ({1})".format(self.name,self.id)
Index('IS_TaxonomyParent',Taxonomy.__table__.c.parent_id)
Index('IS_TaxonomyName',Taxonomy.__table__.c.name)

class Projects(db.Model):
    __tablename__ = 'projects'
    projid  = db.Column(INTEGER,db.Sequence('seq_projects'), primary_key=True)
    title   = db.Column(VARCHAR(255),nullable=False)
    visible = db.Column(db.Boolean(),default=True)
    status = db.Column(VARCHAR(40),default="Annotate") # Annotate, ExploreOnly
    mappingobj   = db.Column(VARCHAR)
    mappingsample   = db.Column(VARCHAR)
    mappingacq   = db.Column(VARCHAR)
    mappingprocess   = db.Column(VARCHAR)
    pctvalidated = db.Column(DOUBLE_PRECISION)
    classifsettings  = db.Column(VARCHAR)
    initclassiflist  = db.Column(VARCHAR) # Initial list of categories
    classiffieldlist  = db.Column(VARCHAR) # Fields available on Manual classif screen
    projmembers=db.relationship('ProjectsPriv',backref=db.backref('projects')) #
    comments  = db.Column(VARCHAR)
    projtype  = db.Column(VARCHAR(50))
    def __str__(self):
        return "{0} ({1})".format(self.title,self.projid)
    def CheckRight(self,Level,userid=None): # Level 0 = Read, 1 = Annotate, 2 = Admin . userid=None = current user
        # pp=self.projmembers.filter(member=userid).first()
        if userid is None:
            u=current_user
            userid=u.id
        else:
            u=users.query.filter_by(id=userid).first()
        if len([x for x in u.roles if x=='Application Administrator'])>0:
            return True # Admin à tous les droits
        pp=[x for x in self.projmembers if x.member==userid]
        if len(pp)==0: # oas de privileges pour cet utilisateur
            return False
        pp=pp[0] #on recupere la premiere ligne seulement.
        if pp.privilege=='Manage':
            return True
        if pp.privilege=='Annotate' and Level<=1:
            return True
        if Level<=0:
            return True
        return False


class ProjectsPriv(db.Model):
    __tablename__ = 'projectspriv'
    id = db.Column(db.Integer,db.Sequence('seq_projectspriv'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'),nullable=False)
    member = db.Column(db.Integer,db.ForeignKey('users.id'))
    privilege = db.Column(VARCHAR(255),nullable=False)
    memberrel=db.relationship("users")
    #project= db.relation(Projects, backref='projectspriv')
    def __str__(self):
        return "{0} ({1})".format(self.member,self.privilege)
Index('IS_ProjectsPriv',ProjectsPriv.__table__.c.projid,ProjectsPriv.__table__.c.member, unique=True)

class Samples(db.Model):
    __tablename__ = 'samples'
    sampleid = db.Column(BIGINT,db.Sequence('seq_samples'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
for i in range(1,31):
    setattr(Samples,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_SamplesProject',Samples.__table__.c.projid)

class Acquisitions(db.Model):
    __tablename__ = 'acquisitions'
    acquisid = db.Column(BIGINT,db.Sequence('seq_acquisitions'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
for i in range(1,31):
    setattr(Acquisitions,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_AcquisitionsProject',Acquisitions.__table__.c.projid)

class Process(db.Model):
    __tablename__ = 'process'
    processid = db.Column(BIGINT,db.Sequence('seq_process'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
for i in range(1,31):
    setattr(Process,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_ProcessProject',Process.__table__.c.projid)

class Objects(db.Model):
    __tablename__ = 'objects'
    objid = db.Column(BIGINT,db.Sequence('seq_objects'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'),nullable=False)
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    objdate = db.Column(DATE)
    objtime = db.Column(TIME)
    object_link= db.Column(VARCHAR(255))
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
    classif_crossvalidation_id = db.Column(INTEGER)
    img0id = db.Column(BIGINT)
    img0=db.relationship("Images",foreign_keys="Images.objid")
    imgcount = db.Column(INTEGER)
    complement_info = db.Column(VARCHAR)
    weblink = db.Column(VARCHAR)
    similarity = db.Column(DOUBLE_PRECISION)
    sunpos = db.Column(CHAR(1))  # position du soleil
    random_value = db.Column(INTEGER)
    sampleid = db.Column(INTEGER,db.ForeignKey('samples.sampleid'))
    sample=db.relationship("Samples")
    acquisid = db.Column(INTEGER,db.ForeignKey('acquisitions.acquisid'))
    acquis=db.relationship("Acquisitions")
    processid = db.Column(INTEGER,db.ForeignKey('process.processid'))
    process=db.relationship("Process")

# Ajout des colonnes numériques & textuelles libres
for i in range(1,501):
    setattr(Objects,"n%02d"%i,db.Column(FLOAT))
for i in range(1,21):
    setattr(Objects,"t%02d"%i,db.Column(VARCHAR(250)))
Index('IS_ObjectsProject',Objects.__table__.c.projid,Objects.__table__.c.classif_qual)
Index('IS_ObjectsLatLong',Objects.__table__.c.latitude,Objects.__table__.c.longitude)
Index('IS_ObjectsSample',Objects.__table__.c.sampleid,Objects.__table__.c.classif_qual)
Index('IS_ObjectsClassif',Objects.__table__.c.classif_id,Objects.__table__.c.projid,Objects.__table__.c.classif_qual)
Index('IS_ObjectsDepth',Objects.__table__.c.projid,Objects.__table__.c.classif_qual,Objects.__table__.c.depth_max,Objects.__table__.c.depth_min)
Index('IS_ObjectsTime',Objects.__table__.c.projid,Objects.__table__.c.classif_qual,Objects.__table__.c.objtime)
Index('IS_ObjectsDate',Objects.__table__.c.objdate,Objects.__table__.c.projid,Objects.__table__.c.classif_qual)
Index('IS_ObjectsDate',Objects.__table__.c.objdate,Objects.__table__.c.projid,Objects.__table__.c.classif_qual)
Index('IS_ObjectsRandom',Objects.__table__.c.random_value,Objects.__table__.c.projid,Objects.__table__.c.classif_qual)

class ObjectsClassifHisto(db.Model):
    __tablename__ = 'objectsclassifhisto'
    objid = db.Column(BIGINT,db.ForeignKey('objects.objid'), primary_key=True)
    classif_date = db.Column(TIMESTAMP, primary_key=True)
    classif_type = db.Column(CHAR(1)) # A : Auto, M : Manu
    classif_id = db.Column(INTEGER)
    classif_qual = db.Column(CHAR(1))
    classif_who = db.Column(db.Integer,db.ForeignKey('users.id'))
    classif_score = db.Column(DOUBLE_PRECISION)


class Images(db.Model):
    __tablename__ = 'images'
    imgid = db.Column(BIGINT,db.Sequence('seq_images'), primary_key=True) # manuel ,db.Sequence('seq_images')
    objid = db.Column(BIGINT, db.ForeignKey('objects.objid'))
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

def GetAll(sql,params=None,debug=False,cursor_factory=psycopg2.extras.DictCursor):
    cur = db.engine.raw_connection().cursor(cursor_factory=cursor_factory)
    try:
        if debug:
            app.logger.debug("GetAll SQL = %s %s",sql,params)
        cur.execute(sql,params)
        res = cur.fetchall()
    finally:
        cur.close()
    return res

def ExecSQL(sql,params=None,debug=False):
    cur = db.engine.raw_connection().cursor()
    try:
        if debug:
            app.logger.debug("ExecSQL SQL = %s %s",sql,params)
        cur.execute(sql,params)
        cur.connection.commit()
    finally:
        cur.close()

