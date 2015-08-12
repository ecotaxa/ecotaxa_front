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
    db.drop_all()
@manager.command
def dbcreate():
    db.create_all()
    from flask.ext.migrate import _get_config
    config = _get_config(None)
    from alembic import command
    command.stamp(config, 'head')


@manager.command
def createsampledata():
    r=database.Projects.query.filter_by(projid=1).first()
    if r is None:
        db.session.add(database.Projects(projid=1,title="Test Project 1"))
        db.session.commit()

@manager.command
def ForceTest1Values():
    from appli import ObjectToStr
    from appli.tasks.taskmanager import AsyncTask,LoadTask
    t=LoadTask(16)
    t.param.IntraStep=0
    t.task.taskstep=1
    t.UpdateParam()


if __name__ == "__main__":
    manager.run()