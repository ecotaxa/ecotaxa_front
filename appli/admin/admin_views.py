# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2016  Picheral, Colin, Irisson (UPMC-CNRS)
#
# flask_admin views for EcoTaxa DB
#
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

from appli import database as ecotaxa_db_def

from appli.database import GetAll


class SecureStrippingBaseForm(SecureForm):
    """
        A form metaclass stripping values
    """

    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            if unbound_field.field_class != InlineModelFormList:
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
        super(UsersView, self).__init__(ecotaxa_db_def.users, session, **kwargs)

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
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)

    edit_template = 'admin2/users_edit.html'
    create_template = 'admin2/users_create.html'


class UsersViewRestricted(UsersView):
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    form_columns = ('email', 'name', 'organisation', 'active', 'password')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UsersViewRestricted, self).__init__(session, **kwargs)

    def is_accessible(self):
        return (not current_user.has_role(ecotaxa_db_def.AdministratorLabel)) \
               and current_user.has_role(ecotaxa_db_def.UserAdministratorLabel)


# Permet de presenter la Vue Inline sous forme de tableau sans les titres.
class ProjectsViewCustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = InlineModelFormList
    inline_field_list_type.form_field_type.widget.template = "admin2/inline_table_form.html"


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
        super(ProjectsViewPrivInlineModelForm, self).__init__(ecotaxa_db_def.ProjectsPriv)


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
    edit_template = 'admin2/projects_edit.html'
    create_template = 'admin2/projects_create.html'
    form_widget_args = {
        'title': {'style': 'width: 400px;'}
    }

    def __init__(self, session, **kwargs):
        super(ProjectsView, self).__init__(ecotaxa_db_def.Projects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class ProjectsViewLight(ModelView):
    column_list = ('projid', 'title', 'visible', 'status', 'objcount', 'pctvalidated', 'pctclassified')
    form_columns = ('title', 'visible', 'status')
    column_descriptions = {'title': "My title"}
    column_searchable_list = ('title',)
    column_default_sort = 'projid'
    inline_model_form_converter = ProjectsViewCustomInlineModelConverter
    inline_models = (ProjectsViewPrivInlineModelForm(),)
    edit_template = 'admin2/projects_edit.html'
    create_template = 'admin2/projects_create.html'

    def __init__(self, session, **kwargs):
        super(ProjectsViewLight, self).__init__(ecotaxa_db_def.Projects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class SamplesView(ModelView):
    column_list = ('sampleid', 'projid', 'orig_id', 'latitude', 'longitude', 't01', 't02', 't03')
    column_filters = ('sampleid', 'projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    form_overrides = dict(dataportal_descriptor=TextAreaField)

    def __init__(self, session, **kwargs):
        super(SamplesView, self).__init__(ecotaxa_db_def.Samples, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class ProcessView(ModelView):
    column_list = ('processid', 'orig_id', 't01', 't02', 't03')
    column_filters = ('processid', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(ProcessView, self).__init__(ecotaxa_db_def.Process, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class AcquisitionsView(ModelView):
    column_list = ('acquisid', 'acq_sample_id', 'orig_id', 't01', 't02', 't03')
    column_filters = ('acquisid', 'acq_sample_id', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(AcquisitionsView, self).__init__(ecotaxa_db_def.Acquisitions, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class TaxonomyView(ModelView):
    column_list = ('id', 'parent_id', 'name', 'id_source')
    column_filters = ('id', 'parent_id', 'name', 'id_source')
    column_searchable_list = ('name',)
    page_size = 100

    # form_columns = ('id','parent_id', 'name','id_source')
    # form_overrides = dict(dataportal_descriptor  =TextAreaField )
    def __init__(self, session, **kwargs):
        super(TaxonomyView, self).__init__(ecotaxa_db_def.Taxonomy, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class ObjectsView(ModelView):
    column_list = ('objid', 'orig_id', 'acquisid', 'classif_qual', 'objdate',)
    column_filters = ('objid', 'orig_id', 'acquisid', 'classif_qual')
    form_overrides = dict(complement_info=TextAreaField)
    form_excluded_columns = ('classif_id', 'classif_auto', 'acquis',
                             'images', 'sample', 'classiffier', 'objfrel')
    form_ajax_refs = {'classif': {'fields': ('name',)}}

    def __init__(self, session, **kwargs):
        super(ObjectsView, self).__init__(ecotaxa_db_def.Objects, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)


class ObjectsFieldsView(ModelView):
    column_list = ('objfid',)
    column_filters = ('objfid',)
    column_searchable_list = ()
    form_excluded_columns = ('objhrel',)

    def __init__(self, session, **kwargs):
        super(ObjectsFieldsView, self).__init__(ecotaxa_db_def.ObjectsFields, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(ecotaxa_db_def.AdministratorLabel)
