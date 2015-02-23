# -*- coding: utf-8 -*-
from flask import Flask
from appli import db,app, database

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView,filters
from wtforms  import TextField, PasswordField
from flask.ext.security.utils import encrypt_password


class UsersView(ModelView):
    # Disable model creation
    can_create = False

    # Override displayed fields
    column_list = ('email', 'name','organisation','active', 'roles')
    form_columns = ('email', 'name','organisation', 'active', 'password', 'roles')
    form_overrides = {
        'email': TextField,
        'password': PasswordField,
    }

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UsersView, self).__init__(database.users, session, **kwargs)

    def update_model(self, form, model):
        # Do not set password if its field is empty.
        if not form._fields['password'].data:
            del form._fields['password']
        else:
            form._fields['password'].data =encrypt_password(form._fields['password'].data)
        return super(UsersView, self).update_model(form, model)

# Create admin
admin = admin.Admin(app, name='Ecotaxa Administration')

# Add views
#admin.add_view(sqla.ModelView(database.users, db.session))
admin.add_view(UsersView(db.session))

#admin.add_view(CategoriesAdmin(Categories, db.session))
