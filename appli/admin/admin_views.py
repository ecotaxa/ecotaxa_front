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
from flask_admin.model.form import InlineFormAdmin
from flask_login import current_user
# noinspection PyDeprecation
from wtforms import TextAreaField
from wtforms.fields import SelectField

import appli.constants
from appli import database as ecotaxa_db_def


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
        return current_user.has_role(appli.constants.AdministratorLabel)


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
        return current_user.has_role(appli.constants.AdministratorLabel)


class SamplesView(ModelView):
    column_list = ('sampleid', 'projid', 'orig_id', 'latitude', 'longitude', 't01', 't02', 't03')
    column_filters = ('sampleid', 'projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    form_overrides = dict(dataportal_descriptor=TextAreaField)

    def __init__(self, session, **kwargs):
        super(SamplesView, self).__init__(ecotaxa_db_def.Samples, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(appli.constants.AdministratorLabel)


class ProcessView(ModelView):
    column_list = ('processid', 'orig_id', 't01', 't02', 't03')
    column_filters = ('processid', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(ProcessView, self).__init__(ecotaxa_db_def.Process, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(appli.constants.AdministratorLabel)


class AcquisitionsView(ModelView):
    column_list = ('acquisid', 'acq_sample_id', 'orig_id', 't01', 't02', 't03')
    column_filters = ('acquisid', 'acq_sample_id', 'orig_id')
    column_searchable_list = ('orig_id',)

    def __init__(self, session, **kwargs):
        super(AcquisitionsView, self).__init__(ecotaxa_db_def.Acquisitions, session, **kwargs)

    def is_accessible(self):
        return current_user.has_role(appli.constants.AdministratorLabel)
