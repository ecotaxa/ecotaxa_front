# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.23
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class Constants(object):
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
        'license_texts': 'dict(str, str)',
        'app_manager': 'list[str]'
    }

    attribute_map = {
        'license_texts': 'license_texts',
        'app_manager': 'app_manager'
    }

    def __init__(self, license_texts=None, app_manager=["",""], local_vars_configuration=None):  # noqa: E501
        """Constants - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._license_texts = None
        self._app_manager = None
        self.discriminator = None

        if license_texts is not None:
            self.license_texts = license_texts
        if app_manager is not None:
            self.app_manager = app_manager

    @property
    def license_texts(self):
        """Gets the license_texts of this Constants.  # noqa: E501

        The supported licenses and help text/links.  # noqa: E501

        :return: The license_texts of this Constants.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._license_texts

    @license_texts.setter
    def license_texts(self, license_texts):
        """Sets the license_texts of this Constants.

        The supported licenses and help text/links.  # noqa: E501

        :param license_texts: The license_texts of this Constants.  # noqa: E501
        :type: dict(str, str)
        """

        self._license_texts = license_texts

    @property
    def app_manager(self):
        """Gets the app_manager of this Constants.  # noqa: E501

        The application manager identity (name, mail), from config file.  # noqa: E501

        :return: The app_manager of this Constants.  # noqa: E501
        :rtype: list[str]
        """
        return self._app_manager

    @app_manager.setter
    def app_manager(self, app_manager):
        """Sets the app_manager of this Constants.

        The application manager identity (name, mail), from config file.  # noqa: E501

        :param app_manager: The app_manager of this Constants.  # noqa: E501
        :type: list[str]
        """

        self._app_manager = app_manager

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
        if not isinstance(other, Constants):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Constants):
            return True

        return self.to_dict() != other.to_dict()
