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


class ProjectFiltersDict(object):
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
        'taxo': 'str',
        'taxochild': 'str',
        'statusfilter': 'str',
        'map_n': 'str',
        'map_w': 'str',
        'map_e': 'str',
        'map_s': 'str',
        'depthmin': 'str',
        'depthmax': 'str',
        'samples': 'str',
        'instrum': 'str',
        'daytime': 'str',
        'month': 'str',
        'fromdate': 'str',
        'todate': 'str',
        'fromtime': 'str',
        'totime': 'str',
        'inverttime': 'str',
        'validfromdate': 'str',
        'validtodate': 'str',
        'freenum': 'str',
        'freenumst': 'str',
        'freenumend': 'str',
        'freetxt': 'str',
        'freetxtval': 'str',
        'filt_annot': 'str',
        'filt_last_annot': 'str'
    }

    attribute_map = {
        'taxo': 'taxo',
        'taxochild': 'taxochild',
        'statusfilter': 'statusfilter',
        'map_n': 'MapN',
        'map_w': 'MapW',
        'map_e': 'MapE',
        'map_s': 'MapS',
        'depthmin': 'depthmin',
        'depthmax': 'depthmax',
        'samples': 'samples',
        'instrum': 'instrum',
        'daytime': 'daytime',
        'month': 'month',
        'fromdate': 'fromdate',
        'todate': 'todate',
        'fromtime': 'fromtime',
        'totime': 'totime',
        'inverttime': 'inverttime',
        'validfromdate': 'validfromdate',
        'validtodate': 'validtodate',
        'freenum': 'freenum',
        'freenumst': 'freenumst',
        'freenumend': 'freenumend',
        'freetxt': 'freetxt',
        'freetxtval': 'freetxtval',
        'filt_annot': 'filt_annot',
        'filt_last_annot': 'filt_last_annot'
    }

    def __init__(self, taxo=None, taxochild=None, statusfilter=None, map_n=None, map_w=None, map_e=None, map_s=None, depthmin=None, depthmax=None, samples=None, instrum=None, daytime=None, month=None, fromdate=None, todate=None, fromtime=None, totime=None, inverttime=None, validfromdate=None, validtodate=None, freenum=None, freenumst=None, freenumend=None, freetxt=None, freetxtval=None, filt_annot=None, filt_last_annot=None, local_vars_configuration=None):  # noqa: E501
        """ProjectFiltersDict - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._taxo = None
        self._taxochild = None
        self._statusfilter = None
        self._map_n = None
        self._map_w = None
        self._map_e = None
        self._map_s = None
        self._depthmin = None
        self._depthmax = None
        self._samples = None
        self._instrum = None
        self._daytime = None
        self._month = None
        self._fromdate = None
        self._todate = None
        self._fromtime = None
        self._totime = None
        self._inverttime = None
        self._validfromdate = None
        self._validtodate = None
        self._freenum = None
        self._freenumst = None
        self._freenumend = None
        self._freetxt = None
        self._freetxtval = None
        self._filt_annot = None
        self._filt_last_annot = None
        self.discriminator = None

        if taxo is not None:
            self.taxo = taxo
        if taxochild is not None:
            self.taxochild = taxochild
        if statusfilter is not None:
            self.statusfilter = statusfilter
        if map_n is not None:
            self.map_n = map_n
        if map_w is not None:
            self.map_w = map_w
        if map_e is not None:
            self.map_e = map_e
        if map_s is not None:
            self.map_s = map_s
        if depthmin is not None:
            self.depthmin = depthmin
        if depthmax is not None:
            self.depthmax = depthmax
        if samples is not None:
            self.samples = samples
        if instrum is not None:
            self.instrum = instrum
        if daytime is not None:
            self.daytime = daytime
        if month is not None:
            self.month = month
        if fromdate is not None:
            self.fromdate = fromdate
        if todate is not None:
            self.todate = todate
        if fromtime is not None:
            self.fromtime = fromtime
        if totime is not None:
            self.totime = totime
        if inverttime is not None:
            self.inverttime = inverttime
        if validfromdate is not None:
            self.validfromdate = validfromdate
        if validtodate is not None:
            self.validtodate = validtodate
        if freenum is not None:
            self.freenum = freenum
        if freenumst is not None:
            self.freenumst = freenumst
        if freenumend is not None:
            self.freenumend = freenumend
        if freetxt is not None:
            self.freetxt = freetxt
        if freetxtval is not None:
            self.freetxtval = freetxtval
        if filt_annot is not None:
            self.filt_annot = filt_annot
        if filt_last_annot is not None:
            self.filt_last_annot = filt_last_annot

    @property
    def taxo(self):
        """Gets the taxo of this ProjectFiltersDict.  # noqa: E501


        :return: The taxo of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._taxo

    @taxo.setter
    def taxo(self, taxo):
        """Sets the taxo of this ProjectFiltersDict.


        :param taxo: The taxo of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._taxo = taxo

    @property
    def taxochild(self):
        """Gets the taxochild of this ProjectFiltersDict.  # noqa: E501


        :return: The taxochild of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._taxochild

    @taxochild.setter
    def taxochild(self, taxochild):
        """Sets the taxochild of this ProjectFiltersDict.


        :param taxochild: The taxochild of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._taxochild = taxochild

    @property
    def statusfilter(self):
        """Gets the statusfilter of this ProjectFiltersDict.  # noqa: E501


        :return: The statusfilter of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._statusfilter

    @statusfilter.setter
    def statusfilter(self, statusfilter):
        """Sets the statusfilter of this ProjectFiltersDict.


        :param statusfilter: The statusfilter of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._statusfilter = statusfilter

    @property
    def map_n(self):
        """Gets the map_n of this ProjectFiltersDict.  # noqa: E501


        :return: The map_n of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._map_n

    @map_n.setter
    def map_n(self, map_n):
        """Sets the map_n of this ProjectFiltersDict.


        :param map_n: The map_n of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._map_n = map_n

    @property
    def map_w(self):
        """Gets the map_w of this ProjectFiltersDict.  # noqa: E501


        :return: The map_w of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._map_w

    @map_w.setter
    def map_w(self, map_w):
        """Sets the map_w of this ProjectFiltersDict.


        :param map_w: The map_w of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._map_w = map_w

    @property
    def map_e(self):
        """Gets the map_e of this ProjectFiltersDict.  # noqa: E501


        :return: The map_e of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._map_e

    @map_e.setter
    def map_e(self, map_e):
        """Sets the map_e of this ProjectFiltersDict.


        :param map_e: The map_e of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._map_e = map_e

    @property
    def map_s(self):
        """Gets the map_s of this ProjectFiltersDict.  # noqa: E501


        :return: The map_s of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._map_s

    @map_s.setter
    def map_s(self, map_s):
        """Sets the map_s of this ProjectFiltersDict.


        :param map_s: The map_s of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._map_s = map_s

    @property
    def depthmin(self):
        """Gets the depthmin of this ProjectFiltersDict.  # noqa: E501


        :return: The depthmin of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._depthmin

    @depthmin.setter
    def depthmin(self, depthmin):
        """Sets the depthmin of this ProjectFiltersDict.


        :param depthmin: The depthmin of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._depthmin = depthmin

    @property
    def depthmax(self):
        """Gets the depthmax of this ProjectFiltersDict.  # noqa: E501


        :return: The depthmax of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._depthmax

    @depthmax.setter
    def depthmax(self, depthmax):
        """Sets the depthmax of this ProjectFiltersDict.


        :param depthmax: The depthmax of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._depthmax = depthmax

    @property
    def samples(self):
        """Gets the samples of this ProjectFiltersDict.  # noqa: E501


        :return: The samples of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._samples

    @samples.setter
    def samples(self, samples):
        """Sets the samples of this ProjectFiltersDict.


        :param samples: The samples of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._samples = samples

    @property
    def instrum(self):
        """Gets the instrum of this ProjectFiltersDict.  # noqa: E501


        :return: The instrum of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._instrum

    @instrum.setter
    def instrum(self, instrum):
        """Sets the instrum of this ProjectFiltersDict.


        :param instrum: The instrum of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._instrum = instrum

    @property
    def daytime(self):
        """Gets the daytime of this ProjectFiltersDict.  # noqa: E501


        :return: The daytime of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._daytime

    @daytime.setter
    def daytime(self, daytime):
        """Sets the daytime of this ProjectFiltersDict.


        :param daytime: The daytime of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._daytime = daytime

    @property
    def month(self):
        """Gets the month of this ProjectFiltersDict.  # noqa: E501


        :return: The month of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._month

    @month.setter
    def month(self, month):
        """Sets the month of this ProjectFiltersDict.


        :param month: The month of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._month = month

    @property
    def fromdate(self):
        """Gets the fromdate of this ProjectFiltersDict.  # noqa: E501


        :return: The fromdate of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._fromdate

    @fromdate.setter
    def fromdate(self, fromdate):
        """Sets the fromdate of this ProjectFiltersDict.


        :param fromdate: The fromdate of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._fromdate = fromdate

    @property
    def todate(self):
        """Gets the todate of this ProjectFiltersDict.  # noqa: E501


        :return: The todate of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._todate

    @todate.setter
    def todate(self, todate):
        """Sets the todate of this ProjectFiltersDict.


        :param todate: The todate of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._todate = todate

    @property
    def fromtime(self):
        """Gets the fromtime of this ProjectFiltersDict.  # noqa: E501


        :return: The fromtime of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._fromtime

    @fromtime.setter
    def fromtime(self, fromtime):
        """Sets the fromtime of this ProjectFiltersDict.


        :param fromtime: The fromtime of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._fromtime = fromtime

    @property
    def totime(self):
        """Gets the totime of this ProjectFiltersDict.  # noqa: E501


        :return: The totime of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._totime

    @totime.setter
    def totime(self, totime):
        """Sets the totime of this ProjectFiltersDict.


        :param totime: The totime of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._totime = totime

    @property
    def inverttime(self):
        """Gets the inverttime of this ProjectFiltersDict.  # noqa: E501


        :return: The inverttime of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._inverttime

    @inverttime.setter
    def inverttime(self, inverttime):
        """Sets the inverttime of this ProjectFiltersDict.


        :param inverttime: The inverttime of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._inverttime = inverttime

    @property
    def validfromdate(self):
        """Gets the validfromdate of this ProjectFiltersDict.  # noqa: E501


        :return: The validfromdate of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._validfromdate

    @validfromdate.setter
    def validfromdate(self, validfromdate):
        """Sets the validfromdate of this ProjectFiltersDict.


        :param validfromdate: The validfromdate of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._validfromdate = validfromdate

    @property
    def validtodate(self):
        """Gets the validtodate of this ProjectFiltersDict.  # noqa: E501


        :return: The validtodate of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._validtodate

    @validtodate.setter
    def validtodate(self, validtodate):
        """Sets the validtodate of this ProjectFiltersDict.


        :param validtodate: The validtodate of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._validtodate = validtodate

    @property
    def freenum(self):
        """Gets the freenum of this ProjectFiltersDict.  # noqa: E501


        :return: The freenum of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._freenum

    @freenum.setter
    def freenum(self, freenum):
        """Sets the freenum of this ProjectFiltersDict.


        :param freenum: The freenum of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._freenum = freenum

    @property
    def freenumst(self):
        """Gets the freenumst of this ProjectFiltersDict.  # noqa: E501


        :return: The freenumst of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._freenumst

    @freenumst.setter
    def freenumst(self, freenumst):
        """Sets the freenumst of this ProjectFiltersDict.


        :param freenumst: The freenumst of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._freenumst = freenumst

    @property
    def freenumend(self):
        """Gets the freenumend of this ProjectFiltersDict.  # noqa: E501


        :return: The freenumend of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._freenumend

    @freenumend.setter
    def freenumend(self, freenumend):
        """Sets the freenumend of this ProjectFiltersDict.


        :param freenumend: The freenumend of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._freenumend = freenumend

    @property
    def freetxt(self):
        """Gets the freetxt of this ProjectFiltersDict.  # noqa: E501


        :return: The freetxt of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._freetxt

    @freetxt.setter
    def freetxt(self, freetxt):
        """Sets the freetxt of this ProjectFiltersDict.


        :param freetxt: The freetxt of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._freetxt = freetxt

    @property
    def freetxtval(self):
        """Gets the freetxtval of this ProjectFiltersDict.  # noqa: E501


        :return: The freetxtval of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._freetxtval

    @freetxtval.setter
    def freetxtval(self, freetxtval):
        """Sets the freetxtval of this ProjectFiltersDict.


        :param freetxtval: The freetxtval of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._freetxtval = freetxtval

    @property
    def filt_annot(self):
        """Gets the filt_annot of this ProjectFiltersDict.  # noqa: E501


        :return: The filt_annot of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._filt_annot

    @filt_annot.setter
    def filt_annot(self, filt_annot):
        """Sets the filt_annot of this ProjectFiltersDict.


        :param filt_annot: The filt_annot of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._filt_annot = filt_annot

    @property
    def filt_last_annot(self):
        """Gets the filt_last_annot of this ProjectFiltersDict.  # noqa: E501


        :return: The filt_last_annot of this ProjectFiltersDict.  # noqa: E501
        :rtype: str
        """
        return self._filt_last_annot

    @filt_last_annot.setter
    def filt_last_annot(self, filt_last_annot):
        """Sets the filt_last_annot of this ProjectFiltersDict.


        :param filt_last_annot: The filt_last_annot of this ProjectFiltersDict.  # noqa: E501
        :type: str
        """

        self._filt_last_annot = filt_last_annot

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
        if not isinstance(other, ProjectFiltersDict):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectFiltersDict):
            return True

        return self.to_dict() != other.to_dict()
