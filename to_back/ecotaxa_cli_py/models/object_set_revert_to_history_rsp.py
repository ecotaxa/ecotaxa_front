# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.30
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ObjectSetRevertToHistoryRsp(object):
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
        'last_entries': 'list[HistoricalLastClassif]',
        'classif_info': 'object'
    }

    attribute_map = {
        'last_entries': 'last_entries',
        'classif_info': 'classif_info'
    }

    def __init__(self, last_entries=[], classif_info=None, local_vars_configuration=None):  # noqa: E501
        """ObjectSetRevertToHistoryRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._last_entries = None
        self._classif_info = None
        self.discriminator = None

        if last_entries is not None:
            self.last_entries = last_entries
        if classif_info is not None:
            self.classif_info = classif_info

    @property
    def last_entries(self):
        """Gets the last_entries of this ObjectSetRevertToHistoryRsp.  # noqa: E501

        Object + last classification  # noqa: E501

        :return: The last_entries of this ObjectSetRevertToHistoryRsp.  # noqa: E501
        :rtype: list[HistoricalLastClassif]
        """
        return self._last_entries

    @last_entries.setter
    def last_entries(self, last_entries):
        """Sets the last_entries of this ObjectSetRevertToHistoryRsp.

        Object + last classification  # noqa: E501

        :param last_entries: The last_entries of this ObjectSetRevertToHistoryRsp.  # noqa: E501
        :type: list[HistoricalLastClassif]
        """

        self._last_entries = last_entries

    @property
    def classif_info(self):
        """Gets the classif_info of this ObjectSetRevertToHistoryRsp.  # noqa: E501

        Classification names (self+parent) for involved IDs.  # noqa: E501

        :return: The classif_info of this ObjectSetRevertToHistoryRsp.  # noqa: E501
        :rtype: object
        """
        return self._classif_info

    @classif_info.setter
    def classif_info(self, classif_info):
        """Sets the classif_info of this ObjectSetRevertToHistoryRsp.

        Classification names (self+parent) for involved IDs.  # noqa: E501

        :param classif_info: The classif_info of this ObjectSetRevertToHistoryRsp.  # noqa: E501
        :type: object
        """

        self._classif_info = classif_info

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
        if not isinstance(other, ObjectSetRevertToHistoryRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ObjectSetRevertToHistoryRsp):
            return True

        return self.to_dict() != other.to_dict()
