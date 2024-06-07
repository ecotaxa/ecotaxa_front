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


class SubsetReq(object):
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
        'filters': 'ProjectFiltersDict',
        'dest_prj_id': 'int',
        'group_type': 'GroupDefinitions',
        'limit_type': 'LimitMethods',
        'limit_value': 'float'
    }

    attribute_map = {
        'filters': 'filters',
        'dest_prj_id': 'dest_prj_id',
        'group_type': 'group_type',
        'limit_type': 'limit_type',
        'limit_value': 'limit_value'
    }

    def __init__(self, filters=None, dest_prj_id=None, group_type=None, limit_type=None, limit_value=None, local_vars_configuration=None):  # noqa: E501
        """SubsetReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._filters = None
        self._dest_prj_id = None
        self._group_type = None
        self._limit_type = None
        self._limit_value = None
        self.discriminator = None

        if filters is not None:
            self.filters = filters
        self.dest_prj_id = dest_prj_id
        self.group_type = group_type
        self.limit_type = limit_type
        self.limit_value = limit_value

    @property
    def filters(self):
        """Gets the filters of this SubsetReq.  # noqa: E501

        The filters to apply to project.  # noqa: E501

        :return: The filters of this SubsetReq.  # noqa: E501
        :rtype: ProjectFiltersDict
        """
        return self._filters

    @filters.setter
    def filters(self, filters):
        """Sets the filters of this SubsetReq.

        The filters to apply to project.  # noqa: E501

        :param filters: The filters of this SubsetReq.  # noqa: E501
        :type: ProjectFiltersDict
        """

        self._filters = filters

    @property
    def dest_prj_id(self):
        """Gets the dest_prj_id of this SubsetReq.  # noqa: E501

        The destination project ID.  # noqa: E501

        :return: The dest_prj_id of this SubsetReq.  # noqa: E501
        :rtype: int
        """
        return self._dest_prj_id

    @dest_prj_id.setter
    def dest_prj_id(self, dest_prj_id):
        """Sets the dest_prj_id of this SubsetReq.

        The destination project ID.  # noqa: E501

        :param dest_prj_id: The dest_prj_id of this SubsetReq.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and dest_prj_id is None:  # noqa: E501
            raise ValueError("Invalid value for `dest_prj_id`, must not be `None`")  # noqa: E501

        self._dest_prj_id = dest_prj_id

    @property
    def group_type(self):
        """Gets the group_type of this SubsetReq.  # noqa: E501

        Define the groups in which to apply limits. C for categories, S for samples, A for acquisitions.  # noqa: E501

        :return: The group_type of this SubsetReq.  # noqa: E501
        :rtype: GroupDefinitions
        """
        return self._group_type

    @group_type.setter
    def group_type(self, group_type):
        """Sets the group_type of this SubsetReq.

        Define the groups in which to apply limits. C for categories, S for samples, A for acquisitions.  # noqa: E501

        :param group_type: The group_type of this SubsetReq.  # noqa: E501
        :type: GroupDefinitions
        """
        if self.local_vars_configuration.client_side_validation and group_type is None:  # noqa: E501
            raise ValueError("Invalid value for `group_type`, must not be `None`")  # noqa: E501

        self._group_type = group_type

    @property
    def limit_type(self):
        """Gets the limit_type of this SubsetReq.  # noqa: E501

        The type of limit_value: P for %, V for constant, both per group.  # noqa: E501

        :return: The limit_type of this SubsetReq.  # noqa: E501
        :rtype: LimitMethods
        """
        return self._limit_type

    @limit_type.setter
    def limit_type(self, limit_type):
        """Sets the limit_type of this SubsetReq.

        The type of limit_value: P for %, V for constant, both per group.  # noqa: E501

        :param limit_type: The limit_type of this SubsetReq.  # noqa: E501
        :type: LimitMethods
        """
        if self.local_vars_configuration.client_side_validation and limit_type is None:  # noqa: E501
            raise ValueError("Invalid value for `limit_type`, must not be `None`")  # noqa: E501

        self._limit_type = limit_type

    @property
    def limit_value(self):
        """Gets the limit_value of this SubsetReq.  # noqa: E501

        Limit value, e.g. 20% or 5 per copepoda or 5% per sample.  # noqa: E501

        :return: The limit_value of this SubsetReq.  # noqa: E501
        :rtype: float
        """
        return self._limit_value

    @limit_value.setter
    def limit_value(self, limit_value):
        """Sets the limit_value of this SubsetReq.

        Limit value, e.g. 20% or 5 per copepoda or 5% per sample.  # noqa: E501

        :param limit_value: The limit_value of this SubsetReq.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and limit_value is None:  # noqa: E501
            raise ValueError("Invalid value for `limit_value`, must not be `None`")  # noqa: E501

        self._limit_value = limit_value

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
        if not isinstance(other, SubsetReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SubsetReq):
            return True

        return self.to_dict() != other.to_dict()
