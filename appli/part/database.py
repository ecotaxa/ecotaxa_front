# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
from appli import db,app,g
from sqlalchemy.dialects.postgresql import BIGINT,FLOAT,VARCHAR,DATE,TIME,DOUBLE_PRECISION,INTEGER,CHAR,TIMESTAMP
from sqlalchemy import Index,Sequence,func
from appli.database import ExecSQL

class part_projects(db.Model):
    __tablename__ = 'part_projects'
    # pprojid  = db.Column(INTEGER,db.Sequence('seq_part_projects'), primary_key=True)
    # SQL Alchemy ne genere pas la sequence comme dans les autres tables précédentes, probablement un evolution
    # mais genere à la place un champ de type serial qui crée une sequence associée
    pprojid  = db.Column(INTEGER,db.Sequence('part_projects_pprojid_seq'), primary_key=True)
    ptitle = db.Column(VARCHAR(250),nullable=False)
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
    default_depthoffset = db.Column(DOUBLE_PRECISION)
    public_visibility_deferral_month = db.Column(INTEGER)
    public_partexport_deferral_month= db.Column(INTEGER)
    public_zooexport_deferral_month= db.Column(INTEGER)
    oldestsampledate = db.Column(TIMESTAMP)
    remote_type= db.Column(VARCHAR(20))
    remote_url = db.Column(VARCHAR(200))
    remote_user= db.Column(VARCHAR(100))
    remote_password= db.Column(VARCHAR(100))
    remote_directory= db.Column(VARCHAR(200))
    remote_vectorref= db.Column(VARCHAR(200))
    enable_descent_filter = db.Column(CHAR(1)) # Y/N/Empty

    def __str__(self):
        return "{0} ({1})".format(self.ptitle,self.pprojid)
Index('is_part_projects_projid',part_projects.__table__.c.projid)


class part_samples(db.Model):
    __tablename__ = 'part_samples'
    # psampleid  = db.Column(INTEGER,db.Sequence('seq_part_samples'), primary_key=True)
    # SQL Alchemy ne genere pas la sequence comme dans les autres tables précédentes, probablement un evolution
    # mais genere à la place un champ de type serial qui crée une sequence associée
    psampleid  = db.Column(INTEGER,db.Sequence('part_samples_psampleid_seq'), primary_key=True)
    pprojid = db.Column(INTEGER,db.ForeignKey('part_projects.pprojid'))
    project=db.relationship("part_projects")
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
    lastimg = db.Column(BIGINT)
    lastimgused = db.Column(BIGINT)
    bottomdepth = db.Column(INTEGER)
    yoyo = db.Column(db.Boolean())
    sampledate = db.Column(TIMESTAMP)
    op_sample_name = db.Column(VARCHAR(100))
    op_sample_email = db.Column(VARCHAR(100))
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
    acq_depthoffset = db.Column(DOUBLE_PRECISION)
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
    lisst_zscat_filename = db.Column(VARCHAR(200))
    lisst_kernel = db.Column(VARCHAR(200))
    lisst_year = db.Column(INTEGER)
    txt_data01 = db.Column(VARCHAR(200))
    txt_data02 = db.Column(VARCHAR(200))
    txt_data03 = db.Column(VARCHAR(200))
    txt_data04 = db.Column(VARCHAR(200))
    txt_data05 = db.Column(VARCHAR(200))
    txt_data06 = db.Column(VARCHAR(200))
    txt_data07 = db.Column(VARCHAR(200))
    txt_data08 = db.Column(VARCHAR(200))
    txt_data09 = db.Column(VARCHAR(200))
    txt_data10 = db.Column(VARCHAR(200))
    proc_process_ratio = db.Column(INTEGER)
    imp_descent_filtered_row = db.Column(INTEGER)
    imp_removed_empty_slice = db.Column(INTEGER)
    integrationtime = db.Column(INTEGER)

    def __str__(self):
        return "{0} ({1})".format(self.profileid,self.psampleid)
Index('is_part_samples_sampleid',part_samples.__table__.c.sampleid)
Index('is_part_samples_prj',part_samples.__table__.c.pprojid)

class part_histopart_reduit(db.Model):
    __tablename__ = 'part_histopart_reduit'
    psampleid  = db.Column(INTEGER,db.ForeignKey('part_samples.psampleid'), primary_key=True)
    lineno  = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes classe entières
for i in range(1, 16):
    setattr(part_histopart_reduit, "class%02d" % i, db.Column(INTEGER))
for i in range(1, 16):
    setattr(part_histopart_reduit, "biovol%02d" % i, db.Column(DOUBLE_PRECISION)) # en mm3/l

class part_histopart_det(db.Model):
    __tablename__ = 'part_histopart_det'
    psampleid = db.Column(INTEGER,db.ForeignKey('part_samples.psampleid'), primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes classe entières
for i in range(1, 46):
    setattr(part_histopart_det, "class%02d" % i, db.Column(INTEGER))
for i in range(1, 46):
    setattr(part_histopart_det, "biovol%02d" % i, db.Column(DOUBLE_PRECISION))  # en mm3/l

class part_histocat(db.Model):
    __tablename__ = 'part_histocat'
    psampleid = db.Column(INTEGER,db.ForeignKey('part_samples.psampleid'), primary_key=True)
    classif_id = db.Column(INTEGER, primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    watervolume = db.Column(DOUBLE_PRECISION)
    nbr = db.Column(DOUBLE_PRECISION)
    avgesd = db.Column(DOUBLE_PRECISION)
    totalbiovolume = db.Column(DOUBLE_PRECISION) # en mm3

class part_histocat_lst(db.Model):
    __tablename__ = 'part_histocat_lst'
    psampleid = db.Column(INTEGER,db.ForeignKey('part_samples.psampleid'), primary_key=True)
    classif_id = db.Column(INTEGER, primary_key=True)

class part_ctd(db.Model):
    __tablename__ = 'part_ctd'
    psampleid = db.Column(INTEGER,db.ForeignKey('part_samples.psampleid'), primary_key=True)
    lineno = db.Column(INTEGER, primary_key=True)
    depth = db.Column(DOUBLE_PRECISION)
    datetime = db.Column(TIMESTAMP)
    chloro_fluo = db.Column(DOUBLE_PRECISION)
    conductivity = db.Column(DOUBLE_PRECISION)
    cpar = db.Column(DOUBLE_PRECISION)
    depth_salt_water= db.Column(DOUBLE_PRECISION)
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
    qc_flag= db.Column(INTEGER)
    sound_speed_c = db.Column(DOUBLE_PRECISION)
    spar = db.Column(DOUBLE_PRECISION)
    temperature = db.Column(DOUBLE_PRECISION)
# Ajout des colonnes de mesures supplémentaires
for i in range(1, 21):
    setattr(part_ctd, "extrames%02d" % i, db.Column(DOUBLE_PRECISION))


def ComputeOldestSampleDateOnProject():
    ExecSQL("update part_projects pp  set oldestsampledate=(select min(sampledate) from part_samples ps where ps.pprojid=pp.pprojid)")
