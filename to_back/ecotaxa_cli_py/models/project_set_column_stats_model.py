# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.35
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ProjectSetColumnStatsModel(object):
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
        'proj_ids': 'list[int]',
        'total': 'int',
        'columns': 'list[str]',
        'counts': 'list[int]',
        'variances': 'list[float]'
    }

    attribute_map = {
        'proj_ids': 'proj_ids',
        'total': 'total',
        'columns': 'columns',
        'counts': 'counts',
        'variances': 'variances'
    }

    def __init__(self, proj_ids=None, total=None, columns=None, counts=None, variances=None, local_vars_configuration=None):  # noqa: E501
        """ProjectSetColumnStatsModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._proj_ids = None
        self._total = None
        self._columns = None
        self._counts = None
        self._variances = None
        self.discriminator = None

        if proj_ids is not None:
            self.proj_ids = proj_ids
        if total is not None:
            self.total = total
        if columns is not None:
            self.columns = columns
        if counts is not None:
            self.counts = counts
        if variances is not None:
            self.variances = variances

    @property
    def proj_ids(self):
        """Gets the proj_ids of this ProjectSetColumnStatsModel.  # noqa: E501

        Projects IDs from the call.  # noqa: E501

        :return: The proj_ids of this ProjectSetColumnStatsModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._proj_ids

    @proj_ids.setter
    def proj_ids(self, proj_ids):
        """Sets the proj_ids of this ProjectSetColumnStatsModel.

        Projects IDs from the call.  # noqa: E501

        :param proj_ids: The proj_ids of this ProjectSetColumnStatsModel.  # noqa: E501
        :type: list[int]
        """

        self._proj_ids = proj_ids

    @property
    def total(self):
        """Gets the total of this ProjectSetColumnStatsModel.  # noqa: E501

        All rows regardless of emptiness.  # noqa: E501

        :return: The total of this ProjectSetColumnStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this ProjectSetColumnStatsModel.

        All rows regardless of emptiness.  # noqa: E501

        :param total: The total of this ProjectSetColumnStatsModel.  # noqa: E501
        :type: int
        """

        self._total = total

    @property
    def columns(self):
        """Gets the columns of this ProjectSetColumnStatsModel.  # noqa: E501

        Column names from the call.  # noqa: E501

        :return: The columns of this ProjectSetColumnStatsModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """Sets the columns of this ProjectSetColumnStatsModel.

        Column names from the call.  # noqa: E501

        :param columns: The columns of this ProjectSetColumnStatsModel.  # noqa: E501
        :type: list[str]
        """

        self._columns = columns

    @property
    def counts(self):
        """Gets the counts of this ProjectSetColumnStatsModel.  # noqa: E501

        Counts of non-empty values, one per column.  # noqa: E501

        :return: The counts of this ProjectSetColumnStatsModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._counts

    @counts.setter
    def counts(self, counts):
        """Sets the counts of this ProjectSetColumnStatsModel.

        Counts of non-empty values, one per column.  # noqa: E501

        :param counts: The counts of this ProjectSetColumnStatsModel.  # noqa: E501
        :type: list[int]
        """

        self._counts = counts

    @property
    def variances(self):
        """Gets the variances of this ProjectSetColumnStatsModel.  # noqa: E501

        Variances of values, one per column.  # noqa: E501

        :return: The variances of this ProjectSetColumnStatsModel.  # noqa: E501
        :rtype: list[float]
        """
        return self._variances

    @variances.setter
    def variances(self, variances):
        """Sets the variances of this ProjectSetColumnStatsModel.

        Variances of values, one per column.  # noqa: E501

        :param variances: The variances of this ProjectSetColumnStatsModel.  # noqa: E501
        :type: list[float]
        """

        self._variances = variances

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
        if not isinstance(other, ProjectSetColumnStatsModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectSetColumnStatsModel):
            return True

        return self.to_dict() != other.to_dict()
