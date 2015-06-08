# -*- coding: utf-8 -*-
from appli import db
from flask.ext.security import  UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR,TIMESTAMP
from sqlalchemy import Index

AdministratorLabel="Application Administrator"

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
    def __str__(self):
        return "{0} ({1})".format(self.name,self.email)

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
    projmembers=db.relationship('ProjectsPriv',backref=db.backref('projects')) #
    def __str__(self):
        return "{0} ({1})".format(self.title,self.projid)

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
    depth_min = db.Column(FLOAT)
    depth_max = db.Column(FLOAT)
    images=db.relationship("Images")
    classif_id = db.Column(INTEGER)
    classif_qual = db.Column(CHAR(1))
    classif_who = db.Column(db.Integer,db.ForeignKey('users.id'))
    classif_when = db.Column(TIMESTAMP)
    classif_auto_id = db.Column(INTEGER)
    classif_auto_score = db.Column(DOUBLE_PRECISION)
    classif_auto_when = db.Column(TIMESTAMP)
    img0id = db.Column(BIGINT)
    img0=db.relationship("Images",foreign_keys="Images.objid")
    imgcount = db.Column(INTEGER)
    complement_info = db.Column(VARCHAR)
    weblink = db.Column(VARCHAR)
    similarity = db.Column(DOUBLE_PRECISION)
    sunpos = db.Column(CHAR(1))  # position du soleil
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

class Images(db.Model):
    __tablename__ = 'images'
    imgid = db.Column(BIGINT, primary_key=True) # manuel ,db.Sequence('seq_images')
    objid = db.Column(BIGINT, db.ForeignKey('objects.objid'))
    imgrank=db.Column(INTEGER)
    file_name = db.Column(VARCHAR(255))
    width = db.Column(INTEGER)
    height = db.Column(INTEGER)
    thumb_file_name = db.Column(VARCHAR(255))
    thumb_width = db.Column(INTEGER)
    thumb_height = db.Column(INTEGER)
Index('IS_ImagesObjects',Images.__table__.c.objid)


