# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import datetime
import os

import psycopg2.extras
from flask_login import current_user
from flask_security import UserMixin, RoleMixin
from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import VARCHAR, DOUBLE_PRECISION, INTEGER, CHAR, TIMESTAMP

from appli import db, app, g, XSSEscape

users_roles = db.Table('users_roles',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id'), primary_key=True),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'), primary_key=True))


# noinspection PyPep8Naming
class roles(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)  # ,db.Sequence('seq_roles')
    name = db.Column(db.String(80), unique=True, nullable=False)

    #    description = db.Column(db.String(255))
    def __str__(self):
        return self.name


# noinspection PyPep8Naming
class users(db.Model, UserMixin):
    id = db.Column(db.Integer, db.Sequence('seq_users'), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    organisation = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    roles = db.relationship('roles', secondary=users_roles,
                            backref=db.backref('users', lazy='dynamic'))  #
    preferences = db.Column(db.String(40000))
    country = db.Column(db.String(50))
    # TODO: naming of below columns
    usercreationdate = db.Column(TIMESTAMP, default=func.now())
    usercreationreason = db.Column(db.String(1000))
    # Mail status: 'V' for verified, 'W' for wrong
    mail_status = db.Column(CHAR, server_default=' ')
    # Date the mail status was set
    mail_status_date = db.Column(TIMESTAMP)

    def __str__(self):
        return "{0} ({1})".format(self.name, self.email)


# noinspection PyPep8Naming
class countrylist(db.Model, UserMixin):
    __tablename__ = 'countrylist'
    countryname = db.Column(db.String(50), primary_key=True, nullable=False)


class Projects(db.Model):
    __tablename__ = 'projects'
    projid = db.Column(INTEGER, db.Sequence('seq_projects'), primary_key=True)
    title = db.Column(VARCHAR(255), nullable=False)
    visible = db.Column(db.Boolean(), default=True)
    license = db.Column(VARCHAR(16), default="", nullable=False)
    status = db.Column(VARCHAR(40), default="Annotate")  # Annotate, ExploreOnly, Annotate No Prediction
    mappingobj = db.Column(VARCHAR)
    mappingsample = db.Column(VARCHAR)
    mappingacq = db.Column(VARCHAR)
    mappingprocess = db.Column(VARCHAR)
    objcount = db.Column(DOUBLE_PRECISION)
    pctvalidated = db.Column(DOUBLE_PRECISION)
    pctclassified = db.Column(DOUBLE_PRECISION)
    classifsettings = db.Column(VARCHAR)  # Settings for Automatic classification.
    initclassiflist = db.Column(VARCHAR)  # Initial list of categories
    classiffieldlist = db.Column(VARCHAR)  # Fields available on sort & displayed field of Manual classif screen
    popoverfieldlist = db.Column(VARCHAR)  # Fields available on popover of Manual classif screen
    comments = db.Column(VARCHAR)
    description = db.Column(VARCHAR)
    fileloaded = db.Column(VARCHAR)
    rf_models_used = db.Column(VARCHAR)
    cnn_network_id = db.Column(VARCHAR(50))

    def __str__(self):
        return "{0} ({1})".format(self.title, self.projid)



class ProjectsPriv(db.Model):
    __tablename__ = 'projectspriv'
    id = db.Column(db.Integer, db.Sequence('seq_projectspriv'), primary_key=True)
    projid = db.Column(INTEGER, db.ForeignKey('projects.projid', ondelete="CASCADE"), nullable=False)
    member = db.Column(db.Integer, db.ForeignKey('users.id'))
    privilege = db.Column(VARCHAR(255), nullable=False)
    extra = db.Column(VARCHAR(1), nullable=True)
    memberrel = db.relationship("users")
    refproject = db.relationship('Projects', backref=db.backref('projmembers', cascade="all, delete-orphan",
                                                                single_parent=True))  # ,cascade='delete'

    def __str__(self):
        return "{0} ({1})".format(self.member, self.privilege)


Index('IS_ProjectsPriv', ProjectsPriv.__table__.c.projid, ProjectsPriv.__table__.c.member, unique=True)


class Samples(db.Model):
    __tablename__ = 'samples'
    sampleid = db.Column(INTEGER, db.Sequence('seq_samples'), primary_key=True)
    projid = db.Column(INTEGER, db.ForeignKey('projects.projid'))
    project = db.relationship("Projects")
    orig_id = db.Column(VARCHAR(255), nullable=False)
    latitude = db.Column(DOUBLE_PRECISION)
    longitude = db.Column(DOUBLE_PRECISION)
    dataportal_descriptor = db.Column(VARCHAR(8000))

    def __str__(self):
        return "{0} ({1})".format(self.orig_id, self.sampleid)


for i in range(1, 31):
    setattr(Samples, "t%02d" % i, db.Column(VARCHAR(250)))
Index('IS_SamplesProjectOrigId', Samples.__table__.c.projid, Samples.__table__.c.orig_id, unique=True)


class Acquisitions(db.Model):
    __tablename__ = 'acquisitions'
    acquisid = db.Column(INTEGER, db.Sequence('seq_acquisitions'), primary_key=True)
    acq_sample_id = db.Column(INTEGER, db.ForeignKey('samples.sampleid'), nullable=False)
    orig_id = db.Column(VARCHAR(255), nullable=False)
    instrument = db.Column(VARCHAR(255))

    def __str__(self):
        return "{0} ({1})".format(self.orig_id, self.acquisid)


for i in range(1, 31):
    setattr(Acquisitions, "t%02d" % i, db.Column(VARCHAR(250)))


class Process(db.Model):
    __tablename__ = 'process'
    # Now a common key with Acquisitions
    processid = db.Column(INTEGER, db.ForeignKey('acquisitions.acquisid', onupdate="CASCADE", ondelete="CASCADE"),
                          primary_key=True)
    orig_id = db.Column(VARCHAR(255), nullable=False)

    def __str__(self):
        return "{0} ({1})".format(self.orig_id, self.processid)


for i in range(1, 31):
    setattr(Process, "t%02d" % i, db.Column(VARCHAR(250)))

GlobalDebugSQL = False


# Les parametres doivent être passés au format (%s)
def GetAll(sql, params=None, debug=False, cursor_factory=psycopg2.extras.DictCursor, doXSSEscape=False):
    if g.db is None:
        g.db = db.engine.raw_connection()
    if doXSSEscape:
        cursor_factory = psycopg2.extras.RealDictCursor
    cur = g.db.cursor(cursor_factory=cursor_factory)
    starttime = datetime.datetime.now()
    try:
        cur.execute(sql, params)
        res = cur.fetchall()
        if doXSSEscape:
            for rid, row in enumerate(res):
                for k, v in row.items():
                    if isinstance(v, str):
                        res[rid][k] = XSSEscape(v)
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:  # noqa
        app.logger.debug("GetAll Exception SQL = %s %s", sql, params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("GetAll (%s) SQL = %s %s", (datetime.datetime.now() - starttime).total_seconds(), sql,
                             params)
        cur.close()
    return res


def ExecSQL(sql, params=None, debug=False):
    if g.db is None:
        g.db = db.engine.raw_connection()
    cur = g.db.cursor()
    starttime = datetime.datetime.now()
    try:
        cur.execute(sql, params)
        LastRowCount = cur.rowcount
        cur.connection.commit()
    except psycopg2.InterfaceError:
        app.logger.debug("Connection was invalidated!, Try to reconnect for next HTTP request")
        db.engine.connect()
        raise
    except:  # noqa
        app.logger.debug("ExecSQL Exception SQL = %s %s", sql, params)
        cur.connection.rollback()
        raise
    finally:
        if debug or GlobalDebugSQL:
            app.logger.debug("ExecSQL (%s) SQL = %s %s", (datetime.datetime.now() - starttime).total_seconds(), sql,
                             params)
        cur.close()
    return LastRowCount


def GetDBToolsDir():
    toolsdir = app.config['DB_TOOLSDIR']
    if len(toolsdir) > 0:
        if toolsdir[0] == '.':  # si chemin relatif on calcule le path absolu par rapport à la racine de l'appli
            toolsdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", toolsdir)
            toolsdir = os.path.normpath(toolsdir)
    return toolsdir


def CSVIntStringToInClause(InStr):
    if InStr is None:
        return ""
    return ",".join([str(int(x)) for x in InStr.split(',')])
