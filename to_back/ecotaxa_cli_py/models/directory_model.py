# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.37
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class DirectoryModel(object):
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
        'path': 'str',
        'entries': 'list[DirectoryEntryModel]'
    }

    attribute_map = {
        'path': 'path',
        'entries': 'entries'
    }

    def __init__(self, path=None, entries=None, local_vars_configuration=None):  # noqa: E501
        """DirectoryModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._path = None
        self._entries = None
        self.discriminator = None

        self.path = path
        self.entries = entries

    @property
    def path(self):
        """Gets the path of this DirectoryModel.  # noqa: E501

        A /-separated path from root to this directory.  # noqa: E501

        :return: The path of this DirectoryModel.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this DirectoryModel.

        A /-separated path from root to this directory.  # noqa: E501

        :param path: The path of this DirectoryModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and path is None:  # noqa: E501
            raise ValueError("Invalid value for `path`, must not be `None`")  # noqa: E501

        self._path = path

    @property
    def entries(self):
        """Gets the entries of this DirectoryModel.  # noqa: E501

        Entries, i.e. subdirectories or contained files.All entries are readable, i.e. can be used as input or navigated into.  # noqa: E501

        :return: The entries of this DirectoryModel.  # noqa: E501
        :rtype: list[DirectoryEntryModel]
        """
        return self._entries

    @entries.setter
    def entries(self, entries):
        """Sets the entries of this DirectoryModel.

        Entries, i.e. subdirectories or contained files.All entries are readable, i.e. can be used as input or navigated into.  # noqa: E501

        :param entries: The entries of this DirectoryModel.  # noqa: E501
        :type: list[DirectoryEntryModel]
        """
        if self.local_vars_configuration.client_side_validation and entries is None:  # noqa: E501
            raise ValueError("Invalid value for `entries`, must not be `None`")  # noqa: E501

        self._entries = entries

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
        if not isinstance(other, DirectoryModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DirectoryModel):
            return True

        return self.to_dict() != other.to_dict()
