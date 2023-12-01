# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.35
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ExportRsp(object):
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
        'errors': 'list[str]',
        'warnings': 'list[str]',
        'job_id': 'int'
    }

    attribute_map = {
        'errors': 'errors',
        'warnings': 'warnings',
        'job_id': 'job_id'
    }

    def __init__(self, errors=[], warnings=[], job_id=0, local_vars_configuration=None):  # noqa: E501
        """ExportRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._errors = None
        self._warnings = None
        self._job_id = None
        self.discriminator = None

        if errors is not None:
            self.errors = errors
        if warnings is not None:
            self.warnings = warnings
        if job_id is not None:
            self.job_id = job_id

    @property
    def errors(self):
        """Gets the errors of this ExportRsp.  # noqa: E501

        Showstopper problems found preventing building the archive.  # noqa: E501

        :return: The errors of this ExportRsp.  # noqa: E501
        :rtype: list[str]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this ExportRsp.

        Showstopper problems found preventing building the archive.  # noqa: E501

        :param errors: The errors of this ExportRsp.  # noqa: E501
        :type: list[str]
        """

        self._errors = errors

    @property
    def warnings(self):
        """Gets the warnings of this ExportRsp.  # noqa: E501

        Problems found while building the archive, which do not prevent producing it.  # noqa: E501

        :return: The warnings of this ExportRsp.  # noqa: E501
        :rtype: list[str]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this ExportRsp.

        Problems found while building the archive, which do not prevent producing it.  # noqa: E501

        :param warnings: The warnings of this ExportRsp.  # noqa: E501
        :type: list[str]
        """

        self._warnings = warnings

    @property
    def job_id(self):
        """Gets the job_id of this ExportRsp.  # noqa: E501

        The created job, 0 if there were problems.  # noqa: E501

        :return: The job_id of this ExportRsp.  # noqa: E501
        :rtype: int
        """
        return self._job_id

    @job_id.setter
    def job_id(self, job_id):
        """Sets the job_id of this ExportRsp.

        The created job, 0 if there were problems.  # noqa: E501

        :param job_id: The job_id of this ExportRsp.  # noqa: E501
        :type: int
        """

        self._job_id = job_id

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
        if not isinstance(other, ExportRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExportRsp):
            return True

        return self.to_dict() != other.to_dict()
