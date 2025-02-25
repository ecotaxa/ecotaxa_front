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


class ClassifyAutoReq(object):
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
        'target_ids': 'list[int]',
        'classifications': 'list[int]',
        'scores': 'list[float]',
        'keep_log': 'bool'
    }

    attribute_map = {
        'target_ids': 'target_ids',
        'classifications': 'classifications',
        'scores': 'scores',
        'keep_log': 'keep_log'
    }

    def __init__(self, target_ids=None, classifications=None, scores=None, keep_log=None, local_vars_configuration=None):  # noqa: E501
        """ClassifyAutoReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._target_ids = None
        self._classifications = None
        self._scores = None
        self._keep_log = None
        self.discriminator = None

        self.target_ids = target_ids
        self.classifications = classifications
        self.scores = scores
        self.keep_log = keep_log

    @property
    def target_ids(self):
        """Gets the target_ids of this ClassifyAutoReq.  # noqa: E501

        The IDs of the target objects.  # noqa: E501

        :return: The target_ids of this ClassifyAutoReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._target_ids

    @target_ids.setter
    def target_ids(self, target_ids):
        """Sets the target_ids of this ClassifyAutoReq.

        The IDs of the target objects.  # noqa: E501

        :param target_ids: The target_ids of this ClassifyAutoReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and target_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `target_ids`, must not be `None`")  # noqa: E501

        self._target_ids = target_ids

    @property
    def classifications(self):
        """Gets the classifications of this ClassifyAutoReq.  # noqa: E501

        The wanted new classifications, i.e. taxon ID, one for each object.  # noqa: E501

        :return: The classifications of this ClassifyAutoReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._classifications

    @classifications.setter
    def classifications(self, classifications):
        """Sets the classifications of this ClassifyAutoReq.

        The wanted new classifications, i.e. taxon ID, one for each object.  # noqa: E501

        :param classifications: The classifications of this ClassifyAutoReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and classifications is None:  # noqa: E501
            raise ValueError("Invalid value for `classifications`, must not be `None`")  # noqa: E501

        self._classifications = classifications

    @property
    def scores(self):
        """Gets the scores of this ClassifyAutoReq.  # noqa: E501

        The classification score is generally between 0 and 1. It indicates the probability that the taxon prediction of this object is correct.  # noqa: E501

        :return: The scores of this ClassifyAutoReq.  # noqa: E501
        :rtype: list[float]
        """
        return self._scores

    @scores.setter
    def scores(self, scores):
        """Sets the scores of this ClassifyAutoReq.

        The classification score is generally between 0 and 1. It indicates the probability that the taxon prediction of this object is correct.  # noqa: E501

        :param scores: The scores of this ClassifyAutoReq.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and scores is None:  # noqa: E501
            raise ValueError("Invalid value for `scores`, must not be `None`")  # noqa: E501

        self._scores = scores

    @property
    def keep_log(self):
        """Gets the keep_log of this ClassifyAutoReq.  # noqa: E501

        Set if former automatic classification history is needed.  # noqa: E501

        :return: The keep_log of this ClassifyAutoReq.  # noqa: E501
        :rtype: bool
        """
        return self._keep_log

    @keep_log.setter
    def keep_log(self, keep_log):
        """Sets the keep_log of this ClassifyAutoReq.

        Set if former automatic classification history is needed.  # noqa: E501

        :param keep_log: The keep_log of this ClassifyAutoReq.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and keep_log is None:  # noqa: E501
            raise ValueError("Invalid value for `keep_log`, must not be `None`")  # noqa: E501

        self._keep_log = keep_log

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
        if not isinstance(other, ClassifyAutoReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ClassifyAutoReq):
            return True

        return self.to_dict() != other.to_dict()
