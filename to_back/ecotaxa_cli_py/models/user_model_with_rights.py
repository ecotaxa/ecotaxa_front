# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.34
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class UserModelWithRights(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'id': 'int',
        'email': 'str',
        'password': 'str',
        'name': 'str',
        'organisation': 'str',
        'status': 'int',
        'status_date': 'datetime',
        'status_admin_comment': 'str',
        'country': 'str',
        'usercreationdate': 'datetime',
        'usercreationreason': 'str',
        'mail_status': 'bool',
        'mail_status_date': 'datetime',
        'can_do': 'list[int]',
        'last_used_projects': 'list[ProjectSummaryModel]'
    }

    attribute_map = {
        'id': 'id',
        'email': 'email',
        'password': 'password',
        'name': 'name',
        'organisation': 'organisation',
        'status': 'status',
        'status_date': 'status_date',
        'status_admin_comment': 'status_admin_comment',
        'country': 'country',
        'usercreationdate': 'usercreationdate',
        'usercreationreason': 'usercreationreason',
        'mail_status': 'mail_status',
        'mail_status_date': 'mail_status_date',
        'can_do': 'can_do',
        'last_used_projects': 'last_used_projects'
    }

    def __init__(self, id=None, email=None, password=None, name=None, organisation=None, status=None, status_date=None, status_admin_comment=None, country=None, usercreationdate=None, usercreationreason=None, mail_status=None, mail_status_date=None, can_do=[], last_used_projects=[], local_vars_configuration=None):  # noqa: E501
        """UserModelWithRights - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._email = None
        self._password = None
        self._name = None
        self._organisation = None
        self._status = None
        self._status_date = None
        self._status_admin_comment = None
        self._country = None
        self._usercreationdate = None
        self._usercreationreason = None
        self._mail_status = None
        self._mail_status_date = None
        self._can_do = None
        self._last_used_projects = None
        self.discriminator = None

        self.id = id
        self.email = email
        if password is not None:
            self.password = password
        self.name = name
        if organisation is not None:
            self.organisation = organisation
        if status is not None:
            self.status = status
        if status_date is not None:
            self.status_date = status_date
        if status_admin_comment is not None:
            self.status_admin_comment = status_admin_comment
        if country is not None:
            self.country = country
        if usercreationdate is not None:
            self.usercreationdate = usercreationdate
        if usercreationreason is not None:
            self.usercreationreason = usercreationreason
        if mail_status is not None:
            self.mail_status = mail_status
        if mail_status_date is not None:
            self.mail_status_date = mail_status_date
        if can_do is not None:
            self.can_do = can_do
        if last_used_projects is not None:
            self.last_used_projects = last_used_projects

    @property
    def id(self):
        """Gets the id of this UserModelWithRights.  # noqa: E501

        The unique numeric id of this user.  # noqa: E501

        :return: The id of this UserModelWithRights.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this UserModelWithRights.

        The unique numeric id of this user.  # noqa: E501

        :param id: The id of this UserModelWithRights.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def email(self):
        """Gets the email of this UserModelWithRights.  # noqa: E501

        User's email address, as text, used during registration.  # noqa: E501

        :return: The email of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this UserModelWithRights.

        User's email address, as text, used during registration.  # noqa: E501

        :param email: The email of this UserModelWithRights.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and email is None:  # noqa: E501
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501

        self._email = email

    @property
    def password(self):
        """Gets the password of this UserModelWithRights.  # noqa: E501

        Encrypted (or not) password.  # noqa: E501

        :return: The password of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this UserModelWithRights.

        Encrypted (or not) password.  # noqa: E501

        :param password: The password of this UserModelWithRights.  # noqa: E501
        :type: str
        """

        self._password = password

    @property
    def name(self):
        """Gets the name of this UserModelWithRights.  # noqa: E501

        User's full name, as text.  # noqa: E501

        :return: The name of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UserModelWithRights.

        User's full name, as text.  # noqa: E501

        :param name: The name of this UserModelWithRights.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def organisation(self):
        """Gets the organisation of this UserModelWithRights.  # noqa: E501

        User's organisation name, as text.  # noqa: E501

        :return: The organisation of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._organisation

    @organisation.setter
    def organisation(self, organisation):
        """Sets the organisation of this UserModelWithRights.

        User's organisation name, as text.  # noqa: E501

        :param organisation: The organisation of this UserModelWithRights.  # noqa: E501
        :type: str
        """

        self._organisation = organisation

    @property
    def status(self):
        """Gets the status of this UserModelWithRights.  # noqa: E501

        Status of the user : 1 for active, 0 for inactive ,2 for pending, -1 for blocked  # noqa: E501

        :return: The status of this UserModelWithRights.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this UserModelWithRights.

        Status of the user : 1 for active, 0 for inactive ,2 for pending, -1 for blocked  # noqa: E501

        :param status: The status of this UserModelWithRights.  # noqa: E501
        :type: int
        """

        self._status = status

    @property
    def status_date(self):
        """Gets the status_date of this UserModelWithRights.  # noqa: E501

        Timestamp status modification date  # noqa: E501

        :return: The status_date of this UserModelWithRights.  # noqa: E501
        :rtype: datetime
        """
        return self._status_date

    @status_date.setter
    def status_date(self, status_date):
        """Sets the status_date of this UserModelWithRights.

        Timestamp status modification date  # noqa: E501

        :param status_date: The status_date of this UserModelWithRights.  # noqa: E501
        :type: datetime
        """

        self._status_date = status_date

    @property
    def status_admin_comment(self):
        """Gets the status_admin_comment of this UserModelWithRights.  # noqa: E501

        Optional Users admininistrator comment about the account status.  # noqa: E501

        :return: The status_admin_comment of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._status_admin_comment

    @status_admin_comment.setter
    def status_admin_comment(self, status_admin_comment):
        """Sets the status_admin_comment of this UserModelWithRights.

        Optional Users admininistrator comment about the account status.  # noqa: E501

        :param status_admin_comment: The status_admin_comment of this UserModelWithRights.  # noqa: E501
        :type: str
        """

        self._status_admin_comment = status_admin_comment

    @property
    def country(self):
        """Gets the country of this UserModelWithRights.  # noqa: E501

        The country name, as text (but chosen in a consistent list).  # noqa: E501

        :return: The country of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """Sets the country of this UserModelWithRights.

        The country name, as text (but chosen in a consistent list).  # noqa: E501

        :param country: The country of this UserModelWithRights.  # noqa: E501
        :type: str
        """

        self._country = country

    @property
    def usercreationdate(self):
        """Gets the usercreationdate of this UserModelWithRights.  # noqa: E501

        The date of creation of the user, as text formatted according to the ISO 8601 standard.  # noqa: E501

        :return: The usercreationdate of this UserModelWithRights.  # noqa: E501
        :rtype: datetime
        """
        return self._usercreationdate

    @usercreationdate.setter
    def usercreationdate(self, usercreationdate):
        """Sets the usercreationdate of this UserModelWithRights.

        The date of creation of the user, as text formatted according to the ISO 8601 standard.  # noqa: E501

        :param usercreationdate: The usercreationdate of this UserModelWithRights.  # noqa: E501
        :type: datetime
        """

        self._usercreationdate = usercreationdate

    @property
    def usercreationreason(self):
        """Gets the usercreationreason of this UserModelWithRights.  # noqa: E501

        Paragraph describing the usage of EcoTaxa made by the user.  # noqa: E501

        :return: The usercreationreason of this UserModelWithRights.  # noqa: E501
        :rtype: str
        """
        return self._usercreationreason

    @usercreationreason.setter
    def usercreationreason(self, usercreationreason):
        """Sets the usercreationreason of this UserModelWithRights.

        Paragraph describing the usage of EcoTaxa made by the user.  # noqa: E501

        :param usercreationreason: The usercreationreason of this UserModelWithRights.  # noqa: E501
        :type: str
        """

        self._usercreationreason = usercreationreason

    @property
    def mail_status(self):
        """Gets the mail_status of this UserModelWithRights.  # noqa: E501

        True for verified, False for waiting for verification, None for no action.  # noqa: E501

        :return: The mail_status of this UserModelWithRights.  # noqa: E501
        :rtype: bool
        """
        return self._mail_status

    @mail_status.setter
    def mail_status(self, mail_status):
        """Sets the mail_status of this UserModelWithRights.

        True for verified, False for waiting for verification, None for no action.  # noqa: E501

        :param mail_status: The mail_status of this UserModelWithRights.  # noqa: E501
        :type: bool
        """

        self._mail_status = mail_status

    @property
    def mail_status_date(self):
        """Gets the mail_status_date of this UserModelWithRights.  # noqa: E501

        Timestamp mail status modification date  # noqa: E501

        :return: The mail_status_date of this UserModelWithRights.  # noqa: E501
        :rtype: datetime
        """
        return self._mail_status_date

    @mail_status_date.setter
    def mail_status_date(self, mail_status_date):
        """Sets the mail_status_date of this UserModelWithRights.

        Timestamp mail status modification date  # noqa: E501

        :param mail_status_date: The mail_status_date of this UserModelWithRights.  # noqa: E501
        :type: datetime
        """

        self._mail_status_date = mail_status_date

    @property
    def can_do(self):
        """Gets the can_do of this UserModelWithRights.  # noqa: E501

        List of User's allowed actions : 1 create a project, 2 administrate the app, 3 administrate users, 4 create taxon.  # noqa: E501

        :return: The can_do of this UserModelWithRights.  # noqa: E501
        :rtype: list[int]
        """
        return self._can_do

    @can_do.setter
    def can_do(self, can_do):
        """Sets the can_do of this UserModelWithRights.

        List of User's allowed actions : 1 create a project, 2 administrate the app, 3 administrate users, 4 create taxon.  # noqa: E501

        :param can_do: The can_do of this UserModelWithRights.  # noqa: E501
        :type: list[int]
        """

        self._can_do = can_do

    @property
    def last_used_projects(self):
        """Gets the last_used_projects of this UserModelWithRights.  # noqa: E501

        List of User's last used projects.  # noqa: E501

        :return: The last_used_projects of this UserModelWithRights.  # noqa: E501
        :rtype: list[ProjectSummaryModel]
        """
        return self._last_used_projects

    @last_used_projects.setter
    def last_used_projects(self, last_used_projects):
        """Sets the last_used_projects of this UserModelWithRights.

        List of User's last used projects.  # noqa: E501

        :param last_used_projects: The last_used_projects of this UserModelWithRights.  # noqa: E501
        :type: list[ProjectSummaryModel]
        """

        self._last_used_projects = last_used_projects

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UserModelWithRights):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserModelWithRights):
            return True

        return self.to_dict() != other.to_dict()
