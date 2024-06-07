# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.37
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class SampleModel(object):
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
        'sampleid': 'int',
        'projid': 'int',
        'orig_id': 'str',
        'latitude': 'float',
        'longitude': 'float',
        'dataportal_descriptor': 'str',
        'free_columns': 'object'
    }

    attribute_map = {
        'sampleid': 'sampleid',
        'projid': 'projid',
        'orig_id': 'orig_id',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'dataportal_descriptor': 'dataportal_descriptor',
        'free_columns': 'free_columns'
    }

    def __init__(self, sampleid=None, projid=None, orig_id=None, latitude=None, longitude=None, dataportal_descriptor=None, free_columns=None, local_vars_configuration=None):  # noqa: E501
        """SampleModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._sampleid = None
        self._projid = None
        self._orig_id = None
        self._latitude = None
        self._longitude = None
        self._dataportal_descriptor = None
        self._free_columns = None
        self.discriminator = None

        self.sampleid = sampleid
        self.projid = projid
        self.orig_id = orig_id
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if dataportal_descriptor is not None:
            self.dataportal_descriptor = dataportal_descriptor
        if free_columns is not None:
            self.free_columns = free_columns

    @property
    def sampleid(self):
        """Gets the sampleid of this SampleModel.  # noqa: E501

        The sample Id.  # noqa: E501

        :return: The sampleid of this SampleModel.  # noqa: E501
        :rtype: int
        """
        return self._sampleid

    @sampleid.setter
    def sampleid(self, sampleid):
        """Sets the sampleid of this SampleModel.

        The sample Id.  # noqa: E501

        :param sampleid: The sampleid of this SampleModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and sampleid is None:  # noqa: E501
            raise ValueError("Invalid value for `sampleid`, must not be `None`")  # noqa: E501

        self._sampleid = sampleid

    @property
    def projid(self):
        """Gets the projid of this SampleModel.  # noqa: E501

        The project Id.  # noqa: E501

        :return: The projid of this SampleModel.  # noqa: E501
        :rtype: int
        """
        return self._projid

    @projid.setter
    def projid(self, projid):
        """Sets the projid of this SampleModel.

        The project Id.  # noqa: E501

        :param projid: The projid of this SampleModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and projid is None:  # noqa: E501
            raise ValueError("Invalid value for `projid`, must not be `None`")  # noqa: E501

        self._projid = projid

    @property
    def orig_id(self):
        """Gets the orig_id of this SampleModel.  # noqa: E501

        Original sample ID from initial TSV load.  # noqa: E501

        :return: The orig_id of this SampleModel.  # noqa: E501
        :rtype: str
        """
        return self._orig_id

    @orig_id.setter
    def orig_id(self, orig_id):
        """Sets the orig_id of this SampleModel.

        Original sample ID from initial TSV load.  # noqa: E501

        :param orig_id: The orig_id of this SampleModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and orig_id is None:  # noqa: E501
            raise ValueError("Invalid value for `orig_id`, must not be `None`")  # noqa: E501

        self._orig_id = orig_id

    @property
    def latitude(self):
        """Gets the latitude of this SampleModel.  # noqa: E501

        The latitude.  # noqa: E501

        :return: The latitude of this SampleModel.  # noqa: E501
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """Sets the latitude of this SampleModel.

        The latitude.  # noqa: E501

        :param latitude: The latitude of this SampleModel.  # noqa: E501
        :type: float
        """

        self._latitude = latitude

    @property
    def longitude(self):
        """Gets the longitude of this SampleModel.  # noqa: E501

        The longitude.  # noqa: E501

        :return: The longitude of this SampleModel.  # noqa: E501
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """Sets the longitude of this SampleModel.

        The longitude.  # noqa: E501

        :param longitude: The longitude of this SampleModel.  # noqa: E501
        :type: float
        """

        self._longitude = longitude

    @property
    def dataportal_descriptor(self):
        """Gets the dataportal_descriptor of this SampleModel.  # noqa: E501


        :return: The dataportal_descriptor of this SampleModel.  # noqa: E501
        :rtype: str
        """
        return self._dataportal_descriptor

    @dataportal_descriptor.setter
    def dataportal_descriptor(self, dataportal_descriptor):
        """Sets the dataportal_descriptor of this SampleModel.


        :param dataportal_descriptor: The dataportal_descriptor of this SampleModel.  # noqa: E501
        :type: str
        """

        self._dataportal_descriptor = dataportal_descriptor

    @property
    def free_columns(self):
        """Gets the free_columns of this SampleModel.  # noqa: E501

        Free columns from sample mapping in project.  # noqa: E501

        :return: The free_columns of this SampleModel.  # noqa: E501
        :rtype: object
        """
        return self._free_columns

    @free_columns.setter
    def free_columns(self, free_columns):
        """Sets the free_columns of this SampleModel.

        Free columns from sample mapping in project.  # noqa: E501

        :param free_columns: The free_columns of this SampleModel.  # noqa: E501
        :type: object
        """

        self._free_columns = free_columns

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
        if not isinstance(other, SampleModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SampleModel):
            return True

        return self.to_dict() != other.to_dict()
