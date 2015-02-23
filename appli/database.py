# -*- coding: utf-8 -*-
from appli import db
from flask.ext.security import  UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR

users_roles = db.Table('users_roles',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id'), primary_key=True),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'), primary_key=True))

class roles(db.Model, RoleMixin ):
    id = db.Column(db.Integer(),db.Sequence('seq_roles'), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    # Required for administrative interface. For python 3 please use __str__ instead.
    def __str__(self):
        return self.name
class users(db.Model, UserMixin):
    id = db.Column(db.Integer,db.Sequence('seq_users'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    organisation = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('roles', secondary=users_roles,
                            backref=db.backref('users', lazy='dynamic')) #
    # Required for administrative interface. For python 3 please use __str__ instead.
    def __str__(self):
        return self.email

class Projects(db.Model):
    __tablename__ = 'projects'
    projid  = db.Column(INTEGER,db.Sequence('seq_projects'), primary_key=True)
    title   = db.Column(VARCHAR(255))
    ownerid = db.Column(db.Integer,db.ForeignKey('users.id'))
    owner   = db.relationship("users")
    colmapping   = db.Column(VARCHAR)


class Objects(db.Model):
    __tablename__ = 'objects'
    objid = db.Column(BIGINT,db.Sequence('seq_objects'), primary_key=True)
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255))
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    objdate = db.Column(DATE)
    objtime = db.Column(TIME)
    depth_min = db.Column(FLOAT)
    depth_max = db.Column(FLOAT)
    images=db.relationship("Images")
    classif_id = db.Column(BIGINT)
    classif_qual = db.Column(CHAR(1))
    img0id = db.Column(BIGINT)
    img0=db.relationship("Images",foreign_keys="Images.objid")
# Ajout des colonnes numériques & textuelles libres
for i in range(1,100):
    setattr(Objects,"n%02d"%i,db.Column(FLOAT))
for i in range(1,10):
    setattr(Objects,"t%02d"%i,db.Column(VARCHAR(250)))

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
