# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.13
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class HistoricalClassification(object):
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
        'objid': 'int',
        'classif_id': 'int',
        'classif_date': 'datetime',
        'classif_who': 'int',
        'classif_type': 'str',
        'classif_qual': 'str',
        'classif_score': 'float',
        'user_name': 'str',
        'taxon_name': 'str'
    }

    attribute_map = {
        'objid': 'objid',
        'classif_id': 'classif_id',
        'classif_date': 'classif_date',
        'classif_who': 'classif_who',
        'classif_type': 'classif_type',
        'classif_qual': 'classif_qual',
        'classif_score': 'classif_score',
        'user_name': 'user_name',
        'taxon_name': 'taxon_name'
    }

    def __init__(self, objid=None, classif_id=None, classif_date=None, classif_who=None, classif_type=None, classif_qual=None, classif_score=None, user_name=None, taxon_name=None, local_vars_configuration=None):  # noqa: E501
        """HistoricalClassification - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._objid = None
        self._classif_id = None
        self._classif_date = None
        self._classif_who = None
        self._classif_type = None
        self._classif_qual = None
        self._classif_score = None
        self._user_name = None
        self._taxon_name = None
        self.discriminator = None

        if objid is not None:
            self.objid = objid
        if classif_id is not None:
            self.classif_id = classif_id
        if classif_date is not None:
            self.classif_date = classif_date
        if classif_who is not None:
            self.classif_who = classif_who
        if classif_type is not None:
            self.classif_type = classif_type
        if classif_qual is not None:
            self.classif_qual = classif_qual
        if classif_score is not None:
            self.classif_score = classif_score
        if user_name is not None:
            self.user_name = user_name
        if taxon_name is not None:
            self.taxon_name = taxon_name

    @property
    def objid(self):
        """Gets the objid of this HistoricalClassification.  # noqa: E501


        :return: The objid of this HistoricalClassification.  # noqa: E501
        :rtype: int
        """
        return self._objid

    @objid.setter
    def objid(self, objid):
        """Sets the objid of this HistoricalClassification.


        :param objid: The objid of this HistoricalClassification.  # noqa: E501
        :type: int
        """

        self._objid = objid

    @property
    def classif_id(self):
        """Gets the classif_id of this HistoricalClassification.  # noqa: E501


        :return: The classif_id of this HistoricalClassification.  # noqa: E501
        :rtype: int
        """
        return self._classif_id

    @classif_id.setter
    def classif_id(self, classif_id):
        """Sets the classif_id of this HistoricalClassification.


        :param classif_id: The classif_id of this HistoricalClassification.  # noqa: E501
        :type: int
        """

        self._classif_id = classif_id

    @property
    def classif_date(self):
        """Gets the classif_date of this HistoricalClassification.  # noqa: E501


        :return: The classif_date of this HistoricalClassification.  # noqa: E501
        :rtype: datetime
        """
        return self._classif_date

    @classif_date.setter
    def classif_date(self, classif_date):
        """Sets the classif_date of this HistoricalClassification.


        :param classif_date: The classif_date of this HistoricalClassification.  # noqa: E501
        :type: datetime
        """

        self._classif_date = classif_date

    @property
    def classif_who(self):
        """Gets the classif_who of this HistoricalClassification.  # noqa: E501


        :return: The classif_who of this HistoricalClassification.  # noqa: E501
        :rtype: int
        """
        return self._classif_who

    @classif_who.setter
    def classif_who(self, classif_who):
        """Sets the classif_who of this HistoricalClassification.


        :param classif_who: The classif_who of this HistoricalClassification.  # noqa: E501
        :type: int
        """

        self._classif_who = classif_who

    @property
    def classif_type(self):
        """Gets the classif_type of this HistoricalClassification.  # noqa: E501


        :return: The classif_type of this HistoricalClassification.  # noqa: E501
        :rtype: str
        """
        return self._classif_type

    @classif_type.setter
    def classif_type(self, classif_type):
        """Sets the classif_type of this HistoricalClassification.


        :param classif_type: The classif_type of this HistoricalClassification.  # noqa: E501
        :type: str
        """

        self._classif_type = classif_type

    @property
    def classif_qual(self):
        """Gets the classif_qual of this HistoricalClassification.  # noqa: E501


        :return: The classif_qual of this HistoricalClassification.  # noqa: E501
        :rtype: str
        """
        return self._classif_qual

    @classif_qual.setter
    def classif_qual(self, classif_qual):
        """Sets the classif_qual of this HistoricalClassification.


        :param classif_qual: The classif_qual of this HistoricalClassification.  # noqa: E501
        :type: str
        """

        self._classif_qual = classif_qual

    @property
    def classif_score(self):
        """Gets the classif_score of this HistoricalClassification.  # noqa: E501


        :return: The classif_score of this HistoricalClassification.  # noqa: E501
        :rtype: float
        """
        return self._classif_score

    @classif_score.setter
    def classif_score(self, classif_score):
        """Sets the classif_score of this HistoricalClassification.


        :param classif_score: The classif_score of this HistoricalClassification.  # noqa: E501
        :type: float
        """

        self._classif_score = classif_score

    @property
    def user_name(self):
        """Gets the user_name of this HistoricalClassification.  # noqa: E501


        :return: The user_name of this HistoricalClassification.  # noqa: E501
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Sets the user_name of this HistoricalClassification.


        :param user_name: The user_name of this HistoricalClassification.  # noqa: E501
        :type: str
        """

        self._user_name = user_name

    @property
    def taxon_name(self):
        """Gets the taxon_name of this HistoricalClassification.  # noqa: E501


        :return: The taxon_name of this HistoricalClassification.  # noqa: E501
        :rtype: str
        """
        return self._taxon_name

    @taxon_name.setter
    def taxon_name(self, taxon_name):
        """Sets the taxon_name of this HistoricalClassification.


        :param taxon_name: The taxon_name of this HistoricalClassification.  # noqa: E501
        :type: str
        """

        self._taxon_name = taxon_name

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
        if not isinstance(other, HistoricalClassification):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, HistoricalClassification):
            return True

        return self.to_dict() != other.to_dict()
