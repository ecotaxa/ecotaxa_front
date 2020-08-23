# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.2
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class EMLGeoCoverage(object):
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
        'geographic_description': 'str',
        'west_bounding_coordinate': 'str',
        'east_bounding_coordinate': 'str',
        'north_bounding_coordinate': 'str',
        'south_bounding_coordinate': 'str'
    }

    attribute_map = {
        'geographic_description': 'geographicDescription',
        'west_bounding_coordinate': 'westBoundingCoordinate',
        'east_bounding_coordinate': 'eastBoundingCoordinate',
        'north_bounding_coordinate': 'northBoundingCoordinate',
        'south_bounding_coordinate': 'southBoundingCoordinate'
    }

    def __init__(self, geographic_description=None, west_bounding_coordinate=None, east_bounding_coordinate=None, north_bounding_coordinate=None, south_bounding_coordinate=None, local_vars_configuration=None):  # noqa: E501
        """EMLGeoCoverage - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._geographic_description = None
        self._west_bounding_coordinate = None
        self._east_bounding_coordinate = None
        self._north_bounding_coordinate = None
        self._south_bounding_coordinate = None
        self.discriminator = None

        self.geographic_description = geographic_description
        self.west_bounding_coordinate = west_bounding_coordinate
        self.east_bounding_coordinate = east_bounding_coordinate
        self.north_bounding_coordinate = north_bounding_coordinate
        self.south_bounding_coordinate = south_bounding_coordinate

    @property
    def geographic_description(self):
        """Gets the geographic_description of this EMLGeoCoverage.  # noqa: E501


        :return: The geographic_description of this EMLGeoCoverage.  # noqa: E501
        :rtype: str
        """
        return self._geographic_description

    @geographic_description.setter
    def geographic_description(self, geographic_description):
        """Sets the geographic_description of this EMLGeoCoverage.


        :param geographic_description: The geographic_description of this EMLGeoCoverage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and geographic_description is None:  # noqa: E501
            raise ValueError("Invalid value for `geographic_description`, must not be `None`")  # noqa: E501

        self._geographic_description = geographic_description

    @property
    def west_bounding_coordinate(self):
        """Gets the west_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501


        :return: The west_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :rtype: str
        """
        return self._west_bounding_coordinate

    @west_bounding_coordinate.setter
    def west_bounding_coordinate(self, west_bounding_coordinate):
        """Sets the west_bounding_coordinate of this EMLGeoCoverage.


        :param west_bounding_coordinate: The west_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and west_bounding_coordinate is None:  # noqa: E501
            raise ValueError("Invalid value for `west_bounding_coordinate`, must not be `None`")  # noqa: E501

        self._west_bounding_coordinate = west_bounding_coordinate

    @property
    def east_bounding_coordinate(self):
        """Gets the east_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501


        :return: The east_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :rtype: str
        """
        return self._east_bounding_coordinate

    @east_bounding_coordinate.setter
    def east_bounding_coordinate(self, east_bounding_coordinate):
        """Sets the east_bounding_coordinate of this EMLGeoCoverage.


        :param east_bounding_coordinate: The east_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and east_bounding_coordinate is None:  # noqa: E501
            raise ValueError("Invalid value for `east_bounding_coordinate`, must not be `None`")  # noqa: E501

        self._east_bounding_coordinate = east_bounding_coordinate

    @property
    def north_bounding_coordinate(self):
        """Gets the north_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501


        :return: The north_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :rtype: str
        """
        return self._north_bounding_coordinate

    @north_bounding_coordinate.setter
    def north_bounding_coordinate(self, north_bounding_coordinate):
        """Sets the north_bounding_coordinate of this EMLGeoCoverage.


        :param north_bounding_coordinate: The north_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and north_bounding_coordinate is None:  # noqa: E501
            raise ValueError("Invalid value for `north_bounding_coordinate`, must not be `None`")  # noqa: E501

        self._north_bounding_coordinate = north_bounding_coordinate

    @property
    def south_bounding_coordinate(self):
        """Gets the south_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501


        :return: The south_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :rtype: str
        """
        return self._south_bounding_coordinate

    @south_bounding_coordinate.setter
    def south_bounding_coordinate(self, south_bounding_coordinate):
        """Sets the south_bounding_coordinate of this EMLGeoCoverage.


        :param south_bounding_coordinate: The south_bounding_coordinate of this EMLGeoCoverage.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and south_bounding_coordinate is None:  # noqa: E501
            raise ValueError("Invalid value for `south_bounding_coordinate`, must not be `None`")  # noqa: E501

        self._south_bounding_coordinate = south_bounding_coordinate

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
        if not isinstance(other, EMLGeoCoverage):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, EMLGeoCoverage):
            return True

        return self.to_dict() != other.to_dict()
