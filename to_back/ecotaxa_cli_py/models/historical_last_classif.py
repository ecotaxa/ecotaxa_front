# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.24
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class HistoricalLastClassif(object):
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
        'histo_classif_date': 'datetime',
        'histo_classif_type': 'str',
        'histo_classif_id': 'int',
        'histo_classif_qual': 'str',
        'histo_classif_who': 'int'
    }

    attribute_map = {
        'objid': 'objid',
        'classif_id': 'classif_id',
        'histo_classif_date': 'histo_classif_date',
        'histo_classif_type': 'histo_classif_type',
        'histo_classif_id': 'histo_classif_id',
        'histo_classif_qual': 'histo_classif_qual',
        'histo_classif_who': 'histo_classif_who'
    }

    def __init__(self, objid=None, classif_id=None, histo_classif_date=None, histo_classif_type=None, histo_classif_id=None, histo_classif_qual=None, histo_classif_who=None, local_vars_configuration=None):  # noqa: E501
        """HistoricalLastClassif - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._objid = None
        self._classif_id = None
        self._histo_classif_date = None
        self._histo_classif_type = None
        self._histo_classif_id = None
        self._histo_classif_qual = None
        self._histo_classif_who = None
        self.discriminator = None

        if objid is not None:
            self.objid = objid
        if classif_id is not None:
            self.classif_id = classif_id
        if histo_classif_date is not None:
            self.histo_classif_date = histo_classif_date
        if histo_classif_type is not None:
            self.histo_classif_type = histo_classif_type
        if histo_classif_id is not None:
            self.histo_classif_id = histo_classif_id
        if histo_classif_qual is not None:
            self.histo_classif_qual = histo_classif_qual
        if histo_classif_who is not None:
            self.histo_classif_who = histo_classif_who

    @property
    def objid(self):
        """Gets the objid of this HistoricalLastClassif.  # noqa: E501

        The object Id.  # noqa: E501

        :return: The objid of this HistoricalLastClassif.  # noqa: E501
        :rtype: int
        """
        return self._objid

    @objid.setter
    def objid(self, objid):
        """Sets the objid of this HistoricalLastClassif.

        The object Id.  # noqa: E501

        :param objid: The objid of this HistoricalLastClassif.  # noqa: E501
        :type: int
        """

        self._objid = objid

    @property
    def classif_id(self):
        """Gets the classif_id of this HistoricalLastClassif.  # noqa: E501

        The classification Id.  # noqa: E501

        :return: The classif_id of this HistoricalLastClassif.  # noqa: E501
        :rtype: int
        """
        return self._classif_id

    @classif_id.setter
    def classif_id(self, classif_id):
        """Sets the classif_id of this HistoricalLastClassif.

        The classification Id.  # noqa: E501

        :param classif_id: The classif_id of this HistoricalLastClassif.  # noqa: E501
        :type: int
        """

        self._classif_id = classif_id

    @property
    def histo_classif_date(self):
        """Gets the histo_classif_date of this HistoricalLastClassif.  # noqa: E501

        The classification date.  # noqa: E501

        :return: The histo_classif_date of this HistoricalLastClassif.  # noqa: E501
        :rtype: datetime
        """
        return self._histo_classif_date

    @histo_classif_date.setter
    def histo_classif_date(self, histo_classif_date):
        """Sets the histo_classif_date of this HistoricalLastClassif.

        The classification date.  # noqa: E501

        :param histo_classif_date: The histo_classif_date of this HistoricalLastClassif.  # noqa: E501
        :type: datetime
        """

        self._histo_classif_date = histo_classif_date

    @property
    def histo_classif_type(self):
        """Gets the histo_classif_type of this HistoricalLastClassif.  # noqa: E501

        The type of classification. Could be **A** for Automatic or **M** for Manual.  # noqa: E501

        :return: The histo_classif_type of this HistoricalLastClassif.  # noqa: E501
        :rtype: str
        """
        return self._histo_classif_type

    @histo_classif_type.setter
    def histo_classif_type(self, histo_classif_type):
        """Sets the histo_classif_type of this HistoricalLastClassif.

        The type of classification. Could be **A** for Automatic or **M** for Manual.  # noqa: E501

        :param histo_classif_type: The histo_classif_type of this HistoricalLastClassif.  # noqa: E501
        :type: str
        """

        self._histo_classif_type = histo_classif_type

    @property
    def histo_classif_id(self):
        """Gets the histo_classif_id of this HistoricalLastClassif.  # noqa: E501

        The classification Id.  # noqa: E501

        :return: The histo_classif_id of this HistoricalLastClassif.  # noqa: E501
        :rtype: int
        """
        return self._histo_classif_id

    @histo_classif_id.setter
    def histo_classif_id(self, histo_classif_id):
        """Sets the histo_classif_id of this HistoricalLastClassif.

        The classification Id.  # noqa: E501

        :param histo_classif_id: The histo_classif_id of this HistoricalLastClassif.  # noqa: E501
        :type: int
        """

        self._histo_classif_id = histo_classif_id

    @property
    def histo_classif_qual(self):
        """Gets the histo_classif_qual of this HistoricalLastClassif.  # noqa: E501

        The classification qualification. Could be **P** for predicted, **V** for validated or **D** for Dubious.  # noqa: E501

        :return: The histo_classif_qual of this HistoricalLastClassif.  # noqa: E501
        :rtype: str
        """
        return self._histo_classif_qual

    @histo_classif_qual.setter
    def histo_classif_qual(self, histo_classif_qual):
        """Sets the histo_classif_qual of this HistoricalLastClassif.

        The classification qualification. Could be **P** for predicted, **V** for validated or **D** for Dubious.  # noqa: E501

        :param histo_classif_qual: The histo_classif_qual of this HistoricalLastClassif.  # noqa: E501
        :type: str
        """

        self._histo_classif_qual = histo_classif_qual

    @property
    def histo_classif_who(self):
        """Gets the histo_classif_who of this HistoricalLastClassif.  # noqa: E501

        The user who manualy classify this object.  # noqa: E501

        :return: The histo_classif_who of this HistoricalLastClassif.  # noqa: E501
        :rtype: int
        """
        return self._histo_classif_who

    @histo_classif_who.setter
    def histo_classif_who(self, histo_classif_who):
        """Sets the histo_classif_who of this HistoricalLastClassif.

        The user who manualy classify this object.  # noqa: E501

        :param histo_classif_who: The histo_classif_who of this HistoricalLastClassif.  # noqa: E501
        :type: int
        """

        self._histo_classif_who = histo_classif_who

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
        if not isinstance(other, HistoricalLastClassif):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, HistoricalLastClassif):
            return True

        return self.to_dict() != other.to_dict()
