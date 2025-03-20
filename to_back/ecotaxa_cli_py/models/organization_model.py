# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.41
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class OrganizationModel(object):
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
        'name': 'str',
        'directories': 'str'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'directories': 'directories'
    }

    def __init__(self, id=None, name=None, directories=None, local_vars_configuration=None):  # noqa: E501
        """OrganizationModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._directories = None
        self.discriminator = None

        self.id = id
        self.name = name
        if directories is not None:
            self.directories = directories

    @property
    def id(self):
        """Gets the id of this OrganizationModel.  # noqa: E501

        OrganizationIDT unique identifier.  # noqa: E501

        :return: The id of this OrganizationModel.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OrganizationModel.

        OrganizationIDT unique identifier.  # noqa: E501

        :param id: The id of this OrganizationModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this OrganizationModel.  # noqa: E501

        Organization's full name, as text.  # noqa: E501

        :return: The name of this OrganizationModel.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this OrganizationModel.

        Organization's full name, as text.  # noqa: E501

        :param name: The name of this OrganizationModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def directories(self):
        """Gets the directories of this OrganizationModel.  # noqa: E501

        References to official directories where the organization is referenced, separated by ,.  # noqa: E501

        :return: The directories of this OrganizationModel.  # noqa: E501
        :rtype: str
        """
        return self._directories

    @directories.setter
    def directories(self, directories):
        """Sets the directories of this OrganizationModel.

        References to official directories where the organization is referenced, separated by ,.  # noqa: E501

        :param directories: The directories of this OrganizationModel.  # noqa: E501
        :type: str
        """

        self._directories = directories

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
        if not isinstance(other, OrganizationModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OrganizationModel):
            return True

        return self.to_dict() != other.to_dict()
