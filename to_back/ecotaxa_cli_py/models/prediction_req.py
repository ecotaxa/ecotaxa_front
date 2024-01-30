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


class PredictionReq(object):
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
        'project_id': 'int',
        'source_project_ids': 'list[int]',
        'learning_limit': 'int',
        'features': 'list[str]',
        'categories': 'list[int]',
        'use_scn': 'bool',
        'pre_mapping': 'dict(str, int)'
    }

    attribute_map = {
        'project_id': 'project_id',
        'source_project_ids': 'source_project_ids',
        'learning_limit': 'learning_limit',
        'features': 'features',
        'categories': 'categories',
        'use_scn': 'use_scn',
        'pre_mapping': 'pre_mapping'
    }

    def __init__(self, project_id=None, source_project_ids=None, learning_limit=None, features=None, categories=None, use_scn=False, pre_mapping=None, local_vars_configuration=None):  # noqa: E501
        """PredictionReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._project_id = None
        self._source_project_ids = None
        self._learning_limit = None
        self._features = None
        self._categories = None
        self._use_scn = None
        self._pre_mapping = None
        self.discriminator = None

        self.project_id = project_id
        self.source_project_ids = source_project_ids
        if learning_limit is not None:
            self.learning_limit = learning_limit
        self.features = features
        self.categories = categories
        if use_scn is not None:
            self.use_scn = use_scn
        self.pre_mapping = pre_mapping

    @property
    def project_id(self):
        """Gets the project_id of this PredictionReq.  # noqa: E501

        The destination project, of which objects will be predicted.  # noqa: E501

        :return: The project_id of this PredictionReq.  # noqa: E501
        :rtype: int
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this PredictionReq.

        The destination project, of which objects will be predicted.  # noqa: E501

        :param project_id: The project_id of this PredictionReq.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and project_id is None:  # noqa: E501
            raise ValueError("Invalid value for `project_id`, must not be `None`")  # noqa: E501

        self._project_id = project_id

    @property
    def source_project_ids(self):
        """Gets the source_project_ids of this PredictionReq.  # noqa: E501

        The source projects, objects in them will serve as reference.  # noqa: E501

        :return: The source_project_ids of this PredictionReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._source_project_ids

    @source_project_ids.setter
    def source_project_ids(self, source_project_ids):
        """Sets the source_project_ids of this PredictionReq.

        The source projects, objects in them will serve as reference.  # noqa: E501

        :param source_project_ids: The source_project_ids of this PredictionReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and source_project_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `source_project_ids`, must not be `None`")  # noqa: E501

        self._source_project_ids = source_project_ids

    @property
    def learning_limit(self):
        """Gets the learning_limit of this PredictionReq.  # noqa: E501

        When set (to a positive value), there will be this number  of objects, _per category_, in the learning set.  # noqa: E501

        :return: The learning_limit of this PredictionReq.  # noqa: E501
        :rtype: int
        """
        return self._learning_limit

    @learning_limit.setter
    def learning_limit(self, learning_limit):
        """Sets the learning_limit of this PredictionReq.

        When set (to a positive value), there will be this number  of objects, _per category_, in the learning set.  # noqa: E501

        :param learning_limit: The learning_limit of this PredictionReq.  # noqa: E501
        :type: int
        """

        self._learning_limit = learning_limit

    @property
    def features(self):
        """Gets the features of this PredictionReq.  # noqa: E501

        The object features AKA free column, to use in the algorithm. Features must be common to all projects, source ones and destination one.  # noqa: E501

        :return: The features of this PredictionReq.  # noqa: E501
        :rtype: list[str]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Sets the features of this PredictionReq.

        The object features AKA free column, to use in the algorithm. Features must be common to all projects, source ones and destination one.  # noqa: E501

        :param features: The features of this PredictionReq.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and features is None:  # noqa: E501
            raise ValueError("Invalid value for `features`, must not be `None`")  # noqa: E501

        self._features = features

    @property
    def categories(self):
        """Gets the categories of this PredictionReq.  # noqa: E501

        In source projects, only objects validated with these categories will be considered.  # noqa: E501

        :return: The categories of this PredictionReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._categories

    @categories.setter
    def categories(self, categories):
        """Sets the categories of this PredictionReq.

        In source projects, only objects validated with these categories will be considered.  # noqa: E501

        :param categories: The categories of this PredictionReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and categories is None:  # noqa: E501
            raise ValueError("Invalid value for `categories`, must not be `None`")  # noqa: E501

        self._categories = categories

    @property
    def use_scn(self):
        """Gets the use_scn of this PredictionReq.  # noqa: E501

        Use extra features, generated using the image, for improving the prediction.  # noqa: E501

        :return: The use_scn of this PredictionReq.  # noqa: E501
        :rtype: bool
        """
        return self._use_scn

    @use_scn.setter
    def use_scn(self, use_scn):
        """Sets the use_scn of this PredictionReq.

        Use extra features, generated using the image, for improving the prediction.  # noqa: E501

        :param use_scn: The use_scn of this PredictionReq.  # noqa: E501
        :type: bool
        """

        self._use_scn = use_scn

    @property
    def pre_mapping(self):
        """Gets the pre_mapping of this PredictionReq.  # noqa: E501

        Categories in keys become value one before launching the ML algorithm. Any unknown value is ignored.  # noqa: E501

        :return: The pre_mapping of this PredictionReq.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._pre_mapping

    @pre_mapping.setter
    def pre_mapping(self, pre_mapping):
        """Sets the pre_mapping of this PredictionReq.

        Categories in keys become value one before launching the ML algorithm. Any unknown value is ignored.  # noqa: E501

        :param pre_mapping: The pre_mapping of this PredictionReq.  # noqa: E501
        :type: dict(str, int)
        """
        if self.local_vars_configuration.client_side_validation and pre_mapping is None:  # noqa: E501
            raise ValueError("Invalid value for `pre_mapping`, must not be `None`")  # noqa: E501

        self._pre_mapping = pre_mapping

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
        if not isinstance(other, PredictionReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PredictionReq):
            return True

        return self.to_dict() != other.to_dict()
