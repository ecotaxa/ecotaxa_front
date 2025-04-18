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


class PredictionInfoT(object):
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
        'object_id': 'int',
        'classif_id': 'int',
        'score': 'float'
    }

    attribute_map = {
        'object_id': 'object_id',
        'classif_id': 'classif_id',
        'score': 'score'
    }

    def __init__(self, object_id=None, classif_id=None, score=None, local_vars_configuration=None):  # noqa: E501
        """PredictionInfoT - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._object_id = None
        self._classif_id = None
        self._score = None
        self.discriminator = None

        self.object_id = object_id
        self.classif_id = classif_id
        self.score = score

    @property
    def object_id(self):
        """Gets the object_id of this PredictionInfoT.  # noqa: E501


        :return: The object_id of this PredictionInfoT.  # noqa: E501
        :rtype: int
        """
        return self._object_id

    @object_id.setter
    def object_id(self, object_id):
        """Sets the object_id of this PredictionInfoT.


        :param object_id: The object_id of this PredictionInfoT.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and object_id is None:  # noqa: E501
            raise ValueError("Invalid value for `object_id`, must not be `None`")  # noqa: E501

        self._object_id = object_id

    @property
    def classif_id(self):
        """Gets the classif_id of this PredictionInfoT.  # noqa: E501


        :return: The classif_id of this PredictionInfoT.  # noqa: E501
        :rtype: int
        """
        return self._classif_id

    @classif_id.setter
    def classif_id(self, classif_id):
        """Sets the classif_id of this PredictionInfoT.


        :param classif_id: The classif_id of this PredictionInfoT.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and classif_id is None:  # noqa: E501
            raise ValueError("Invalid value for `classif_id`, must not be `None`")  # noqa: E501

        self._classif_id = classif_id

    @property
    def score(self):
        """Gets the score of this PredictionInfoT.  # noqa: E501


        :return: The score of this PredictionInfoT.  # noqa: E501
        :rtype: float
        """
        return self._score

    @score.setter
    def score(self, score):
        """Sets the score of this PredictionInfoT.


        :param score: The score of this PredictionInfoT.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and score is None:  # noqa: E501
            raise ValueError("Invalid value for `score`, must not be `None`")  # noqa: E501

        self._score = score

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
        if not isinstance(other, PredictionInfoT):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PredictionInfoT):
            return True

        return self.to_dict() != other.to_dict()
