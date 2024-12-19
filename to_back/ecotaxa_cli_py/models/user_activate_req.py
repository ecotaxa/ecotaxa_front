# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.39
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class UserActivateReq(object):
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
        'token': 'str',
        'reason': 'str',
        'password': 'str'
    }

    attribute_map = {
        'token': 'token',
        'reason': 'reason',
        'password': 'password'
    }

    def __init__(self, token=None, reason=None, password=None, local_vars_configuration=None):  # noqa: E501
        """UserActivateReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._token = None
        self._reason = None
        self._password = None
        self.discriminator = None

        if token is not None:
            self.token = token
        if reason is not None:
            self.reason = reason
        if password is not None:
            self.password = password

    @property
    def token(self):
        """Gets the token of this UserActivateReq.  # noqa: E501

        token when the user is not an admin and must confirm the email.   # noqa: E501

        :return: The token of this UserActivateReq.  # noqa: E501
        :rtype: str
        """
        return self._token

    @token.setter
    def token(self, token):
        """Sets the token of this UserActivateReq.

        token when the user is not an admin and must confirm the email.   # noqa: E501

        :param token: The token of this UserActivateReq.  # noqa: E501
        :type: str
        """

        self._token = token

    @property
    def reason(self):
        """Gets the reason of this UserActivateReq.  # noqa: E501

        status,optional users administrator comment related to the status.   # noqa: E501

        :return: The reason of this UserActivateReq.  # noqa: E501
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """Sets the reason of this UserActivateReq.

        status,optional users administrator comment related to the status.   # noqa: E501

        :param reason: The reason of this UserActivateReq.  # noqa: E501
        :type: str
        """

        self._reason = reason

    @property
    def password(self):
        """Gets the password of this UserActivateReq.  # noqa: E501

        Existing user can modify own email and must confirm it with token and password when email confirmation is on.   # noqa: E501

        :return: The password of this UserActivateReq.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this UserActivateReq.

        Existing user can modify own email and must confirm it with token and password when email confirmation is on.   # noqa: E501

        :param password: The password of this UserActivateReq.  # noqa: E501
        :type: str
        """

        self._password = password

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
        if not isinstance(other, UserActivateReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserActivateReq):
            return True

        return self.to_dict() != other.to_dict()
