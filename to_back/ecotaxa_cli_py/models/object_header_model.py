# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.4
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
        'projid': 'int',
        'objdate': 'date',
        'objtime': 'str',
        'latitude': 'float',
        'longitude': 'float',
        'depth_min': 'float',
        'depth_max': 'float',
        'sunpos': 'str',
        'classif_id': 'int',
        'classif_qual': 'str',
        'classif_who': 'int',
        'classif_when': 'datetime',
        'classif_auto_id': 'int',
        'classif_auto_score': 'float',
        'classif_auto_when': 'datetime',
        'classif_crossvalidation_id': 'int',
        'img0id': 'int',
        'imgcount': 'int',
        'complement_info': 'str',
        'similarity': 'float',
        'random_value': 'int',
        'sampleid': 'int',
        'acquisid': 'int',
        'processid': 'int'
    }

    attribute_map = {
        'objid': 'objid',
        'projid': 'projid',
        'objdate': 'objdate',
        'objtime': 'objtime',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'depth_min': 'depth_min',
        'depth_max': 'depth_max',
        'sunpos': 'sunpos',
        'classif_id': 'classif_id',
        'classif_qual': 'classif_qual',
        'classif_who': 'classif_who',
        'classif_when': 'classif_when',
        'classif_auto_id': 'classif_auto_id',
        'classif_auto_score': 'classif_auto_score',
        'classif_auto_when': 'classif_auto_when',
        'classif_crossvalidation_id': 'classif_crossvalidation_id',
        'img0id': 'img0id',
        'imgcount': 'imgcount',
        'complement_info': 'complement_info',
        'similarity': 'similarity',
        'random_value': 'random_value',
        'sampleid': 'sampleid',
        'acquisid': 'acquisid',
        'processid': 'processid'
    }

    def __init__(self, objid=None, projid=None, objdate=None, objtime=None, latitude=None, longitude=None, depth_min=None, depth_max=None, sunpos=None, classif_id=None, classif_qual=None, classif_who=None, classif_when=None, classif_auto_id=None, classif_auto_score=None, classif_auto_when=None, classif_crossvalidation_id=None, img0id=None, imgcount=None, complement_info=None, similarity=None, random_value=None, sampleid=None, acquisid=None, processid=None, local_vars_configuration=None):  # noqa: E501
        """ObjectHeaderModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._objid = None
        self._projid = None
        self._objdate = None
        self._objtime = None
        self._latitude = None
        self._longitude = None
        self._depth_min = None
        self._depth_max = None
        self._sunpos = None
        self._classif_id = None
        self._classif_qual = None
        self._classif_who = None
        self._classif_when = None
        self._classif_auto_id = None
        self._classif_auto_score = None
        self._classif_auto_when = None
        self._classif_crossvalidation_id = None
        self._img0id = None
        self._imgcount = None
        self._complement_info = None
        self._similarity = None
        self._random_value = None
        self._sampleid = None
        self._acquisid = None
        self._processid = None
        self.discriminator = None

        if objid is not None:
            self.objid = objid
        self.projid = projid
        if objdate is not None:
            self.objdate = objdate
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
        if sunpos is not None:
            self.sunpos = sunpos
        if classif_id is not None:
            self.classif_id = classif_id
        if classif_qual is not None:
            self.classif_qual = classif_qual
        if classif_who is not None:
            self.classif_who = classif_who
        if classif_when is not None:
            self.classif_when = classif_when
        if classif_auto_id is not None:
            self.classif_auto_id = classif_auto_id
        if classif_auto_score is not None:
            self.classif_auto_score = classif_auto_score
        if classif_auto_when is not None:
            self.classif_auto_when = classif_auto_when
        if classif_crossvalidation_id is not None:
            self.classif_crossvalidation_id = classif_crossvalidation_id
        if img0id is not None:
            self.img0id = img0id
        if imgcount is not None:
            self.imgcount = imgcount
        if complement_info is not None:
            self.complement_info = complement_info
        if similarity is not None:
            self.similarity = similarity
        if random_value is not None:
            self.random_value = random_value
        if sampleid is not None:
            self.sampleid = sampleid
        if acquisid is not None:
            self.acquisid = acquisid
        if processid is not None:
            self.processid = processid

    @property
    def objid(self):
        """Gets the objid of this ObjectHeaderModel.  # noqa: E501


        :return: The objid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._objid

    @objid.setter
    def objid(self, objid):
        """Sets the objid of this ObjectHeaderModel.


        :param objid: The objid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._objid = objid

    @property
    def projid(self):
        """Gets the projid of this ObjectHeaderModel.  # noqa: E501


        :return: The projid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._projid

    @projid.setter
    def projid(self, projid):
        """Sets the projid of this ObjectHeaderModel.


        :param projid: The projid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and projid is None:  # noqa: E501
            raise ValueError("Invalid value for `projid`, must not be `None`")  # noqa: E501

        self._projid = projid

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


        :return: The latitude of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """Sets the latitude of this ObjectHeaderModel.


        :param latitude: The latitude of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._latitude = latitude

    @property
    def longitude(self):
        """Gets the longitude of this ObjectHeaderModel.  # noqa: E501


        :return: The longitude of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """Sets the longitude of this ObjectHeaderModel.


        :param longitude: The longitude of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._longitude = longitude

    @property
    def depth_min(self):
        """Gets the depth_min of this ObjectHeaderModel.  # noqa: E501


        :return: The depth_min of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._depth_min

    @depth_min.setter
    def depth_min(self, depth_min):
        """Sets the depth_min of this ObjectHeaderModel.


        :param depth_min: The depth_min of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._depth_min = depth_min

    @property
    def depth_max(self):
        """Gets the depth_max of this ObjectHeaderModel.  # noqa: E501


        :return: The depth_max of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._depth_max

    @depth_max.setter
    def depth_max(self, depth_max):
        """Sets the depth_max of this ObjectHeaderModel.


        :param depth_max: The depth_max of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._depth_max = depth_max

    @property
    def sunpos(self):
        """Gets the sunpos of this ObjectHeaderModel.  # noqa: E501


        :return: The sunpos of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._sunpos

    @sunpos.setter
    def sunpos(self, sunpos):
        """Sets the sunpos of this ObjectHeaderModel.


        :param sunpos: The sunpos of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._sunpos = sunpos

    @property
    def classif_id(self):
        """Gets the classif_id of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_id

    @classif_id.setter
    def classif_id(self, classif_id):
        """Sets the classif_id of this ObjectHeaderModel.


        :param classif_id: The classif_id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_id = classif_id

    @property
    def classif_qual(self):
        """Gets the classif_qual of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_qual of this ObjectHeaderModel.  # noqa: E501
        :rtype: str
        """
        return self._classif_qual

    @classif_qual.setter
    def classif_qual(self, classif_qual):
        """Sets the classif_qual of this ObjectHeaderModel.


        :param classif_qual: The classif_qual of this ObjectHeaderModel.  # noqa: E501
        :type: str
        """

        self._classif_qual = classif_qual

    @property
    def classif_who(self):
        """Gets the classif_who of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_who of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_who

    @classif_who.setter
    def classif_who(self, classif_who):
        """Sets the classif_who of this ObjectHeaderModel.


        :param classif_who: The classif_who of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_who = classif_who

    @property
    def classif_when(self):
        """Gets the classif_when of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_when of this ObjectHeaderModel.  # noqa: E501
        :rtype: datetime
        """
        return self._classif_when

    @classif_when.setter
    def classif_when(self, classif_when):
        """Sets the classif_when of this ObjectHeaderModel.


        :param classif_when: The classif_when of this ObjectHeaderModel.  # noqa: E501
        :type: datetime
        """

        self._classif_when = classif_when

    @property
    def classif_auto_id(self):
        """Gets the classif_auto_id of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_auto_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_auto_id

    @classif_auto_id.setter
    def classif_auto_id(self, classif_auto_id):
        """Sets the classif_auto_id of this ObjectHeaderModel.


        :param classif_auto_id: The classif_auto_id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_auto_id = classif_auto_id

    @property
    def classif_auto_score(self):
        """Gets the classif_auto_score of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_auto_score of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._classif_auto_score

    @classif_auto_score.setter
    def classif_auto_score(self, classif_auto_score):
        """Sets the classif_auto_score of this ObjectHeaderModel.


        :param classif_auto_score: The classif_auto_score of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._classif_auto_score = classif_auto_score

    @property
    def classif_auto_when(self):
        """Gets the classif_auto_when of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_auto_when of this ObjectHeaderModel.  # noqa: E501
        :rtype: datetime
        """
        return self._classif_auto_when

    @classif_auto_when.setter
    def classif_auto_when(self, classif_auto_when):
        """Sets the classif_auto_when of this ObjectHeaderModel.


        :param classif_auto_when: The classif_auto_when of this ObjectHeaderModel.  # noqa: E501
        :type: datetime
        """

        self._classif_auto_when = classif_auto_when

    @property
    def classif_crossvalidation_id(self):
        """Gets the classif_crossvalidation_id of this ObjectHeaderModel.  # noqa: E501


        :return: The classif_crossvalidation_id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._classif_crossvalidation_id

    @classif_crossvalidation_id.setter
    def classif_crossvalidation_id(self, classif_crossvalidation_id):
        """Sets the classif_crossvalidation_id of this ObjectHeaderModel.


        :param classif_crossvalidation_id: The classif_crossvalidation_id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._classif_crossvalidation_id = classif_crossvalidation_id

    @property
    def img0id(self):
        """Gets the img0id of this ObjectHeaderModel.  # noqa: E501


        :return: The img0id of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._img0id

    @img0id.setter
    def img0id(self, img0id):
        """Sets the img0id of this ObjectHeaderModel.


        :param img0id: The img0id of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._img0id = img0id

    @property
    def imgcount(self):
        """Gets the imgcount of this ObjectHeaderModel.  # noqa: E501


        :return: The imgcount of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._imgcount

    @imgcount.setter
    def imgcount(self, imgcount):
        """Sets the imgcount of this ObjectHeaderModel.


        :param imgcount: The imgcount of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._imgcount = imgcount

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

    @property
    def similarity(self):
        """Gets the similarity of this ObjectHeaderModel.  # noqa: E501


        :return: The similarity of this ObjectHeaderModel.  # noqa: E501
        :rtype: float
        """
        return self._similarity

    @similarity.setter
    def similarity(self, similarity):
        """Sets the similarity of this ObjectHeaderModel.


        :param similarity: The similarity of this ObjectHeaderModel.  # noqa: E501
        :type: float
        """

        self._similarity = similarity

    @property
    def random_value(self):
        """Gets the random_value of this ObjectHeaderModel.  # noqa: E501


        :return: The random_value of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._random_value

    @random_value.setter
    def random_value(self, random_value):
        """Sets the random_value of this ObjectHeaderModel.


        :param random_value: The random_value of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._random_value = random_value

    @property
    def sampleid(self):
        """Gets the sampleid of this ObjectHeaderModel.  # noqa: E501


        :return: The sampleid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._sampleid

    @sampleid.setter
    def sampleid(self, sampleid):
        """Sets the sampleid of this ObjectHeaderModel.


        :param sampleid: The sampleid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._sampleid = sampleid

    @property
    def acquisid(self):
        """Gets the acquisid of this ObjectHeaderModel.  # noqa: E501


        :return: The acquisid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._acquisid

    @acquisid.setter
    def acquisid(self, acquisid):
        """Sets the acquisid of this ObjectHeaderModel.


        :param acquisid: The acquisid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._acquisid = acquisid

    @property
    def processid(self):
        """Gets the processid of this ObjectHeaderModel.  # noqa: E501


        :return: The processid of this ObjectHeaderModel.  # noqa: E501
        :rtype: int
        """
        return self._processid

    @processid.setter
    def processid(self, processid):
        """Sets the processid of this ObjectHeaderModel.


        :param processid: The processid of this ObjectHeaderModel.  # noqa: E501
        :type: int
        """

        self._processid = processid

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
