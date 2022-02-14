# manage.py
import os
import shutil

from flask_script import Manager

from appli import app, g
from appli import db, database


manager = Manager(app)


@manager.command
def dbdrop():
    db.drop_all()


@manager.command
def dbcreate():
    with app.app_context():  # Création d'un contexte pour utiliser les fonction GetAll,ExecSQL qui mémorisent
        g.db = None
        db.create_all()


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


if __name__ == "__main__":
    manager.run()
