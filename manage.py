# manage.py

from flask.ext.script import Manager
from flask.ext.security.utils import encrypt_password
from flask.ext.migrate import Migrate, MigrateCommand
from appli import db,user_datastore,database

from appli import app

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def hello():
    print ("hello")

@manager.command
def createadminuser():
    """
    Create Admin User in the database admin/password
    """

    from appli.database import roles
    r=roles.query.filter_by(id=1).first()
    if r is None:
        db.session.add(roles(id=1,name=database.AdministratorLabel))
        db.session.commit()
    r=roles.query.filter_by(id=2).first()
    if r is None:
        db.session.add(roles(id=2,name='Users Administrator'))
        db.session.commit()

    u=user_datastore.find_user(email='admin')
    print(u)
    if u is not None:
        user_datastore.delete_user(u)
        db.session.commit()
    user_datastore.create_user(email='admin', password=encrypt_password('altidev'),name="Application Administrator")
    user_datastore.add_role_to_user('admin','Application Administrator')
    db.session.commit()

@manager.command
def dbdrop():
    from appli import db,user_datastore
    db.drop_all()
@manager.command
def dbcreate():
    from appli import db,user_datastore
    db.create_all()

@manager.command
def createsampledata():
    from appli import db,database
    r=database.Projects.query.filter_by(projid=1).first()
    if r is None:
        db.session.add(database.Projects(projid=1,title="Test Project 1"))
        db.session.commit()


if __name__ == "__main__":
    manager.run()