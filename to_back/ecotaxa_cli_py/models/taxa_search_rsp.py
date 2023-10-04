# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.34
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class TaxaSearchRsp(object):
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
        'id': 'int',
        'renm_id': 'int',
        'text': 'str',
        'pr': 'int'
    }

    attribute_map = {
        'id': 'id',
        'renm_id': 'renm_id',
        'text': 'text',
        'pr': 'pr'
    }

    def __init__(self, id=None, renm_id=None, text=None, pr=None, local_vars_configuration=None):  # noqa: E501
        """TaxaSearchRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._renm_id = None
        self._text = None
        self._pr = None
        self.discriminator = None

        self.id = id
        if renm_id is not None:
            self.renm_id = renm_id
        self.text = text
        self.pr = pr

    @property
    def id(self):
        """Gets the id of this TaxaSearchRsp.  # noqa: E501

        The taxon/category IDs.  # noqa: E501

        :return: The id of this TaxaSearchRsp.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TaxaSearchRsp.

        The taxon/category IDs.  # noqa: E501

        :param id: The id of this TaxaSearchRsp.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def renm_id(self):
        """Gets the renm_id of this TaxaSearchRsp.  # noqa: E501

        The advised replacement ID if the taxon/category is deprecated.  # noqa: E501

        :return: The renm_id of this TaxaSearchRsp.  # noqa: E501
        :rtype: int
        """
        return self._renm_id

    @renm_id.setter
    def renm_id(self, renm_id):
        """Sets the renm_id of this TaxaSearchRsp.

        The advised replacement ID if the taxon/category is deprecated.  # noqa: E501

        :param renm_id: The renm_id of this TaxaSearchRsp.  # noqa: E501
        :type: int
        """

        self._renm_id = renm_id

    @property
    def text(self):
        """Gets the text of this TaxaSearchRsp.  # noqa: E501

        The taxon name, display one.  # noqa: E501

        :return: The text of this TaxaSearchRsp.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this TaxaSearchRsp.

        The taxon name, display one.  # noqa: E501

        :param text: The text of this TaxaSearchRsp.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and text is None:  # noqa: E501
            raise ValueError("Invalid value for `text`, must not be `None`")  # noqa: E501

        self._text = text

    @property
    def pr(self):
        """Gets the pr of this TaxaSearchRsp.  # noqa: E501

        1 if the taxon is in project list, 0 otherwise.  # noqa: E501

        :return: The pr of this TaxaSearchRsp.  # noqa: E501
        :rtype: int
        """
        return self._pr

    @pr.setter
    def pr(self, pr):
        """Sets the pr of this TaxaSearchRsp.

        1 if the taxon is in project list, 0 otherwise.  # noqa: E501

        :param pr: The pr of this TaxaSearchRsp.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and pr is None:  # noqa: E501
            raise ValueError("Invalid value for `pr`, must not be `None`")  # noqa: E501

        self._pr = pr

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
        if not isinstance(other, TaxaSearchRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxaSearchRsp):
            return True

        return self.to_dict() != other.to_dict()
