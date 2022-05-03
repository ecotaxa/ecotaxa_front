# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.28
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class TaxonUsageModel(object):
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
        'projid': 'int',
        'title': 'str',
        'nb_validated': 'int'
    }

    attribute_map = {
        'projid': 'projid',
        'title': 'title',
        'nb_validated': 'nb_validated'
    }

    def __init__(self, projid=None, title=None, nb_validated=None, local_vars_configuration=None):  # noqa: E501
        """TaxonUsageModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._projid = None
        self._title = None
        self._nb_validated = None
        self.discriminator = None

        if projid is not None:
            self.projid = projid
        if title is not None:
            self.title = title
        self.nb_validated = nb_validated

    @property
    def projid(self):
        """Gets the projid of this TaxonUsageModel.  # noqa: E501

        Project unique identifier.  # noqa: E501

        :return: The projid of this TaxonUsageModel.  # noqa: E501
        :rtype: int
        """
        return self._projid

    @projid.setter
    def projid(self, projid):
        """Sets the projid of this TaxonUsageModel.

        Project unique identifier.  # noqa: E501

        :param projid: The projid of this TaxonUsageModel.  # noqa: E501
        :type: int
        """

        self._projid = projid

    @property
    def title(self):
        """Gets the title of this TaxonUsageModel.  # noqa: E501

        Project's title.  # noqa: E501

        :return: The title of this TaxonUsageModel.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this TaxonUsageModel.

        Project's title.  # noqa: E501

        :param title: The title of this TaxonUsageModel.  # noqa: E501
        :type: str
        """

        self._title = title

    @property
    def nb_validated(self):
        """Gets the nb_validated of this TaxonUsageModel.  # noqa: E501

        How many validated objects in this category in this project.  # noqa: E501

        :return: The nb_validated of this TaxonUsageModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_validated

    @nb_validated.setter
    def nb_validated(self, nb_validated):
        """Sets the nb_validated of this TaxonUsageModel.

        How many validated objects in this category in this project.  # noqa: E501

        :param nb_validated: The nb_validated of this TaxonUsageModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and nb_validated is None:  # noqa: E501
            raise ValueError("Invalid value for `nb_validated`, must not be `None`")  # noqa: E501

        self._nb_validated = nb_validated

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
        if not isinstance(other, TaxonUsageModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxonUsageModel):
            return True

        return self.to_dict() != other.to_dict()
