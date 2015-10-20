# -*- coding: utf-8 -*-
from appli import db,app, database
import flask.ext.admin
from flask.ext.admin.contrib.sqla import ModelView,filters
from wtforms  import TextAreaField
from flask.ext.security.utils import encrypt_password
from flask.ext.admin import base
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.model.form import InlineFormAdmin
from wtforms.fields import SelectField,TextField,PasswordField
from wtforms.validators import ValidationError

class UsersView(ModelView):
    # Disable model creation
    can_create = True

    # Override displayed fields
    column_list = ('email', 'name','organisation','active', 'roles')
    form_columns = ('email', 'name','organisation', 'active', 'roles', 'password')
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
    def checkpasswordequal(form, field):
        if field.data !=form._fields['password_confirm'].data:
            raise ValidationError("Password Confirmation doesn't match")

    def scaffold_form(self):
        form_class = super(UsersView, self).scaffold_form()
        form_class.password_confirm = PasswordField('Password Confirmation')
        return form_class
    form_args = dict(
        password=dict( validators=[checkpasswordequal])
    )

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
            choices=[('View', 'View'), ('Annotate', 'Annotate'), ('Manage', 'Manage')]
        ))
    def __init__(self):
        return super(ProjectsViewPrivInlineModelForm, self).__init__(database.ProjectsPriv)

class ProjectsView(ModelView):
    column_list = ('projid', 'title')
    inline_model_form_converter = ProjectsViewCustomInlineModelConverter
    inline_models = (ProjectsViewPrivInlineModelForm(),)
    form_overrides = dict(mappingobj  =TextAreaField,mappingsample  =TextAreaField,mappingacq=TextAreaField,mappingprocess  =TextAreaField,classiffieldlist=TextAreaField,classifsettings=TextAreaField  )

    def __init__(self, session, **kwargs):
        super(ProjectsView, self).__init__(database.Projects, session, **kwargs)


class SamplesView(ModelView):
    column_list = ('sampleid','projid', 'orig_id','latitude','longitude','t01','t02','t03')
    column_filters = ('sampleid','projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    form_overrides = dict(dataportal_descriptor  =TextAreaField )
    def __init__(self, session, **kwargs):
        super(SamplesView, self).__init__(database.Samples, session, **kwargs)

class ProcessView(ModelView):
    column_list = ('processid','projid', 'orig_id','t01','t02','t03')
    column_filters = ('processid','projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    def __init__(self, session, **kwargs):
        super(ProcessView, self).__init__(database.Process, session, **kwargs)

class AcquisitionsView(ModelView):
    column_list = ('acquisid','projid', 'orig_id','t01','t02','t03')
    column_filters = ('acquisid','projid', 'orig_id')
    column_searchable_list = ('orig_id',)
    def __init__(self, session, **kwargs):
        super(AcquisitionsView, self).__init__(database.Acquisitions, session, **kwargs)

class TaxonomyView(ModelView):
    column_list = ('id','parent_id', 'name','id_source')
    column_filters = ('id','parent_id', 'name','id_source')
    column_searchable_list = ('name',)
    page_size = 100
    # form_columns = ('id','parent_id', 'name','id_source')
    # form_overrides = dict(dataportal_descriptor  =TextAreaField )
    def __init__(self, session, **kwargs):
        super(TaxonomyView, self).__init__(database.Taxonomy, session, **kwargs)

class ObjectsView(ModelView):
    column_list = ('objid','projid', 'sampleid','classif_qual','objdate','acquisid','processid')
    column_filters = ('objid','projid','sampleid', 'classif_qual','acquisid','processid')
    form_overrides = dict(complement_info  =TextAreaField )
    form_excluded_columns=('classif_id','classif_auto','processrel','acquis','img0','images','sample','classiffier','objfrel')
    form_ajax_refs = { 'classif': { 'fields': ( 'name',) } }

    def __init__(self, session, **kwargs):
        super(ObjectsView, self).__init__(database.Objects, session, **kwargs)

class ObjectsFieldsView(ModelView):
    column_list = ('objfid','orig_id')
    column_filters = ('objfid','orig_id')
    column_searchable_list = ('orig_id',)
    form_excluded_columns=('objhrel', )
    def __init__(self, session, **kwargs):
        super(ObjectsFieldsView, self).__init__(database.ObjectsFields, session, **kwargs)

# Create admin
adminApp = flask.ext.admin.Admin(app, name='Ecotaxa Administration')

# Add views
#admin.add_view(sqla.ModelView(database.users, db.session))
adminApp.add_view(UsersView(db.session))
adminApp.add_view(ProjectsView(db.session))
adminApp.add_view(ObjectsView(db.session,category='Objects'))
adminApp.add_view(ObjectsFieldsView(db.session,category='Objects'))
adminApp.add_view(SamplesView(db.session,category='Objects'))
adminApp.add_view(ProcessView(db.session,category='Objects'))
adminApp.add_view(AcquisitionsView(db.session,category='Objects'))
adminApp.add_view(TaxonomyView(db.session))
adminApp.add_link(base.MenuLink('Ecotaxa Home', url='/'))
adminApp.add_link(base.MenuLink('View DB Size', category='Database', url='/dbadmin/viewsizes'))
adminApp.add_link(base.MenuLink('View DB Bloat', category='Database', url='/dbadmin/viewbloat'))
adminApp.add_link(base.MenuLink('Recompute Projects and Taxo stat (can be long)', category='Database', url='/dbadmin/recomputestat'))




#admin.add_view(CategoriesAdmin(Categories, db.session))
