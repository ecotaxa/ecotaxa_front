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


class ImportReq(object):
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
        'source_path': 'str',
        'taxo_mappings': 'dict(str, str)',
        'skip_loaded_files': 'bool',
        'skip_existing_objects': 'bool',
        'update_mode': 'str'
    }

    attribute_map = {
        'source_path': 'source_path',
        'taxo_mappings': 'taxo_mappings',
        'skip_loaded_files': 'skip_loaded_files',
        'skip_existing_objects': 'skip_existing_objects',
        'update_mode': 'update_mode'
    }

    def __init__(self, source_path=None, taxo_mappings=None, skip_loaded_files=False, skip_existing_objects=False, update_mode='', local_vars_configuration=None):  # noqa: E501
        """ImportReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._source_path = None
        self._taxo_mappings = None
        self._skip_loaded_files = None
        self._skip_existing_objects = None
        self._update_mode = None
        self.discriminator = None

        self.source_path = source_path
        if taxo_mappings is not None:
            self.taxo_mappings = taxo_mappings
        if skip_loaded_files is not None:
            self.skip_loaded_files = skip_loaded_files
        if skip_existing_objects is not None:
            self.skip_existing_objects = skip_existing_objects
        if update_mode is not None:
            self.update_mode = update_mode

    @property
    def source_path(self):
        """Gets the source_path of this ImportReq.  # noqa: E501

        Source path on server, to zip or plain directory.     The path can be returned by a file upload (absolute),     otherwise it's relative to shared file area root.  # noqa: E501

        :return: The source_path of this ImportReq.  # noqa: E501
        :rtype: str
        """
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        """Sets the source_path of this ImportReq.

        Source path on server, to zip or plain directory.     The path can be returned by a file upload (absolute),     otherwise it's relative to shared file area root.  # noqa: E501

        :param source_path: The source_path of this ImportReq.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and source_path is None:  # noqa: E501
            raise ValueError("Invalid value for `source_path`, must not be `None`")  # noqa: E501

        self._source_path = source_path

    @property
    def taxo_mappings(self):
        """Gets the taxo_mappings of this ImportReq.  # noqa: E501

        Optional taxonomy mapping, the key specifies the taxonomy ID found in file and the value specifies the final taxonomy ID to write.  # noqa: E501

        :return: The taxo_mappings of this ImportReq.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._taxo_mappings

    @taxo_mappings.setter
    def taxo_mappings(self, taxo_mappings):
        """Sets the taxo_mappings of this ImportReq.

        Optional taxonomy mapping, the key specifies the taxonomy ID found in file and the value specifies the final taxonomy ID to write.  # noqa: E501

        :param taxo_mappings: The taxo_mappings of this ImportReq.  # noqa: E501
        :type: dict(str, str)
        """

        self._taxo_mappings = taxo_mappings

    @property
    def skip_loaded_files(self):
        """Gets the skip_loaded_files of this ImportReq.  # noqa: E501

        If true skip loaded files, else don't.  # noqa: E501

        :return: The skip_loaded_files of this ImportReq.  # noqa: E501
        :rtype: bool
        """
        return self._skip_loaded_files

    @skip_loaded_files.setter
    def skip_loaded_files(self, skip_loaded_files):
        """Sets the skip_loaded_files of this ImportReq.

        If true skip loaded files, else don't.  # noqa: E501

        :param skip_loaded_files: The skip_loaded_files of this ImportReq.  # noqa: E501
        :type: bool
        """

        self._skip_loaded_files = skip_loaded_files

    @property
    def skip_existing_objects(self):
        """Gets the skip_existing_objects of this ImportReq.  # noqa: E501

        If true skip existing objects, else don't.  # noqa: E501

        :return: The skip_existing_objects of this ImportReq.  # noqa: E501
        :rtype: bool
        """
        return self._skip_existing_objects

    @skip_existing_objects.setter
    def skip_existing_objects(self, skip_existing_objects):
        """Sets the skip_existing_objects of this ImportReq.

        If true skip existing objects, else don't.  # noqa: E501

        :param skip_existing_objects: The skip_existing_objects of this ImportReq.  # noqa: E501
        :type: bool
        """

        self._skip_existing_objects = skip_existing_objects

    @property
    def update_mode(self):
        """Gets the update_mode of this ImportReq.  # noqa: E501

        Update data ('Yes'), including classification ('Cla').  # noqa: E501

        :return: The update_mode of this ImportReq.  # noqa: E501
        :rtype: str
        """
        return self._update_mode

    @update_mode.setter
    def update_mode(self, update_mode):
        """Sets the update_mode of this ImportReq.

        Update data ('Yes'), including classification ('Cla').  # noqa: E501

        :param update_mode: The update_mode of this ImportReq.  # noqa: E501
        :type: str
        """

        self._update_mode = update_mode

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
        if not isinstance(other, ImportReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImportReq):
            return True

        return self.to_dict() != other.to_dict()
