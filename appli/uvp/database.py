# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from appli import db,app,g
from flask_security import  UserMixin, RoleMixin
from flask_login import current_user
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR,TIMESTAMP
from sqlalchemy import Index,Sequence,func
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import foreign,remote
import json,psycopg2.extras,datetime,os

class uvp_projects(db.Model):
    __tablename__ = 'uvp_projects'
    # uprojid  = db.Column(INTEGER,db.Sequence('seq_uvp_projects'), primary_key=True)
    # SQL Alchemy ne genere pas la sequence comme dans les autres tables précédentes, probablement un evolution
    # mais genere à la place un champ de type serial qui crée une sequence associée
    uprojid  = db.Column(INTEGER,db.Sequence('uvp_projects_uprojid_seq'), primary_key=True)
    utitle = db.Column(VARCHAR(250),nullable=False)
    rawfolder = db.Column(VARCHAR(250),nullable=False)
    ownerid = db.Column(db.Integer,db.ForeignKey('users.id'))
    owneridrel=db.relationship("users")
    projid = db.Column(INTEGER,db.ForeignKey('projects.projid'))
    project=db.relationship("Projects")
    instrumtype = db.Column(VARCHAR(50))
    op_name = db.Column(VARCHAR(100))
    op_email = db.Column(VARCHAR(100))
    cs_name = db.Column(VARCHAR(100))
    cs_email = db.Column(VARCHAR(100))
    do_name = db.Column(VARCHAR(100))
    do_email = db.Column(VARCHAR(100))
    prj_info = db.Column(VARCHAR(1000))
    prj_acronym = db.Column(VARCHAR(100))
    cruise = db.Column(VARCHAR(100))
    ship = db.Column(VARCHAR(100))
    default_instrumsn = db.Column(VARCHAR(50))
    default_aa = db.Column(DOUBLE_PRECISION)
    default_exp = db.Column(DOUBLE_PRECISION)
    default_volimage = db.Column(DOUBLE_PRECISION)
    default_depthoffset = db.Column(DOUBLE_PRECISION)
    dataportal_desc = db.Column(VARCHAR(8000))

    def __str__(self):
        return "{0} ({1})".format(self.utitle,self.uprojid)
Index('is_uvp_projects_projid',uvp_projects.__table__.c.projid)


class uvp_samples(db.Model):
    __tablename__ = 'uvp_samples'
    # usampleid  = db.Column(INTEGER,db.Sequence('seq_uvp_samples'), primary_key=True)
    # SQL Alchemy ne genere pas la sequence comme dans les autres tables précédentes, probablement un evolution
    # mais genere à la place un champ de type serial qui crée une sequence associée
    usampleid  = db.Column(INTEGER,db.Sequence('uvp_samples_usampleid_seq'), primary_key=True)
    uprojid = db.Column(INTEGER,db.ForeignKey('uvp_projects.uprojid'))
    project=db.relationship("uvp_projects")
    profileid = db.Column(VARCHAR(250),nullable=False)
    filename = db.Column(VARCHAR(250),nullable=False)
    sampleid = db.Column(INTEGER,db.ForeignKey('samples.sampleid'))
    sample=db.relationship("Samples")
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    organizedbydeepth = db.Column(db.Boolean())
    histobrutavailable = db.Column(db.Boolean())
    qualitytaxo = db.Column(VARCHAR(20))
    qualitypart = db.Column(VARCHAR(20))
    daterecalculhistotaxo = db.Column(TIMESTAMP)
    winddir = db.Column(INTEGER)
    winspeed = db.Column(INTEGER)
    seastate = db.Column(INTEGER)
    nebuloussness = db.Column(INTEGER)
    comment = db.Column(VARCHAR(1000))
    stationid = db.Column(VARCHAR(100))
    firstimage = db.Column(INTEGER)
    lastimg = db.Column(INTEGER)
    bottomdepth = db.Column(INTEGER)
    yoyo = db.Column(db.Boolean())
    sampledate = db.Column(TIMESTAMP)
    ctd_desc = db.Column(VARCHAR(1000))
    ctd_origfilename = db.Column(VARCHAR(250))
    ctd_import_name = db.Column(VARCHAR(100))
    ctd_import_email = db.Column(VARCHAR(100))
    ctd_import_datetime = db.Column(TIMESTAMP)
    ctd_status = db.Column(VARCHAR(50))
    instrumsn = db.Column(VARCHAR(50))
    acq_aa = db.Column(DOUBLE_PRECISION)
    acq_exp = db.Column(DOUBLE_PRECISION)
    acq_volimage = db.Column(DOUBLE_PRECISION)
    acq_pixel = db.Column(DOUBLE_PRECISION)
    acq_shutterspeed = db.Column(INTEGER)
    acq_smzoo = db.Column(INTEGER)
    acq_exposure = db.Column(INTEGER)
    acq_gain = db.Column(INTEGER)
    acq_filedescription = db.Column(VARCHAR(200))
    acq_eraseborder = db.Column(INTEGER)
    acq_tasktype = db.Column(INTEGER)
    acq_threshold = db.Column(INTEGER)
    acq_choice = db.Column(INTEGER)
    acq_disktype = db.Column(INTEGER)
    acq_smbase = db.Column(INTEGER)
    acq_ratio = db.Column(INTEGER)
    acq_descent_filter = db.Column(db.Boolean())
    acq_presure_gain = db.Column(DOUBLE_PRECISION)
    acq_xsize = db.Column(INTEGER)
    acq_ysize = db.Column(INTEGER)
    acq_barcode = db.Column(VARCHAR(50))
    proc_datetime = db.Column(TIMESTAMP)
    proc_gamma = db.Column(DOUBLE_PRECISION)
    proc_soft = db.Column(VARCHAR(250))
    op_sample_name = db.Column(VARCHAR(100))
    op_sample_email = db.Column(VARCHAR(100))

    def __str__(self):
        return "{0} ({1})".format(self.profileid,self.usampleid)
