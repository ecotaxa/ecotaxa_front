from typing import List

from flask import request, flash
from flask_admin.helpers import get_form_data
from flask_login import current_user
from wtforms import PasswordField, TextAreaField, SelectField, ValidationError, EmailField, SelectMultipleField, \
    HiddenField

import appli.constants
from appli import constants
from appli.admin.admin_views import SecureStrippingBaseForm
from appli.admin.views.from_api_model import APIModelView
from appli.back_config import get_country_names
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UsersApi, UserModelWithRights, ApiException


class UsersView(APIModelView):
    # Enable model creation
    can_create = True
    # Disable model deletion - A user might be referenced by an exported-then-deleted dataset
    can_delete = False
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    # Form tuning - List View
    column_exclude_list = ('usercreationreason', 'last_used_projects', 'can_do', 'password')
    column_searchable_list = ('email', 'name')
    # Form tuning - Detail view
    form_excluded_columns = ('last_used_projects')
    form_overrides = {
        'id': HiddenField,
        'email': EmailField,
        'password': PasswordField,
        'usercreationreason': TextAreaField,
        'country': SelectField,
        'can_do': SelectMultipleField
    }
    # Additions
    mandatory_columns = ('email', 'name', 'usercreationdate')

    def __init__(self):
        super(UsersView, self).__init__(model=UserModelWithRights, name="Users")

    def update_model(self, form, model):
        """ Called on "save" of existing model """
        # No way to modify data from the POST, other than referencing this private member
        # noinspection PyProtectedMember
        form_fields = form._fields
        # Change password _only_ if it's been filled, with confirmation, as browsers tend to remember password
        if not (form_fields['password'].data and form_fields['password_confirm'].data):
            form_fields['password'].data = None
        # The forms stores a datetime, the API needs a str
        form_fields['usercreationdate'].data = form_fields['usercreationdate'].data.isoformat() + " 00:00:00"
        try:
            with ApiClient(UsersApi, request) as api:
                ret = api.update_user(user_id=form.data['id'],
                                      user_model_with_rights=form.data)
        except ApiException as ae:
            flash(str(ae), 'error')

    def create_model(self, form):
        """ Called on "save" of new model """
        # noinspection PyProtectedMember
        form_fields = form._fields
        # The forms stores a datetime, the API needs a str
        form_fields['usercreationdate'].data = form_fields['usercreationdate'].data.isoformat() + " 00:00:00"
        form_fields['id'].data = -1
        try:
            with ApiClient(UsersApi, request) as api:
                ret = api.create_user(user_model_with_rights=form.data)
        except ApiException as ae:
            flash(str(ae), 'error')

    @staticmethod
    def check_password_confirm(form, field):
        if form.id.data:
            # Exiting user
            if form.password.data and field.data and field.data != form.password.data:
                raise ValidationError("Password Confirmation doesn't match")
        else:
            # New user
            if field.data != form.password.data:
                raise ValidationError("Password Confirmation doesn't match")

    def edit_form(self, obj=None):
        form = self._edit_form_class(get_form_data(), obj=obj)
        countries = [(nm, nm) for nm in get_country_names(request)]
        countries.sort()
        form.country.choices = [('', '')] + countries
        form.can_do.label.text = "Roles"
        form.can_do.choices = [(str(num), lbl) for num, lbl in constants.API_GLOBAL_ROLES.items()]
        return form

    def create_form(self, obj=None):
        return self.edit_form(obj)

    def is_accessible(self):
        return current_user.has_role(appli.constants.AdministratorLabel)

    edit_template = 'admin2/users_edit.html'
    create_template = 'admin2/users_create.html'

    # Added methods to compensate the lack of DB behind

    def scaffold_form(self):
        form_class = super(UsersView, self).scaffold_form()
        form_class.password_confirm = PasswordField('Password Confirmation',
                                                    validators=[self.check_password_confirm])
        return form_class

    def init_search(self):
        return True

    def search_placeholder(self):
        return ", ".join(self.column_searchable_list)

    def get_filters(self):
        return None

    def get_list(self, page, sort_field, sort_desc, search, filters,
                 page_size=None):
        """
            Return a paginated and sorted list of models from the data source.

            :param page:
                Page number, 0 based. Can be set to None if it is first page.
            :param sort_field:
                Sort column name or None.
            :param sort_desc:
                If set to True, sorting is in descending order.
            :param search:
                Search query
            :param filters:
                List of filter tuples. First value in a tuple is a search
                index, second value is a search value.
            :param page_size:
                Number of results. Defaults to ModelView's page_size. Can be
                overriden to change the page_size limit. Removing the page_size
                limit requires setting page_size to 0 or False.
        """
        # We have no server-side filtering or pagination, so read all and do in-memory operations
        with ApiClient(UsersApi, request) as api:
            ret: List[UserModelWithRights] = api.get_users()
        page = 0 if page is None else page
        if search:
            ret = self.search_in_models(ret, self.column_searchable_list, search)
        if sort_field:
            self.sort_model_list(ret, sort_field, sort_desc)
        ret_len = len(ret)
        if page_size:
            from_ = page_size * page
            to_ = from_ + page_size
        else:
            from_ = 0
            to_ = self.page_size
        return ret_len, ret[from_:to_]

    def get_pk_value(self, model):
        return model.id

    def get_one(self, id_):
        with ApiClient(UsersApi, request) as api:
            ret: List[UserModelWithRights] = api.get_users(ids=str(id_))
        return ret[0]

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def _create_ajax_loader(self, name, options):
        pass

    def delete_model(self, model):
        # Cannot delete
        raise


class UsersViewRestricted(UsersView):
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    form_columns = ('email', 'name', 'organisation', 'active', 'password')

    def __init__(self):
        # You can pass name and other parameters if you want to
        super(UsersViewRestricted, self).__init__()

    def is_accessible(self):
        return (not current_user.has_role(appli.constants.AdministratorLabel)) \
               and current_user.has_role(appli.constants.UserAdministratorLabel)
