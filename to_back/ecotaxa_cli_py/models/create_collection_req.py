# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.40
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class CreateCollectionReq(object):
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
        'title': 'str',
        'project_ids': 'list[int]'
    }

    attribute_map = {
        'title': 'title',
        'project_ids': 'project_ids'
    }

    def __init__(self, title=None, project_ids=None, local_vars_configuration=None):  # noqa: E501
        """CreateCollectionReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._title = None
        self._project_ids = None
        self.discriminator = None

        self.title = title
        self.project_ids = project_ids

    @property
    def title(self):
        """Gets the title of this CreateCollectionReq.  # noqa: E501

        The collection title.  # noqa: E501

        :return: The title of this CreateCollectionReq.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this CreateCollectionReq.

        The collection title.  # noqa: E501

        :param title: The title of this CreateCollectionReq.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and title is None:  # noqa: E501
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def project_ids(self):
        """Gets the project_ids of this CreateCollectionReq.  # noqa: E501

        The list of composing project IDs.  # noqa: E501

        :return: The project_ids of this CreateCollectionReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._project_ids

    @project_ids.setter
    def project_ids(self, project_ids):
        """Sets the project_ids of this CreateCollectionReq.

        The list of composing project IDs.  # noqa: E501

        :param project_ids: The project_ids of this CreateCollectionReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and project_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `project_ids`, must not be `None`")  # noqa: E501

        self._project_ids = project_ids

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
        if not isinstance(other, CreateCollectionReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateCollectionReq):
            return True

        return self.to_dict() != other.to_dict()
