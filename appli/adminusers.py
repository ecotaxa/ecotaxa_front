# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
import flask_admin
from flask_admin import base
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import SecureForm
from flask_admin.helpers import get_form_data
from flask_admin.model.form import InlineFormAdmin
from flask_login import current_user
# noinspection PyDeprecation
from flask_security.utils import encrypt_password
from wtforms import TextAreaField
from wtforms.fields import SelectField, TextField, PasswordField
from wtforms.validators import ValidationError

from appli import db
# We need the @route there
from appli.adminothers import *
from appli.database import GetAll


class SecureStrippingBaseForm(SecureForm):
    """
        A form metaclass stripping values
    """
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            filters.append(_strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)


def _strip_filter(value):
    # strip field if possible
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value

# noinspection PyProtectedMember
class UsersView(ModelView):
    # Disable model creation
    can_create = True
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    # Override displayed fields
    column_list = ('email', 'name', 'organisation', 'active', 'roles', 'country')
    form_columns = ('email', 'name', 'organisation', 'active', 'roles', 'password',
                    'country', 'usercreationreason')
    column_searchable_list = ('email', 'name')
    form_overrides = {
        'email': TextField,
        'password': PasswordField,
        'usercreationreason': TextAreaField,
        'country': SelectField
    }

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UsersView, self).__init__(database.users, session, **kwargs)

    def update_model(self, form, model):
        # Do not set password if its field is empty.
        if not form._fields['password'].data:
            del form._fields['password']
        else:
            # noinspection PyDeprecation
            form._fields['password'].data = encrypt_password(form._fields['password'].data)
        return super(UsersView, self).update_model(form, model)

    def create_model(self, form):
        # noinspection PyDeprecation
        form._fields['password'].data = encrypt_password(form._fields['password'].data)
        return super(UsersView, self).create_model(form)

    # noinspection PyMethodParameters
    def checkpasswordequal(form, field):
        if field.data != form._fields['password_confirm'].data:
            raise ValidationError("Password Confirmation doesn't match")

    def edit_form(self, obj=None):
        form = self._edit_form_class(get_form_data(), obj=obj)
        form.country.choices = [('', '')] + GetAll("""select countryname k,countryname v from countrylist order by 1""")
        return form

    def create_form(self, obj=None):
        return self.edit_form(obj)

    def scaffold_form(self):
        form_class = super(UsersView, self).scaffold_form()
        form_class.password_confirm = PasswordField('Password Confirmation')
        return form_class

    form_args = dict(
        password=dict(validators=[checkpasswordequal])
    )

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)

    edit_template = 'admin/users_edit.html'
    create_template = 'admin/users_create.html'


class UsersViewRestricted(UsersView):
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    form_columns = ('email', 'name', 'organisation', 'active', 'password')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UsersViewRestricted, self).__init__(session, **kwargs)

    def is_accessible(self):
        return (not current_user.has_role(database.AdministratorLabel)) and current_user.has_role(
            database.UserAdministratorLabel)


# Permet de presenter la Vue Inline sous forme de tableau sans les titres.
class ProjectsViewCustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = InlineModelFormList
    inline_field_list_type.form_field_type.widget.template = "admin/inline_table_form.html"


# Customized inline form handler
class ProjectsViewPrivInlineModelForm(InlineFormAdmin):
    form_label = 'Privileges'
    form_overrides = dict(privilege=SelectField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        privilege=dict(
            choices=[('View', 'View'), ('Annotate', 'Annotate'), ('Manage', 'Manage')]
        ))

    def __init__(self):
        super(ProjectsViewPrivInlineModelForm, self).__init__(database.ProjectsPriv)


