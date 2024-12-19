# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.39
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class SampleTaxoStatsModel(object):
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
        'sample_id': 'int',
        'used_taxa': 'list[int]',
        'nb_unclassified': 'int',
        'nb_validated': 'int',
        'nb_dubious': 'int',
        'nb_predicted': 'int'
    }

    attribute_map = {
        'sample_id': 'sample_id',
        'used_taxa': 'used_taxa',
        'nb_unclassified': 'nb_unclassified',
        'nb_validated': 'nb_validated',
        'nb_dubious': 'nb_dubious',
        'nb_predicted': 'nb_predicted'
    }

    def __init__(self, sample_id=None, used_taxa=None, nb_unclassified=None, nb_validated=None, nb_dubious=None, nb_predicted=None, local_vars_configuration=None):  # noqa: E501
        """SampleTaxoStatsModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._sample_id = None
        self._used_taxa = None
        self._nb_unclassified = None
        self._nb_validated = None
        self._nb_dubious = None
        self._nb_predicted = None
        self.discriminator = None

        if sample_id is not None:
            self.sample_id = sample_id
        if used_taxa is not None:
            self.used_taxa = used_taxa
        if nb_unclassified is not None:
            self.nb_unclassified = nb_unclassified
        if nb_validated is not None:
            self.nb_validated = nb_validated
        if nb_dubious is not None:
            self.nb_dubious = nb_dubious
        if nb_predicted is not None:
            self.nb_predicted = nb_predicted

    @property
    def sample_id(self):
        """Gets the sample_id of this SampleTaxoStatsModel.  # noqa: E501

        The sample id.  # noqa: E501

        :return: The sample_id of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._sample_id

    @sample_id.setter
    def sample_id(self, sample_id):
        """Sets the sample_id of this SampleTaxoStatsModel.

        The sample id.  # noqa: E501

        :param sample_id: The sample_id of this SampleTaxoStatsModel.  # noqa: E501
        :type: int
        """

        self._sample_id = sample_id

    @property
    def used_taxa(self):
        """Gets the used_taxa of this SampleTaxoStatsModel.  # noqa: E501

        The taxa/category ids used inside the sample. -1 for unclassified objects.  # noqa: E501

        :return: The used_taxa of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._used_taxa

    @used_taxa.setter
    def used_taxa(self, used_taxa):
        """Sets the used_taxa of this SampleTaxoStatsModel.

        The taxa/category ids used inside the sample. -1 for unclassified objects.  # noqa: E501

        :param used_taxa: The used_taxa of this SampleTaxoStatsModel.  # noqa: E501
        :type: list[int]
        """

        self._used_taxa = used_taxa

    @property
    def nb_unclassified(self):
        """Gets the nb_unclassified of this SampleTaxoStatsModel.  # noqa: E501

        The number of unclassified objects inside the sample.  # noqa: E501

        :return: The nb_unclassified of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_unclassified

    @nb_unclassified.setter
    def nb_unclassified(self, nb_unclassified):
        """Sets the nb_unclassified of this SampleTaxoStatsModel.

        The number of unclassified objects inside the sample.  # noqa: E501

        :param nb_unclassified: The nb_unclassified of this SampleTaxoStatsModel.  # noqa: E501
        :type: int
        """

        self._nb_unclassified = nb_unclassified

    @property
    def nb_validated(self):
        """Gets the nb_validated of this SampleTaxoStatsModel.  # noqa: E501

        The number of validated objects inside the sample.  # noqa: E501

        :return: The nb_validated of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_validated

    @nb_validated.setter
    def nb_validated(self, nb_validated):
        """Sets the nb_validated of this SampleTaxoStatsModel.

        The number of validated objects inside the sample.  # noqa: E501

        :param nb_validated: The nb_validated of this SampleTaxoStatsModel.  # noqa: E501
        :type: int
        """

        self._nb_validated = nb_validated

    @property
    def nb_dubious(self):
        """Gets the nb_dubious of this SampleTaxoStatsModel.  # noqa: E501

        The number of dubious objects inside the sample.  # noqa: E501

        :return: The nb_dubious of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_dubious

    @nb_dubious.setter
    def nb_dubious(self, nb_dubious):
        """Sets the nb_dubious of this SampleTaxoStatsModel.

        The number of dubious objects inside the sample.  # noqa: E501

        :param nb_dubious: The nb_dubious of this SampleTaxoStatsModel.  # noqa: E501
        :type: int
        """

        self._nb_dubious = nb_dubious

    @property
    def nb_predicted(self):
        """Gets the nb_predicted of this SampleTaxoStatsModel.  # noqa: E501

        The number of predicted objects inside the sample.  # noqa: E501

        :return: The nb_predicted of this SampleTaxoStatsModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_predicted

    @nb_predicted.setter
    def nb_predicted(self, nb_predicted):
        """Sets the nb_predicted of this SampleTaxoStatsModel.

        The number of predicted objects inside the sample.  # noqa: E501

        :param nb_predicted: The nb_predicted of this SampleTaxoStatsModel.  # noqa: E501
        :type: int
        """

        self._nb_predicted = nb_predicted

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
        if not isinstance(other, SampleTaxoStatsModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SampleTaxoStatsModel):
            return True

        return self.to_dict() != other.to_dict()
