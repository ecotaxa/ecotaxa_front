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


class ObjectHeaderModel(object):
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
        'acquisid': 'int',
        'classif_id': 'int',
        'objtime': 'str',
        'latitude': 'float',
        'longitude': 'float',
        'depth_min': 'float',
        'depth_max': 'float',
        'objdate': 'date',
        'classif_qual': 'str',
        'sunpos': 'str',
        'classif_when': 'datetime',
        'classif_who': 'int',
        'classif_auto_id': 'int',
        'classif_auto_when': 'datetime',
        'classif_auto_score': 'float',
        'orig_id': 'str',
        'object_link': 'str',
        'complement_info': 'str'
    }

    attribute_map = {
        'objid': 'objid',
        'acquisid': 'acquisid',
        'classif_id': 'classif_id',
        'objtime': 'objtime',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'depth_min': 'depth_min',
        'depth_max': 'depth_max',
        'objdate': 'objdate',
        'classif_qual': 'classif_qual',
        'sunpos': 'sunpos',
        'classif_when': 'classif_when',
        'classif_who': 'classif_who',
        'classif_auto_id': 'classif_auto_id',
        'classif_auto_when': 'classif_auto_when',
        'classif_auto_score': 'classif_auto_score',
        'orig_id': 'orig_id',
        'object_link': 'object_link',
        'complement_info': 'complement_info'
    }

    def __init__(self, objid=None, acquisid=None, classif_id=None, objtime=None, latitude=None, longitude=None, depth_min=None, depth_max=None, objdate=None, classif_qual=None, sunpos=None, classif_when=None, classif_who=None, classif_auto_id=None, classif_auto_when=None, classif_auto_score=None, orig_id=None, object_link=None, complement_info=None, local_vars_configuration=None):  # noqa: E501
        """ObjectHeaderModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._objid = None
        self._acquisid = None
        self._classif_id = None
        self._objtime = None
        self._latitude = None
        self._longitude = None
        self._depth_min = None
        self._depth_max = None
        self._objdate = None
        self._classif_qual = None
        self._sunpos = None
        self._classif_when = None
        self._classif_who = None
        self._classif_auto_id = None
        self._classif_auto_when = None
        self._classif_auto_score = None
        self._orig_id = None
        self._object_link = None
        self._complement_info = None
        self.discriminator = None

        self.objid = objid
        self.acquisid = acquisid
        if classif_id is not None:
            self.classif_id = classif_id
        if objtime is not None:
            self.objtime = objtime
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if depth_min is not None:
            self.depth_min = depth_min
        if depth_max is not None:
            self.depth_max = depth_max
        if objdate is not None:
            self.objdate = objdate
        if classif_qual is not None:
            self.classif_qual = classif_qual
        if sunpos is not None:
            self.sunpos = sunpos
        if classif_when is not None:
            self.classif_when = classif_when
        if classif_who is not None:
            self.classif_who = classif_who
        if classif_auto_id is not None:
            self.classif_auto_id = classif_auto_id
        if classif_auto_when is not None:
            self.classif_auto_when = classif_auto_when
        if classif_auto_score is not None:
            self.classif_auto_score = classif_auto_score
        self.orig_id = orig_id
        if object_link is not None:
            self.object_link = object_link
        if complement_info is not None:
            self.complement_info = complement_info

    @property
    def objid(self):
        """Gets the objid of this ObjectHeaderModel.  # noqa: E501

        The object Id.  # noqa: E501

        :return: The objid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._objid

    @objid.setter
    def objid(self, objid):
        """Sets the objid of this ObjectHeaderModel.

        The object Id.  # noqa: E501

        :param objid: The objid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and objid is None:  # noqa: E501
            raise ValueError("Invalid value for `objid`, must not be `None`")  # noqa: E501

        self._objid = objid

    @property
    def acquisid(self):
        """Gets the acquisid of this ObjectHeaderModel.  # noqa: E501

        The parent acquisition Id.  # noqa: E501

        :return: The acquisid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._acquisid

    @acquisid.setter
    def acquisid(self, acquisid):
        """Sets the acquisid of this ObjectHeaderModel.

        The parent acquisition Id.  # noqa: E501

        :param acquisid: The acquisid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and acquisid is None:  # noqa: E501
            raise ValueError("Invalid value for `acquisid`, must not be `None`")  # noqa: E501

        self._acquisid = acquisid

    @property
    def classif_id(self):
        """Gets the classif_id of this ObjectHeaderModel.  # noqa: E501

        The classification Id.  # noqa: E501

        :return: The classif_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_id

    @classif_id.setter
    def classif_id(self, classif_id):
        """Sets the classif_id of this ObjectHeaderModel.

        The classification Id.  # noqa: E501

        :param classif_id: The classif_id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_id = classif_id

    @property
    def objtime(self):
        """Gets the objtime of this ObjectHeaderModel.  # noqa: E501


        :return: The objtime of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._objtime

    @objtime.setter
    def objtime(self, objtime):
        """Sets the objtime of this ObjectHeaderModel.


        :param objtime: The objtime of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._objtime = objtime

    @property
    def latitude(self):
        """Gets the latitude of this ObjectHeaderModel.  # noqa: E501

        The latitude.  # noqa: E501

        :return: The latitude of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """Sets the latitude of this ObjectHeaderModel.

        The latitude.  # noqa: E501

        :param latitude: The latitude of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._latitude = latitude

    @property
    def longitude(self):
        """Gets the longitude of this ObjectHeaderModel.  # noqa: E501

        The longitude.  # noqa: E501

        :return: The longitude of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """Sets the longitude of this ObjectHeaderModel.

        The longitude.  # noqa: E501

        :param longitude: The longitude of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._longitude = longitude

    @property
    def depth_min(self):
        """Gets the depth_min of this ObjectHeaderModel.  # noqa: E501

        The min depth.  # noqa: E501

        :return: The depth_min of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._depth_min

    @depth_min.setter
    def depth_min(self, depth_min):
        """Sets the depth_min of this ObjectHeaderModel.

        The min depth.  # noqa: E501

        :param depth_min: The depth_min of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._depth_min = depth_min

    @property
    def depth_max(self):
        """Gets the depth_max of this ObjectHeaderModel.  # noqa: E501

        The min depth.  # noqa: E501

        :return: The depth_max of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._depth_max

    @depth_max.setter
    def depth_max(self, depth_max):
        """Sets the depth_max of this ObjectHeaderModel.

        The min depth.  # noqa: E501

        :param depth_max: The depth_max of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._depth_max = depth_max

    @property
    def objdate(self):
        """Gets the objdate of this ObjectHeaderModel.  # noqa: E501


        :return: The objdate of this ObjectHeaderModel.  # noqa: E501
        :rtype: date
        """
        return self._objdate

    @objdate.setter
    def objdate(self, objdate):
        """Sets the objdate of this ObjectHeaderModel.


        :param objdate: The objdate of this ObjectHeaderModel.  # noqa: E501
        :type: date
        """

        self._objdate = objdate

    @property
    def classif_qual(self):
        """Gets the classif_qual of this ObjectHeaderModel.  # noqa: E501

        The classification qualification. Could be **P** for predicted, **V** for validated or **D** for Dubious.  # noqa: E501

        :return: The classif_qual of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._classif_qual

    @classif_qual.setter
    def classif_qual(self, classif_qual):
        """Sets the classif_qual of this ObjectHeaderModel.

        The classification qualification. Could be **P** for predicted, **V** for validated or **D** for Dubious.  # noqa: E501

        :param classif_qual: The classif_qual of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._classif_qual = classif_qual

    @property
    def sunpos(self):
        """Gets the sunpos of this ObjectHeaderModel.  # noqa: E501

        Sun position, from date, time and coords.  # noqa: E501

        :return: The sunpos of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._sunpos

    @sunpos.setter
    def sunpos(self, sunpos):
        """Sets the sunpos of this ObjectHeaderModel.

        Sun position, from date, time and coords.  # noqa: E501

        :param sunpos: The sunpos of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._sunpos = sunpos

    @property
    def classif_when(self):
        """Gets the classif_when of this ObjectHeaderModel.  # noqa: E501

        The classification date.  # noqa: E501

        :return: The classif_when of this ObjectHeaderModel.  # noqa: E501
        :rtype: datetime
        """
        return self._classif_when

    @classif_when.setter
    def classif_when(self, classif_when):
        """Sets the classif_when of this ObjectHeaderModel.

        The classification date.  # noqa: E501

        :param classif_when: The classif_when of this ObjectHeaderModel.  # noqa: E501
        :type: datetime
        """

        self._classif_when = classif_when

    @property
    def classif_who(self):
        """Gets the classif_who of this ObjectHeaderModel.  # noqa: E501

        The user who manualy classify this object.  # noqa: E501

        :return: The classif_who of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_who

    @classif_who.setter
    def classif_who(self, classif_who):
        """Sets the classif_who of this ObjectHeaderModel.

        The user who manualy classify this object.  # noqa: E501

        :param classif_who: The classif_who of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_who = classif_who

    @property
    def classif_auto_id(self):
        """Gets the classif_auto_id of this ObjectHeaderModel.  # noqa: E501

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'.   # noqa: E501

        :return: The classif_auto_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_auto_id

    @classif_auto_id.setter
    def classif_auto_id(self, classif_auto_id):
        """Sets the classif_auto_id of this ObjectHeaderModel.

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'.   # noqa: E501

        :param classif_auto_id: The classif_auto_id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_auto_id = classif_auto_id

    @property
    def classif_auto_when(self):
        """Gets the classif_auto_when of this ObjectHeaderModel.  # noqa: E501

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'. The classification date.  # noqa: E501

        :return: The classif_auto_when of this ObjectHeaderModel.  # noqa: E501
        :rtype: datetime
        """
        return self._classif_auto_when

    @classif_auto_when.setter
    def classif_auto_when(self, classif_auto_when):
        """Sets the classif_auto_when of this ObjectHeaderModel.

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'. The classification date.  # noqa: E501

        :param classif_auto_when: The classif_auto_when of this ObjectHeaderModel.  # noqa: E501
        :type: datetime
        """

        self._classif_auto_when = classif_auto_when

    @property
    def classif_auto_score(self):
        """Gets the classif_auto_score of this ObjectHeaderModel.  # noqa: E501

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'. The classification auto score is generally between 0 and 1. This is a confidence score, in the fact that, the taxon prediction for this object is correct.  # noqa: E501

        :return: The classif_auto_score of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._classif_auto_score

    @classif_auto_score.setter
    def classif_auto_score(self, classif_auto_score):
        """Sets the classif_auto_score of this ObjectHeaderModel.

        Set if the object was ever predicted, remain forever with these value. Reflect the 'last state' only if classif_qual is 'P'. The classification auto score is generally between 0 and 1. This is a confidence score, in the fact that, the taxon prediction for this object is correct.  # noqa: E501

        :param classif_auto_score: The classif_auto_score of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._classif_auto_score = classif_auto_score

    @property
    def orig_id(self):
        """Gets the orig_id of this ObjectHeaderModel.  # noqa: E501

        Original object ID from initial TSV load.  # noqa: E501

        :return: The orig_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._orig_id

    @orig_id.setter
    def orig_id(self, orig_id):
        """Sets the orig_id of this ObjectHeaderModel.

        Original object ID from initial TSV load.  # noqa: E501

        :param orig_id: The orig_id of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and orig_id is None:  # noqa: E501
            raise ValueError("Invalid value for `orig_id`, must not be `None`")  # noqa: E501

        self._orig_id = orig_id

    @property
    def object_link(self):
        """Gets the object_link of this ObjectHeaderModel.  # noqa: E501

        Object link.  # noqa: E501

        :return: The object_link of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._object_link

    @object_link.setter
    def object_link(self, object_link):
        """Sets the object_link of this ObjectHeaderModel.

        Object link.  # noqa: E501

        :param object_link: The object_link of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._object_link = object_link

    @property
    def complement_info(self):
        """Gets the complement_info of this ObjectHeaderModel.  # noqa: E501


        :return: The complement_info of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._complement_info

    @complement_info.setter
    def complement_info(self, complement_info):
        """Sets the complement_info of this ObjectHeaderModel.


        :param complement_info: The complement_info of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._complement_info = complement_info

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
        if not isinstance(other, ObjectHeaderModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ObjectHeaderModel):
            return True

        return self.to_dict() != other.to_dict()
