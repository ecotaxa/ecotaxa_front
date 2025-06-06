# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.41
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class BodyPutUserFileMyFilesPost(object):
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
        'file': 'file',
        'path': 'str',
        'tag': 'str'
    }

    attribute_map = {
        'file': 'file',
        'path': 'path',
        'tag': 'tag'
    }

    def __init__(self, file=None, path=None, tag=None, local_vars_configuration=None):  # noqa: E501
        """BodyPutUserFileMyFilesPost - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._file = None
        self._path = None
        self._tag = None
        self.discriminator = None

        self.file = file
        if path is not None:
            self.path = path
        if tag is not None:
            self.tag = tag

    @property
    def file(self):
        """Gets the file of this BodyPutUserFileMyFilesPost.  # noqa: E501


        :return: The file of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :rtype: file
        """
        return self._file

    @file.setter
    def file(self, file):
        """Sets the file of this BodyPutUserFileMyFilesPost.


        :param file: The file of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :type: file
        """
        if self.local_vars_configuration.client_side_validation and file is None:  # noqa: E501
            raise ValueError("Invalid value for `file`, must not be `None`")  # noqa: E501

        self._file = file

    @property
    def path(self):
        """Gets the path of this BodyPutUserFileMyFilesPost.  # noqa: E501

        The client-side full path of the file.  # noqa: E501

        :return: The path of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this BodyPutUserFileMyFilesPost.

        The client-side full path of the file.  # noqa: E501

        :param path: The path of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :type: str
        """

        self._path = path

    @property
    def tag(self):
        """Gets the tag of this BodyPutUserFileMyFilesPost.  # noqa: E501

        If a tag is provided, then all files with the same tag are grouped (in a sub-directory). Otherwise, a temp directory with only this file will be created.  # noqa: E501

        :return: The tag of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this BodyPutUserFileMyFilesPost.

        If a tag is provided, then all files with the same tag are grouped (in a sub-directory). Otherwise, a temp directory with only this file will be created.  # noqa: E501

        :param tag: The tag of this BodyPutUserFileMyFilesPost.  # noqa: E501
        :type: str
        """

        self._tag = tag

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
        if not isinstance(other, BodyPutUserFileMyFilesPost):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BodyPutUserFileMyFilesPost):
            return True

        return self.to_dict() != other.to_dict()