Index('is_uvp_samples_sampleid',uvp_samples.__table__.c.sampleid)
Index('is_uvp_samples_prj',uvp_samples.__table__.c.uprojid)

class uvp_histopart_reduit(db.Model):
    __tablename__ = 'uvp_histopart_reduit'
    usampleid  = db.Column(INTEGER,db.ForeignKey('uvp_samples.usampleid'), primary_key=True)
    lineno  = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes classe entières
for i in range(1, 16):
    setattr(uvp_histopart_reduit, "class%02d" % i, db.Column(INTEGER))

class uvp_histopart_det(db.Model):
    __tablename__ = 'uvp_histopart_det'
    usampleid = db.Column(INTEGER,db.ForeignKey('uvp_samples.usampleid'), primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes classe entières
for i in range(1, 46):
    setattr(uvp_histopart_det, "class%02d" % i, db.Column(INTEGER))

class uvp_histocat(db.Model):
    __tablename__ = 'uvp_histocat'
    usampleid = db.Column(INTEGER,db.ForeignKey('uvp_samples.usampleid'), primary_key=True)
    classif_id = db.Column(INTEGER, primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
    concentration = db.Column(DOUBLE_PRECISION)
    esdmoyen = db.Column(DOUBLE_PRECISION)
    biovolume = db.Column(DOUBLE_PRECISION)

class uvp_histocat_lst(db.Model):
    __tablename__ = 'uvp_histocat_lst'
    usampleid = db.Column(INTEGER,db.ForeignKey('uvp_samples.usampleid'), primary_key=True)
    classif_id = db.Column(INTEGER, primary_key=True)

class uvp_ctd(db.Model):
    __tablename__ = 'uvp_ctd'
    usampleid = db.Column(INTEGER,db.ForeignKey('uvp_samples.usampleid'), primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    chloro_fluo = db.Column(DOUBLE_PRECISION)
    conductivity = db.Column(DOUBLE_PRECISION)
    cpar = db.Column(DOUBLE_PRECISION)
    fcdom_factory = db.Column(DOUBLE_PRECISION)
    in_situ_density_anomaly = db.Column(DOUBLE_PRECISION)
    neutral_density = db.Column(DOUBLE_PRECISION)
    nitrate = db.Column(DOUBLE_PRECISION)
    oxygen_mass = db.Column(DOUBLE_PRECISION)
    oxygen_vol = db.Column(DOUBLE_PRECISION)
    par = db.Column(DOUBLE_PRECISION)
    part_backscattering_coef_470_nm = db.Column(DOUBLE_PRECISION)
    pot_temperature = db.Column(DOUBLE_PRECISION)
    potential_density_anomaly = db.Column(DOUBLE_PRECISION)
    potential_temperature = db.Column(DOUBLE_PRECISION)
    practical_salinity = db.Column(DOUBLE_PRECISION)
    practical_salinity__from_conductivity= db.Column(DOUBLE_PRECISION)
    pressure_in_water_column = db.Column(DOUBLE_PRECISION)
    qc_flag= db.Column(INTEGER)
    sound_speed_c = db.Column(DOUBLE_PRECISION)
    spar = db.Column(DOUBLE_PRECISION)
    temperature = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes de mesures supplémentaires
for i in range(1, 21):
    setattr(uvp_ctd, "extrames%02d" % i, db.Column(DOUBLE_PRECISION))

