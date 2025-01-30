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


class BodyExportObjectSetBackupObjectSetExportBackupPost(object):
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
        'filters': 'ProjectFilters',
        'request': 'BackupExportReq'
    }

    attribute_map = {
        'filters': 'filters',
        'request': 'request'
    }

    def __init__(self, filters=None, request=None, local_vars_configuration=None):  # noqa: E501
        """BodyExportObjectSetBackupObjectSetExportBackupPost - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._filters = None
        self._request = None
        self.discriminator = None

        self.filters = filters
        self.request = request

    @property
    def filters(self):
        """Gets the filters of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501


        :return: The filters of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501
        :rtype: ProjectFilters
        """
        return self._filters

    @filters.setter
    def filters(self, filters):
        """Sets the filters of this BodyExportObjectSetBackupObjectSetExportBackupPost.


        :param filters: The filters of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501
        :type: ProjectFilters
        """
        if self.local_vars_configuration.client_side_validation and filters is None:  # noqa: E501
            raise ValueError("Invalid value for `filters`, must not be `None`")  # noqa: E501

        self._filters = filters

    @property
    def request(self):
        """Gets the request of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501


        :return: The request of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501
        :rtype: BackupExportReq
        """
        return self._request

    @request.setter
    def request(self, request):
        """Sets the request of this BodyExportObjectSetBackupObjectSetExportBackupPost.


        :param request: The request of this BodyExportObjectSetBackupObjectSetExportBackupPost.  # noqa: E501
        :type: BackupExportReq
        """
        if self.local_vars_configuration.client_side_validation and request is None:  # noqa: E501
            raise ValueError("Invalid value for `request`, must not be `None`")  # noqa: E501

        self._request = request

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
        if not isinstance(other, BodyExportObjectSetBackupObjectSetExportBackupPost):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BodyExportObjectSetBackupObjectSetExportBackupPost):
            return True

        return self.to_dict() != other.to_dict()
