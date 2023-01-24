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


class SimpleImportReq(object):
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
        'source_path': 'str',
        'values': 'dict(str, str)',
        'possible_values': 'list[str]'
    }

    attribute_map = {
        'source_path': 'source_path',
        'values': 'values',
        'possible_values': 'possible_values'
    }

    def __init__(self, source_path=None, values=None, possible_values=["imgdate","imgtime","latitude","longitude","depthmin","depthmax","taxolb","userlb","status"], local_vars_configuration=None):  # noqa: E501
        """SimpleImportReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._source_path = None
        self._values = None
        self._possible_values = None
        self.discriminator = None

        self.source_path = source_path
        self.values = values
        if possible_values is not None:
            self.possible_values = possible_values

    @property
    def source_path(self):
        """Gets the source_path of this SimpleImportReq.  # noqa: E501

        Source path on server, to zip or plain directory.  # noqa: E501

        :return: The source_path of this SimpleImportReq.  # noqa: E501
        :rtype: str
        """
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        """Sets the source_path of this SimpleImportReq.

        Source path on server, to zip or plain directory.  # noqa: E501

        :param source_path: The source_path of this SimpleImportReq.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and source_path is None:  # noqa: E501
            raise ValueError("Invalid value for `source_path`, must not be `None`")  # noqa: E501

        self._source_path = source_path

    @property
    def values(self):
        """Gets the values of this SimpleImportReq.  # noqa: E501

        :imgdate, imgtime, latitude, longitude, depthmin, depthmax, taxolb, userlb, status  # noqa: E501

        :return: The values of this SimpleImportReq.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._values

    @values.setter
    def values(self, values):
        """Sets the values of this SimpleImportReq.

        :imgdate, imgtime, latitude, longitude, depthmin, depthmax, taxolb, userlb, status  # noqa: E501

        :param values: The values of this SimpleImportReq.  # noqa: E501
        :type: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and values is None:  # noqa: E501
            raise ValueError("Invalid value for `values`, must not be `None`")  # noqa: E501

        self._values = values

    @property
    def possible_values(self):
        """Gets the possible_values of this SimpleImportReq.  # noqa: E501


        :return: The possible_values of this SimpleImportReq.  # noqa: E501
        :rtype: list[str]
        """
        return self._possible_values

    @possible_values.setter
    def possible_values(self, possible_values):
        """Sets the possible_values of this SimpleImportReq.


        :param possible_values: The possible_values of this SimpleImportReq.  # noqa: E501
        :type: list[str]
        """

        self._possible_values = possible_values

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
        if not isinstance(other, SimpleImportReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SimpleImportReq):
            return True

        return self.to_dict() != other.to_dict()
