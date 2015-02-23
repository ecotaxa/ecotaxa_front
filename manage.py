# manage.py

from flask.ext.script import Manager
from flask.ext.security.utils import encrypt_password

from appli import app

manager = Manager(app)

@manager.command
def hello():
    print ("hello")

@manager.command
def createadminuser():
    """
    Create Admin User in the database admin/password
    """
    from appli import db,user_datastore
    u=user_datastore.find_user(email='admin')
    print(u)
    user_datastore.delete_user(u)
    user_datastore.create_user(email='admin', password=encrypt_password('altidev'))
    user_datastore.create_role(name="admin",description="Application Administrator")
    user_datastore.add_role_to_user('admin','admin')
    db.session.commit()

@manager.command
def dbdrop():
    from appli import db,user_datastore
    db.drop_all()
@manager.command
def dbcreate():
    from appli import db,user_datastore
    db.create_all()




if __name__ == "__main__":
    manager.run()