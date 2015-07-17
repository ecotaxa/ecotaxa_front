# -*- coding: utf-8 -*-
from flask import Flask
from appli import db,app, database

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView,filters
from wtforms  import TextField, PasswordField,TextAreaField
from flask.ext.security.utils import encrypt_password
from flask.ext.admin import base
from flask_admin.form import RenderTemplateWidget
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.model.form import InlineFormAdmin
from wtforms.fields import SelectField

class UsersView(ModelView):
    # Disable model creation
    can_create = True

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

    def create_model(self, form):
        form._fields['password'].data =encrypt_password(form._fields['password'].data)
        return super(UsersView, self).create_model(form)

# Permet de presenter la Vue Inline sous forme de tableau sans les titres.
class ProjectsViewCustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = InlineModelFormList
    inline_field_list_type.form_field_type.widget.template="admin/inline_table_form.html"

# Customized inline form handler
class ProjectsViewPrivInlineModelForm(InlineFormAdmin):
    form_label = 'Privileges'
    form_overrides = dict(privilege=SelectField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        privilege=dict(
            choices=[(0, 'View'), ('Annotate', 'Annotate'), ('Manage', 'Manage')]
        ))
    def __init__(self):
        return super(ProjectsViewPrivInlineModelForm, self).__init__(database.ProjectsPriv)

class ProjectsView(ModelView):
    column_list = ('projid', 'title')
    inline_model_form_converter = ProjectsViewCustomInlineModelConverter
    inline_models = (ProjectsViewPrivInlineModelForm(),)
    form_overrides = dict(mappingobj  =TextAreaField,mappingsample  =TextAreaField,mappingacq=TextAreaField,mappingprocess  =TextAreaField,classiffieldlist=TextAreaField  )

    def __init__(self, session, **kwargs):
        super(ProjectsView, self).__init__(database.Projects, session, **kwargs)


# Create admin
adminApp = admin.Admin(app, name='Ecotaxa Administration')

# Add views
#admin.add_view(sqla.ModelView(database.users, db.session))
adminApp.add_view(UsersView(db.session))
adminApp.add_view(ProjectsView(db.session))
adminApp.add_link(base.MenuLink('Ecotaxa Home', url='/'))

#admin.add_view(CategoriesAdmin(Categories, db.session))
