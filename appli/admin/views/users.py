from flask import request
from flask_admin.helpers import get_form_data
from flask_login import current_user
from flask_security.utils import encrypt_password
from wtforms import StringField, PasswordField, TextAreaField, SelectField, ValidationError

import appli.constants
from appli.admin.admin_views import SecureStrippingBaseForm
from appli.admin.views.from_api_model import APIModelView
from appli.back_config import get_country_names
from appli.utils import ApiClient
from to_back.ecotaxa_cli_py import UserModel, UsersApi


class UsersView(APIModelView):
    # Enable model creation
    can_create = True
    # Disable model deletion - A user might be referenced by an exported-then-deleted dataset
    can_delete = False
    # Enable CSRF check
    form_base_class = SecureStrippingBaseForm

    # Override displayed fields
    column_list = ('email', 'name', 'organisation', 'active', 'roles', 'country')
    column_sortable_list = [a_col for a_col in column_list if a_col != 'roles']
    form_columns = ('email', 'mail_status', 'mail_status_date', 'name', 'organisation', 'active',
                    'roles', 'password', 'country', 'usercreationreason')
    column_searchable_list = ('email', 'name')
    form_overrides = {
        'email': StringField,
        'password': PasswordField,
        'usercreationreason': TextAreaField,
        'country': SelectField
    }

    def __init__(self):
        super(UsersView, self).__init__(model=UserModel, name="Users")

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
        countries = [(nm, nm) for nm in get_country_names(request)]
        countries.sort()
        form.country.choices = [('', '')] + countries
        return form

    def create_form(self, obj=None):
        return self.edit_form(obj)

    form_args = dict(
        password=dict(validators=[checkpasswordequal])
    )

    def is_accessible(self):
        return current_user.has_role(appli.constants.AdministratorLabel)

    edit_template = 'admin2/users_edit.html'
    create_template = 'admin2/users_create.html'

    # Added methods to compensate the lack of DB behind

    def scaffold_form(self):
        form_class = super(UsersView, self).scaffold_form()
        form_class.password_confirm = PasswordField('Password Confirmation')
        return form_class

    def scaffold_sortable_columns(self):
        return self.sortable_columns

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
            ret = api.get_users()
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
            ret = api.get_user(user_id=id_)
        return ret

    def scaffold_list_columns(self):
        pass

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
