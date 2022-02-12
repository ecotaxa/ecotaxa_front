# manage.py
import os
import shutil

from flask_script import Manager
# noinspection PyDeprecation
from flask_security.utils import encrypt_password

import appli.constants
from appli import app, g
from appli import db, user_datastore, database

manager = Manager(app)


@manager.command
def dbdrop():
    db.drop_all()


@manager.command
def dbcreate():
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        db.create_all()
        database.ExecSQL("""create view objects as 
                  select sam.projid, sam.sampleid, obh.*, obh.acquisid as processid, ofi.*
                    from obj_head obh
                    join acquisitions acq on obh.acquisid = acq.acquisid
                    join samples sam on acq.acq_sample_id = sam.sampleid 
                    left join obj_field ofi on obh.objid = ofi.objfid -- allow elimination by planner
                    """)


@manager.command
def createsampledata():
    r = database.Projects.query.filter_by(projid=1).first()
    if r is None:
        db.session.add(database.Projects(projid=1, title="Test Project 1"))
        db.session.commit()


@manager.command
def FullDBRestore(UseExistingDatabase=False):
    """
    Will restore an exported DB as is and replace all existing data
    """
    from appli.db_imp_exp import RestoreDBFull
    if UseExistingDatabase:
        print("You have specified the UseExistingDatabase option, the database itself will be kept, "
              "but all its content will be removed")
    if input("This operation will import an exported DB and DESTROY all existing data of the existing database.\n"
             "Are you SURE ? Confirm by Y !").lower() != "y":
        print("Import Aborted !!!")
        exit()
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        RestoreDBFull(UseExistingDatabase)


@manager.command
def CreateDB(UseExistingDatabase=False):
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        if UseExistingDatabase:
            print("You have specified the UseExistingDatabase option, "
                  "the database itself will be kept, but all its content will be removed")
        if input("This operation will create a new empty DB.\n"
                 " If a database exists, it will DESTROY all existing data of the existing database.\n"
                 "Are you SURE ? Confirm by Y !").lower() != "y":
            print("Import Aborted !!!")
            exit()

        print("Configuration is Database:", app.config['DB_DATABASE'])
        print("Login: ", app.config['DB_USER'], "/", app.config['DB_PASSWORD'])
        print("Host: ", app.config['DB_HOST'])
        import psycopg2

        if os.path.exists("vault"):
            print("Drop existings images")
            shutil.rmtree("vault")
            os.mkdir("vault")

        print("Connect Database")
        if UseExistingDatabase:
            conn = psycopg2.connect(user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
                                    host=app.config['DB_HOST'], database=app.config['DB_DATABASE'])
        else:
            # On se loggue en postgres pour dropper/creer les bases qui doit être déclaré trust dans hba_conf
            conn = psycopg2.connect(user='postgres', host=app.config['DB_HOST'])
        cur = conn.cursor()

        conn.set_session(autocommit=True)
        if UseExistingDatabase:
            print("Drop the existing public schema")
            sql = "DROP SCHEMA public cascade"
        else:
            print("Drop the existing database")
            sql = "DROP DATABASE IF EXISTS " + app.config['DB_DATABASE']
        cur.execute(sql)

        if UseExistingDatabase:
            print("Create the public schema")
            sql = "create schema public AUTHORIZATION " + app.config['DB_USER']
        else:
            print("Create the new database")
            sql = "create DATABASE " + app.config['DB_DATABASE'] + " WITH ENCODING='UTF8'  OWNER=" + app.config[
                'DB_USER'] + " TEMPLATE=template0 LC_CTYPE='C' LC_COLLATE='C' CONNECTION LIMIT=-1 "
        cur.execute(sql)

        print("Create the Schema")
        dbcreate()
        print("NOT CREATING Roles & Users & Country list")
        print("Creation Done")


@manager.command
def UpdateSunPos(ProjId):
    """
    will update Sunpos field for object of the given project
    if projid = * all projects are updated
    """
    from astral import AstralError
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        param = []
        sql = """select distinct objdate, objtime, 
                                 round(cast(latitude as NUMERIC),4) latitude,
                                 round(cast(longitude as NUMERIC),4) longitude
                   from obj_head
                 where objdate is not null 
                   and objtime is not null  
                   and longitude is not null 
                   and latitude is not null
     """
        if ProjId != '*':
            sql += " and projid=%s "
            param.append(ProjId)
        Obj = database.GetAll(sql, param)
        for o in Obj:
            # l=Location()
            # l.latitude=o['latitude']
            # l.longitude = o['longitude']
            # s=l.sun(date=o['objdate'],local=False)
            # dt=datetime.datetime(o['objdate'].year,o['objdate'].month,o['objdate'].day,o['objtime'].hour,
            # o['objtime'].minute,o['objtime'].second,tzinfo=pytz.UTC)
            # if s['sunset'].time()>s['sunrise'].time() \
            #         and dt.time()>=s['sunset'].time(): Result='N'
            # elif dt>=s['dusk']: Result='U'
            # elif dt>=s['sunrise']: Result='D'
            app.logger.info("Process %s %s %s %s", o['objdate'], o['objtime'], o['latitude'], o['longitude'])
            try:
                Result = CalcAstralDayTime(o['objdate'], o['objtime'], o['latitude'], o['longitude'])
                sql = "update obj_head set sunpos=%s " \
                      " where objdate=%s " \
                      "   and objtime=%s " \
                      "   and round(cast(latitude as NUMERIC),4) = %s " \
                      "   and round(cast(longitude as NUMERIC),4) = %s "
                param = [Result, o['objdate'], o['objtime'], o['latitude'], o['longitude']]
                if ProjId != '*':
                    sql += " and projid=%s "
                    param.append(ProjId)
                database.ExecSQL(sql, param)
                app.logger.info(Result)
            except AstralError as e:
                app.logger.error("Astral error : %s", e)

        # print(Result)


if __name__ == "__main__":
    manager.run()


def CalcAstralDayTime(Date, Time, Latitude, Longitude):
    """
    Calcule la position du soleil pour l'heure donnée.
    :param Date: Date UTC
    :param Time:  Heure UTC
    :param Latitude: Latitude
    :param Longitude: Longitude
    :return: D pour Day, U pour Dusk/crépuscule, N pour Night/Nuit, A pour Aube/Dawn
    """
    from astral import Location
    l = Location()
    l.solar_depression = 'nautical'
    l.latitude = Latitude
    l.longitude = Longitude
    s = l.sun(date=Date, local=False)
    # print(Date,Time,Latitude,Longitude,s,)
    Result = '?'
    Inter = ({'d': 'sunrise', 'f': 'sunset', 'r': 'D'}
             , {'d': 'sunset', 'f': 'dusk', 'r': 'U'}
             , {'d': 'dusk', 'f': 'dawn', 'r': 'N'}
             , {'d': 'dawn', 'f': 'sunrise', 'r': 'A'}
             )
    for I in Inter:
        if s[I['d']].time() < s[I['f']].time() and (Time >= s[I['d']].time() and Time <= s[I['f']].time()):
            Result = I['r']
        elif s[I['d']].time() > s[I['f']].time() and (Time >= s[I['d']].time() or Time <= s[I['f']].time()):
            Result = I['r']  # Changement de jour entre les 2 parties de l'intervalle
    return Result
