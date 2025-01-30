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


class SimilaritySearchRsp(object):
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
        'neighbor_ids': 'list[int]',
        'sim_scores': 'list[float]',
        'message': 'str'
    }

    attribute_map = {
        'neighbor_ids': 'neighbor_ids',
        'sim_scores': 'sim_scores',
        'message': 'message'
    }

    def __init__(self, neighbor_ids=None, sim_scores=None, message=None, local_vars_configuration=None):  # noqa: E501
        """SimilaritySearchRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._neighbor_ids = None
        self._sim_scores = None
        self._message = None
        self.discriminator = None

        self.neighbor_ids = neighbor_ids
        self.sim_scores = sim_scores
        if message is not None:
            self.message = message

    @property
    def neighbor_ids(self):
        """Gets the neighbor_ids of this SimilaritySearchRsp.  # noqa: E501

        The list of similar objects IDs.  # noqa: E501

        :return: The neighbor_ids of this SimilaritySearchRsp.  # noqa: E501
        :rtype: list[int]
        """
        return self._neighbor_ids

    @neighbor_ids.setter
    def neighbor_ids(self, neighbor_ids):
        """Sets the neighbor_ids of this SimilaritySearchRsp.

        The list of similar objects IDs.  # noqa: E501

        :param neighbor_ids: The neighbor_ids of this SimilaritySearchRsp.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and neighbor_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `neighbor_ids`, must not be `None`")  # noqa: E501

        self._neighbor_ids = neighbor_ids

    @property
    def sim_scores(self):
        """Gets the sim_scores of this SimilaritySearchRsp.  # noqa: E501

        The list of similarity scores, between 0 and 1. The higher the closer, e.g. 1 for the target_id itself.  # noqa: E501

        :return: The sim_scores of this SimilaritySearchRsp.  # noqa: E501
        :rtype: list[float]
        """
        return self._sim_scores

    @sim_scores.setter
    def sim_scores(self, sim_scores):
        """Sets the sim_scores of this SimilaritySearchRsp.

        The list of similarity scores, between 0 and 1. The higher the closer, e.g. 1 for the target_id itself.  # noqa: E501

        :param sim_scores: The sim_scores of this SimilaritySearchRsp.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and sim_scores is None:  # noqa: E501
            raise ValueError("Invalid value for `sim_scores`, must not be `None`")  # noqa: E501

        self._sim_scores = sim_scores

    @property
    def message(self):
        """Gets the message of this SimilaritySearchRsp.  # noqa: E501

        A message to the user. If not 'Success' then some condition prevented the computation.  # noqa: E501

        :return: The message of this SimilaritySearchRsp.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this SimilaritySearchRsp.

        A message to the user. If not 'Success' then some condition prevented the computation.  # noqa: E501

        :param message: The message of this SimilaritySearchRsp.  # noqa: E501
        :type: str
        """

        self._message = message

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
        if not isinstance(other, SimilaritySearchRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SimilaritySearchRsp):
            return True

        return self.to_dict() != other.to_dict()
