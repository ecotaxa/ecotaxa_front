# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.17
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class UserActivity(object):
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
        'nb_actions': 'int',
        'last_annot': 'str'
    }

    attribute_map = {
        'id': 'id',
        'nb_actions': 'nb_actions',
        'last_annot': 'last_annot'
    }

    def __init__(self, id=None, nb_actions=None, last_annot=None, local_vars_configuration=None):  # noqa: E501
        """UserActivity - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._nb_actions = None
        self._last_annot = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if nb_actions is not None:
            self.nb_actions = nb_actions
        if last_annot is not None:
            self.last_annot = last_annot

    @property
    def id(self):
        """Gets the id of this UserActivity.  # noqa: E501


        :return: The id of this UserActivity.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this UserActivity.


        :param id: The id of this UserActivity.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def nb_actions(self):
        """Gets the nb_actions of this UserActivity.  # noqa: E501


        :return: The nb_actions of this UserActivity.  # noqa: E501
        :rtype: int
        """
        return self._nb_actions

    @nb_actions.setter
    def nb_actions(self, nb_actions):
        """Sets the nb_actions of this UserActivity.


        :param nb_actions: The nb_actions of this UserActivity.  # noqa: E501
        :type: int
        """

        self._nb_actions = nb_actions

    @property
    def last_annot(self):
        """Gets the last_annot of this UserActivity.  # noqa: E501


        :return: The last_annot of this UserActivity.  # noqa: E501
        :rtype: str
        """
        return self._last_annot

    @last_annot.setter
    def last_annot(self, last_annot):
        """Sets the last_annot of this UserActivity.


        :param last_annot: The last_annot of this UserActivity.  # noqa: E501
        :type: str
        """

        self._last_annot = last_annot

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
        if not isinstance(other, UserActivity):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserActivity):
            return True

        return self.to_dict() != other.to_dict()
