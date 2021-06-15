# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.15
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ObjectSetSummaryRsp(object):
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
        'total_objects': 'int',
        'validated_objects': 'int',
        'dubious_objects': 'int',
        'predicted_objects': 'int'
    }

    attribute_map = {
        'total_objects': 'total_objects',
        'validated_objects': 'validated_objects',
        'dubious_objects': 'dubious_objects',
        'predicted_objects': 'predicted_objects'
    }

    def __init__(self, total_objects=None, validated_objects=None, dubious_objects=None, predicted_objects=None, local_vars_configuration=None):  # noqa: E501
        """ObjectSetSummaryRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._total_objects = None
        self._validated_objects = None
        self._dubious_objects = None
        self._predicted_objects = None
        self.discriminator = None

        if total_objects is not None:
            self.total_objects = total_objects
        if validated_objects is not None:
            self.validated_objects = validated_objects
        if dubious_objects is not None:
            self.dubious_objects = dubious_objects
        if predicted_objects is not None:
            self.predicted_objects = predicted_objects

    @property
    def total_objects(self):
        """Gets the total_objects of this ObjectSetSummaryRsp.  # noqa: E501


        :return: The total_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :rtype: int
        """
        return self._total_objects

    @total_objects.setter
    def total_objects(self, total_objects):
        """Sets the total_objects of this ObjectSetSummaryRsp.


        :param total_objects: The total_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :type: int
        """

        self._total_objects = total_objects

    @property
    def validated_objects(self):
        """Gets the validated_objects of this ObjectSetSummaryRsp.  # noqa: E501


        :return: The validated_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :rtype: int
        """
        return self._validated_objects

    @validated_objects.setter
    def validated_objects(self, validated_objects):
        """Sets the validated_objects of this ObjectSetSummaryRsp.


        :param validated_objects: The validated_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :type: int
        """

        self._validated_objects = validated_objects

    @property
    def dubious_objects(self):
        """Gets the dubious_objects of this ObjectSetSummaryRsp.  # noqa: E501


        :return: The dubious_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :rtype: int
        """
        return self._dubious_objects

    @dubious_objects.setter
    def dubious_objects(self, dubious_objects):
        """Sets the dubious_objects of this ObjectSetSummaryRsp.


        :param dubious_objects: The dubious_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :type: int
        """

        self._dubious_objects = dubious_objects

    @property
    def predicted_objects(self):
        """Gets the predicted_objects of this ObjectSetSummaryRsp.  # noqa: E501


        :return: The predicted_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :rtype: int
        """
        return self._predicted_objects

    @predicted_objects.setter
    def predicted_objects(self, predicted_objects):
        """Sets the predicted_objects of this ObjectSetSummaryRsp.


        :param predicted_objects: The predicted_objects of this ObjectSetSummaryRsp.  # noqa: E501
        :type: int
        """

        self._predicted_objects = predicted_objects

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
        if not isinstance(other, ObjectSetSummaryRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ObjectSetSummaryRsp):
            return True

        return self.to_dict() != other.to_dict()