class ProjectsView(ModelView):
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    column_list = ('projid', 'title', 'visible', 'status', 'objcount', 'pctvalidated', 'pctclassified')
    column_searchable_list = ('title',)
    column_default_sort = 'projid'
    inline_model_form_converter = ProjectsViewCustomInlineModelConverter
    inline_models = (ProjectsViewPrivInlineModelForm(),)
    form_overrides = dict(mappingobj=TextAreaField, mappingsample=TextAreaField, mappingacq=TextAreaField,
                          mappingprocess=TextAreaField, classiffieldlist=TextAreaField, classifsettings=TextAreaField)
    form_excluded_columns = ('objcount', 'pctvalidated', 'pctclassified')
    edit_template = 'admin/projects_edit.html'
    create_template = 'admin/projects_create.html'
    form_widget_args = {
        'title': {'style': 'width: 400px;'}
    }

    def __init__(self, session, **kwargs):
        super(ProjectsView, self).__init__(database.Projects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class ProjectsViewLight(ModelView):
    column_list = ('projid', 'title', 'visible', 'status', 'objcount', 'pctvalidated', 'pctclassified')
    form_columns = ('title', 'visible', 'status')
    column_descriptions = {'title': "My title"}
    column_searchable_list = ('title',)
    column_default_sort = 'projid'
    inline_model_form_converter = ProjectsViewCustomInlineModelConverter
    inline_models = (ProjectsViewPrivInlineModelForm(),)
    edit_template = 'admin/projects_edit.html'
    create_template = 'admin/projects_create.html'

    def __init__(self, session, **kwargs):
        super(ProjectsViewLight, self).__init__(database.Projects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class SamplesView(ModelView):
    column_list = ('sampleid', 'projid', 'orig_id', 'latitude', 'longitude', 't01', 't02', 't03')
    column_filters = ('sampleid', 'projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    form_overrides = dict(dataportal_descriptor=TextAreaField)

    def __init__(self, session, **kwargs):
        super(SamplesView, self).__init__(database.Samples, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class ProcessView(ModelView):
    column_list = ('processid', 'orig_id', 't01', 't02', 't03')
    column_filters = ('processid', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(ProcessView, self).__init__(database.Process, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class AcquisitionsView(ModelView):
    column_list = ('acquisid', 'acq_sample_id', 'orig_id', 't01', 't02', 't03')
    column_filters = ('acquisid', 'acq_sample_id', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(AcquisitionsView, self).__init__(database.Acquisitions, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class TaxonomyView(ModelView):
    column_list = ('id', 'parent_id', 'name', 'id_source')
    column_filters = ('id', 'parent_id', 'name', 'id_source')
    column_searchable_list = ('name',)
    page_size = 100

    # form_columns = ('id','parent_id', 'name','id_source')
    # form_overrides = dict(dataportal_descriptor  =TextAreaField )
    def __init__(self, session, **kwargs):
        super(TaxonomyView, self).__init__(database.Taxonomy, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class ObjectsView(ModelView):
    column_list = ('objid', 'acquisid', 'classif_qual', 'objdate', )
    column_filters = ('objid', 'acquisid', 'classif_qual')
    form_overrides = dict(complement_info=TextAreaField)
    form_excluded_columns = ('classif_id', 'classif_auto', 'acquis',
                             'images', 'sample', 'classiffier', 'objfrel')
    form_ajax_refs = {'classif': {'fields': ('name',)}}

    def __init__(self, session, **kwargs):
        super(ObjectsView, self).__init__(database.Objects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


class ObjectsFieldsView(ModelView):
    column_list = ('objfid', 'orig_id')
    column_filters = ('objfid', 'orig_id')
    column_searchable_list = ('orig_id',)
    form_excluded_columns = ('objhrel',)

    def __init__(self, session, **kwargs):
        super(ObjectsFieldsView, self).__init__(database.ObjectsFields, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(database.AdministratorLabel)


# Create admin
adminApp = flask_admin.Admin(app, name='Ecotaxa Administration', base_template="admin/base_no_link.html")

# Add views
# admin.add_view(sqla.ModelView(database.users, db.session))
adminApp.add_view(UsersView(db.session, name="Users"))
adminApp.add_view(UsersViewRestricted(db.session, name="users", endpoint="userrest"))

adminApp.add_view(ProjectsViewLight(db.session, endpoint="projectlight", category='Projects'))
adminApp.add_view(ProjectsView(db.session, name="Projects (Full)", category='Projects'))
adminApp.add_view(ObjectsView(db.session, category='Objects'))
adminApp.add_view(ObjectsFieldsView(db.session, category='Objects'))
adminApp.add_view(SamplesView(db.session, category='Objects'))
adminApp.add_view(ProcessView(db.session, category='Objects'))
adminApp.add_view(AcquisitionsView(db.session, category='Objects'))
adminApp.add_view(TaxonomyView(db.session, category='Taxonomy', name="Edit Taxonomy"))

# adminApp.add_link(base.MenuLink('Import Taxonomy (admin only)', category='Taxonomy',
# url='/Task/Create/TaskTaxoImport'))
adminApp.add_link(base.MenuLink('Merge 2 categories (admin only)',
                                category='Taxonomy', url='/dbadmin/merge2taxon'))
adminApp.add_link(base.MenuLink('Taxonomy errors (admin only)',
                                category='Taxonomy', url='/dbadmin/viewtaxoerror'))
adminApp.add_link(base.MenuLink('Ecotaxa Home', url='/'))
adminApp.add_link(base.MenuLink('View DB Size (admin only)',
                                category='Database', url='/dbadmin/viewsizes'))
adminApp.add_link(base.MenuLink('View DB Bloat (admin only)',
                                category='Database', url='/dbadmin/viewbloat'))

adminApp.add_link(base.MenuLink('SQL Console (admin only)',
                                category='Database', url='/dbadmin/console'))
adminApp.add_link(base.MenuLink('Recompute Projects and Taxo stat (can be long)(admin only)',
                                category='Database', url='/dbadmin/recomputestat'))


def GetAdminList():
    LstUsers = GetAll("""select name||'('||email||')' nom from users u
                        join users_roles r on u.id=r.user_id where r.role_id=1""")
    return ", ".join([r[0] for r in LstUsers])


app.jinja_env.globals.update(GetAdminList=GetAdminList)

# admin.add_view(CategoriesAdmin(Categories, db.session))
