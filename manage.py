# manage.py
import os
import shutil

from flask_script import Manager
# noinspection PyDeprecation
from flask_security.utils import encrypt_password

from appli import app, g
from appli import db, user_datastore, database

manager = Manager(app)


@manager.command
def hello():
    print("hello")


@manager.command
def createadminuser():
    """
    Create Admin User in the database admin/password
    """

    from appli.database import roles
    r = roles.query.filter_by(id=1).first()
    if r is None:
        print("Create role ", database.AdministratorLabel)
        # noinspection PyArgumentList
        db.session.add(roles(id=1, name=database.AdministratorLabel))
        db.session.commit()
    r = roles.query.filter_by(id=2).first()
    if r is None:
        print("Create role ", database.UserAdministratorLabel)
        # noinspection PyArgumentList
        db.session.add(roles(id=2, name=database.UserAdministratorLabel))
        db.session.commit()

    u = user_datastore.find_user(email='admin')
    if u is not None:
        print("drop user ", u)
        user_datastore.delete_user(u)
        db.session.commit()
    print("Create user 'admin' with password 'ecotaxa'")
    # noinspection PyDeprecation
    user_datastore.create_user(email='admin', password=encrypt_password('ecotaxa'), name="Application Administrator")
    user_datastore.add_role_to_user('admin', 'Application Administrator')
    db.session.commit()


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
def ResetDBSequence(cur=None):
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        print("Start Sequence Reset")
        if cur is None:
            cur = db.session
        cur.execute("SELECT setval('seq_acquisitions', (SELECT max(acquisid) FROM acquisitions), true)")
        cur.execute("SELECT setval('seq_images', (SELECT max(imgid) FROM images), true)")
        cur.execute("SELECT setval('seq_objects', (SELECT max(objid) FROM obj_head), true)")
        cur.execute("SELECT setval('seq_projects', (SELECT max(projid) FROM projects), true)")
        cur.execute("SELECT setval('seq_projectspriv', (SELECT max(id) FROM projectspriv), true)")
        cur.execute("SELECT setval('seq_samples', (SELECT max(sampleid) FROM samples), true)")
        cur.execute("SELECT setval('seq_taxonomy', (SELECT max(id) FROM taxonomy), true)")
        cur.execute("SELECT setval('seq_users', (SELECT max(id) FROM users), true)")
        cur.execute("SELECT setval('roles_id_seq', (SELECT max(id) FROM roles), true)")
        print("Sequence Reset Done")


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
        print("Create Roles & Users & Country list")
        createadminuser()
        sql = """INSERT INTO countrylist(countryname) VALUES
('Afghanistan'),('Albania'),('Algeria'),('America'),('Andorra'),('Angola'),('Antigua'),('Argentina'),('Armenia'),
('Australia'),('Austria'),('Azerbaijan'),
('Bahamas'),('Bahrain'),('Bangladesh'),('Barbados'),('Belarus'),('Belgium'),('Belize'),('Benin'),('Bhutan'),('Bissau'),
('Bolivia'),('Bosnia'),('Botswana'),
('Brazil'),('British'),('Brunei'),('Bulgaria'),('Burkina'),('Burma'),('Burundi'),('Cambodia'),('Cameroon'),
('Canada'),('Cape Verde'),('Central African Republic'),
('Chad'),('Chile'),('China'),('Colombia'),('Comoros'),('Congo'),('Costa Rica'),('Croatia'),('Cuba'),('Cyprus'),
('Czech'),('Denmark'),('Djibouti'),('Dominica'),
('East Timor'),('Ecuador'),('Egypt'),('El Salvador'),('Emirate'),('England'),('Eritrea'),('Estonia'),('Ethiopia'),
('Fiji'),('Finland'),('France'),('Gabon'),
('Gambia'),('Georgia'),('Germany'),('Ghana'),('Great Britain'),('Greece'),('Grenada'),('Grenadines'),('Guatemala'),
('Guinea'),('Guyana'),('Haiti'),('Herzegovina'),
('Honduras'),('Hungary'),('Iceland'),('India'),('Indonesia'),('Iran'),('Iraq'),('Ireland'),('Israel'),('Italy'),
('Ivory Coast'),('Jamaica'),('Japan'),('Jordan'),
('Kazakhstan'),('Kenya'),('Kiribati'),('Korea'),('Kosovo'),('Kuwait'),('Kyrgyzstan'),('Laos'),('Latvia'),('Lebanon'),
('Lesotho'),('Liberia'),('Libya'),
('Liechtenstein'),('Lithuania'),('Luxembourg'),('Macedonia'),('Madagascar'),('Malawi'),('Malaysia'),('Maldives'),
('Mali'),('Malta'),('Marshall'),('Mauritania'),
('Mauritius'),('Mexico'),('Micronesia'),('Moldova'),('Monaco'),('Mongolia'),('Montenegro'),('Morocco'),('Mozambique'),
('Myanmar'),('Namibia'),('Nauru'),
('Nepal'),('Netherlands'),('New Zealand'),('Nicaragua'),('Niger'),('Nigeria'),('Norway'),('Oman'),('Pakistan'),
('Palau'),('Panama'),('Papua'),('Paraguay'),
('Peru'),('Philippines'),('Poland'),('Portugal'),('Qatar'),('Romania'),('Russia'),('Rwanda'),('Samoa'),('San Marino'),
('Sao Tome'),('Saudi Arabia'),('Senegal'),
('Serbia'),('Seychelles'),('Sierra Leone'),('Singapore'),('Slovakia'),('Slovenia'),('Solomon'),('Somalia'),
('South Africa'),('South Sudan'),('Spain'),
('Sri Lanka'),('St. Kitts'),('St. Lucia'),('St Kitts'),('St Lucia'),('Saint Kitts'),('Santa Lucia'),('Sudan'),
('Suriname'),('Swaziland'),('Sweden'),
('Switzerland'),('Syria'),('Taiwan'),('Tajikistan'),('Tanzania'),('Thailand'),('Tobago'),('Togo'),('Tonga'),
('Trinidad'),('Tunisia'),('Turkey'),('Turkmenistan'),
('Tuvalu'),('Uganda'),('Ukraine'),('United Kingdom'),('United States'),('Uruguay'),('USA'),('Uzbekistan'),
('Vanuatu'),('Vatican'),('Venezuela'),
('Vietnam'),('Yemen'),('Zambia'),('Zimbabwe')"""
        database.ExecSQL(sql)
        print("Creation Done")


@manager.command
def UpdateSunPos(ProjId):
    """
    will update Sunpos field for object of the given project
    if projid = * all projects are updated
    """
    from appli import CalcAstralDayTime
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
