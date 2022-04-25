# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.27
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ObjectSetQueryRsp(object):
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
        'object_ids': 'list[int]',
        'acquisition_ids': 'list[int]',
        'sample_ids': 'list[int]',
        'project_ids': 'list[int]',
        'details': 'list[list[object]]',
        'total_ids': 'int'
    }

    attribute_map = {
        'object_ids': 'object_ids',
        'acquisition_ids': 'acquisition_ids',
        'sample_ids': 'sample_ids',
        'project_ids': 'project_ids',
        'details': 'details',
        'total_ids': 'total_ids'
    }

    def __init__(self, object_ids=[], acquisition_ids=[], sample_ids=[], project_ids=[], details=[], total_ids=0, local_vars_configuration=None):  # noqa: E501
        """ObjectSetQueryRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._object_ids = None
        self._acquisition_ids = None
        self._sample_ids = None
        self._project_ids = None
        self._details = None
        self._total_ids = None
        self.discriminator = None

        if object_ids is not None:
            self.object_ids = object_ids
        if acquisition_ids is not None:
            self.acquisition_ids = acquisition_ids
        if sample_ids is not None:
            self.sample_ids = sample_ids
        if project_ids is not None:
            self.project_ids = project_ids
        if details is not None:
            self.details = details
        if total_ids is not None:
            self.total_ids = total_ids

    @property
    def object_ids(self):
        """Gets the object_ids of this ObjectSetQueryRsp.  # noqa: E501

        Matching object IDs.  # noqa: E501

        :return: The object_ids of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: list[int]
        """
        return self._object_ids

    @object_ids.setter
    def object_ids(self, object_ids):
        """Sets the object_ids of this ObjectSetQueryRsp.

        Matching object IDs.  # noqa: E501

        :param object_ids: The object_ids of this ObjectSetQueryRsp.  # noqa: E501
        :type: list[int]
        """

        self._object_ids = object_ids

    @property
    def acquisition_ids(self):
        """Gets the acquisition_ids of this ObjectSetQueryRsp.  # noqa: E501

        Parent (acquisition) IDs.  # noqa: E501

        :return: The acquisition_ids of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: list[int]
        """
        return self._acquisition_ids

    @acquisition_ids.setter
    def acquisition_ids(self, acquisition_ids):
        """Sets the acquisition_ids of this ObjectSetQueryRsp.

        Parent (acquisition) IDs.  # noqa: E501

        :param acquisition_ids: The acquisition_ids of this ObjectSetQueryRsp.  # noqa: E501
        :type: list[int]
        """

        self._acquisition_ids = acquisition_ids

    @property
    def sample_ids(self):
        """Gets the sample_ids of this ObjectSetQueryRsp.  # noqa: E501

        Parent (sample) IDs.  # noqa: E501

        :return: The sample_ids of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: list[int]
        """
        return self._sample_ids

    @sample_ids.setter
    def sample_ids(self, sample_ids):
        """Sets the sample_ids of this ObjectSetQueryRsp.

        Parent (sample) IDs.  # noqa: E501

        :param sample_ids: The sample_ids of this ObjectSetQueryRsp.  # noqa: E501
        :type: list[int]
        """

        self._sample_ids = sample_ids

    @property
    def project_ids(self):
        """Gets the project_ids of this ObjectSetQueryRsp.  # noqa: E501

        Project Ids.  # noqa: E501

        :return: The project_ids of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: list[int]
        """
        return self._project_ids

    @project_ids.setter
    def project_ids(self, project_ids):
        """Sets the project_ids of this ObjectSetQueryRsp.

        Project Ids.  # noqa: E501

        :param project_ids: The project_ids of this ObjectSetQueryRsp.  # noqa: E501
        :type: list[int]
        """

        self._project_ids = project_ids

    @property
    def details(self):
        """Gets the details of this ObjectSetQueryRsp.  # noqa: E501

        Requested fields, in request order.  # noqa: E501

        :return: The details of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: list[list[object]]
        """
        return self._details

    @details.setter
    def details(self, details):
        """Sets the details of this ObjectSetQueryRsp.

        Requested fields, in request order.  # noqa: E501

        :param details: The details of this ObjectSetQueryRsp.  # noqa: E501
        :type: list[list[object]]
        """

        self._details = details

    @property
    def total_ids(self):
        """Gets the total_ids of this ObjectSetQueryRsp.  # noqa: E501

        Total rows returned by the query, even if it was window-ed.  # noqa: E501

        :return: The total_ids of this ObjectSetQueryRsp.  # noqa: E501
        :rtype: int
        """
        return self._total_ids

    @total_ids.setter
    def total_ids(self, total_ids):
        """Sets the total_ids of this ObjectSetQueryRsp.

        Total rows returned by the query, even if it was window-ed.  # noqa: E501

        :param total_ids: The total_ids of this ObjectSetQueryRsp.  # noqa: E501
        :type: int
        """

        self._total_ids = total_ids

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
        if not isinstance(other, ObjectSetQueryRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ObjectSetQueryRsp):
            return True

        return self.to_dict() != other.to_dict()
