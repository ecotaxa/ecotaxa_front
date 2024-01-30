# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.36
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class TaxonomyRecast(object):
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
        'from_to': 'dict(str, int)',
        'doc': 'dict(str, str)'
    }

    attribute_map = {
        'from_to': 'from_to',
        'doc': 'doc'
    }

    def __init__(self, from_to=None, doc=None, local_vars_configuration=None):  # noqa: E501
        """TaxonomyRecast - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._from_to = None
        self._doc = None
        self.discriminator = None

        self.from_to = from_to
        if doc is not None:
            self.doc = doc

    @property
    def from_to(self):
        """Gets the from_to of this TaxonomyRecast.  # noqa: E501

        Mapping from seen taxon (key) to output replacement one (value). Use a null replacement to _discard_ the present taxon. Note: keys are strings.  # noqa: E501

        :return: The from_to of this TaxonomyRecast.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._from_to

    @from_to.setter
    def from_to(self, from_to):
        """Sets the from_to of this TaxonomyRecast.

        Mapping from seen taxon (key) to output replacement one (value). Use a null replacement to _discard_ the present taxon. Note: keys are strings.  # noqa: E501

        :param from_to: The from_to of this TaxonomyRecast.  # noqa: E501
        :type: dict(str, int)
        """
        if self.local_vars_configuration.client_side_validation and from_to is None:  # noqa: E501
            raise ValueError("Invalid value for `from_to`, must not be `None`")  # noqa: E501

        self._from_to = from_to

    @property
    def doc(self):
        """Gets the doc of this TaxonomyRecast.  # noqa: E501

        To keep memory of the reasons for the above mapping. Note: keys are strings.  # noqa: E501

        :return: The doc of this TaxonomyRecast.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._doc

    @doc.setter
    def doc(self, doc):
        """Sets the doc of this TaxonomyRecast.

        To keep memory of the reasons for the above mapping. Note: keys are strings.  # noqa: E501

        :param doc: The doc of this TaxonomyRecast.  # noqa: E501
        :type: dict(str, str)
        """

        self._doc = doc

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
        if not isinstance(other, TaxonomyRecast):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxonomyRecast):
            return True

        return self.to_dict() != other.to_dict()
