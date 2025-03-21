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


class SummaryExportReq(object):
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
        'collection_id': 'int',
        'project_id': 'AnyOfintegerstring',
        'quantity': 'SummaryExportQuantitiesOptionsEnum',
        'summarise_by': 'SummaryExportSumOptionsEnum',
        'taxo_mapping': 'dict(str, int)',
        'formulae': 'dict(str, str)',
        'out_to_ftp': 'bool'
    }

    attribute_map = {
        'collection_id': 'collection_id',
        'project_id': 'project_id',
        'quantity': 'quantity',
        'summarise_by': 'summarise_by',
        'taxo_mapping': 'taxo_mapping',
        'formulae': 'formulae',
        'out_to_ftp': 'out_to_ftp'
    }

    def __init__(self, collection_id=None, project_id=None, quantity=None, summarise_by=None, taxo_mapping=None, formulae=None, out_to_ftp=False, local_vars_configuration=None):  # noqa: E501
        """SummaryExportReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._collection_id = None
        self._project_id = None
        self._quantity = None
        self._summarise_by = None
        self._taxo_mapping = None
        self._formulae = None
        self._out_to_ftp = None
        self.discriminator = None

        if collection_id is not None:
            self.collection_id = collection_id
        self.project_id = project_id
        if quantity is not None:
            self.quantity = quantity
        if summarise_by is not None:
            self.summarise_by = summarise_by
        if taxo_mapping is not None:
            self.taxo_mapping = taxo_mapping
        if formulae is not None:
            self.formulae = formulae
        if out_to_ftp is not None:
            self.out_to_ftp = out_to_ftp

    @property
    def collection_id(self):
        """Gets the collection_id of this SummaryExportReq.  # noqa: E501

        The Collection to export if requested.  # noqa: E501

        :return: The collection_id of this SummaryExportReq.  # noqa: E501
        :rtype: int
        """
        return self._collection_id

    @collection_id.setter
    def collection_id(self, collection_id):
        """Sets the collection_id of this SummaryExportReq.

        The Collection to export if requested.  # noqa: E501

        :param collection_id: The collection_id of this SummaryExportReq.  # noqa: E501
        :type: int
        """

        self._collection_id = collection_id

    @property
    def project_id(self):
        """Gets the project_id of this SummaryExportReq.  # noqa: E501

        The project(int) or projects (str, project ids list) to export.  # noqa: E501

        :return: The project_id of this SummaryExportReq.  # noqa: E501
        :rtype: AnyOfintegerstring
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this SummaryExportReq.

        The project(int) or projects (str, project ids list) to export.  # noqa: E501

        :param project_id: The project_id of this SummaryExportReq.  # noqa: E501
        :type: AnyOfintegerstring
        """
        if self.local_vars_configuration.client_side_validation and project_id is None:  # noqa: E501
            raise ValueError("Invalid value for `project_id`, must not be `None`")  # noqa: E501

        self._project_id = project_id

    @property
    def quantity(self):
        """Gets the quantity of this SummaryExportReq.  # noqa: E501

        The quantity to compute. Abundance is always possible.  # noqa: E501

        :return: The quantity of this SummaryExportReq.  # noqa: E501
        :rtype: SummaryExportQuantitiesOptionsEnum
        """
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        """Sets the quantity of this SummaryExportReq.

        The quantity to compute. Abundance is always possible.  # noqa: E501

        :param quantity: The quantity of this SummaryExportReq.  # noqa: E501
        :type: SummaryExportQuantitiesOptionsEnum
        """

        self._quantity = quantity

    @property
    def summarise_by(self):
        """Gets the summarise_by of this SummaryExportReq.  # noqa: E501

        Computations aggregation level.  # noqa: E501

        :return: The summarise_by of this SummaryExportReq.  # noqa: E501
        :rtype: SummaryExportSumOptionsEnum
        """
        return self._summarise_by

    @summarise_by.setter
    def summarise_by(self, summarise_by):
        """Sets the summarise_by of this SummaryExportReq.

        Computations aggregation level.  # noqa: E501

        :param summarise_by: The summarise_by of this SummaryExportReq.  # noqa: E501
        :type: SummaryExportSumOptionsEnum
        """

        self._summarise_by = summarise_by

    @property
    def taxo_mapping(self):
        """Gets the taxo_mapping of this SummaryExportReq.  # noqa: E501

        Mapping from present taxon (key) to output replacement one (value). Use a 0 replacement to _discard_ the present taxon.  # noqa: E501

        :return: The taxo_mapping of this SummaryExportReq.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._taxo_mapping

    @taxo_mapping.setter
    def taxo_mapping(self, taxo_mapping):
        """Sets the taxo_mapping of this SummaryExportReq.

        Mapping from present taxon (key) to output replacement one (value). Use a 0 replacement to _discard_ the present taxon.  # noqa: E501

        :param taxo_mapping: The taxo_mapping of this SummaryExportReq.  # noqa: E501
        :type: dict(str, int)
        """

        self._taxo_mapping = taxo_mapping

    @property
    def formulae(self):
        """Gets the formulae of this SummaryExportReq.  # noqa: E501

        Transitory: How to get values from DB free columns. Python syntax, prefixes are 'sam', 'ssm' and 'obj'.Variables used in computations are 'total_water_volume', 'subsample_coef' and 'individual_volume'  # noqa: E501

        :return: The formulae of this SummaryExportReq.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._formulae

    @formulae.setter
    def formulae(self, formulae):
        """Sets the formulae of this SummaryExportReq.

        Transitory: How to get values from DB free columns. Python syntax, prefixes are 'sam', 'ssm' and 'obj'.Variables used in computations are 'total_water_volume', 'subsample_coef' and 'individual_volume'  # noqa: E501

        :param formulae: The formulae of this SummaryExportReq.  # noqa: E501
        :type: dict(str, str)
        """

        self._formulae = formulae

    @property
    def out_to_ftp(self):
        """Gets the out_to_ftp of this SummaryExportReq.  # noqa: E501

        Copy result file to FTP area. Original file is still available.  # noqa: E501

        :return: The out_to_ftp of this SummaryExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._out_to_ftp

    @out_to_ftp.setter
    def out_to_ftp(self, out_to_ftp):
        """Sets the out_to_ftp of this SummaryExportReq.

        Copy result file to FTP area. Original file is still available.  # noqa: E501

        :param out_to_ftp: The out_to_ftp of this SummaryExportReq.  # noqa: E501
        :type: bool
        """

        self._out_to_ftp = out_to_ftp

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
        if not isinstance(other, SummaryExportReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SummaryExportReq):
            return True

        return self.to_dict() != other.to_dict()
