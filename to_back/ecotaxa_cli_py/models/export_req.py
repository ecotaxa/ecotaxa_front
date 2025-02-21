# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.40
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ExportReq(object):
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
        'exp_type': 'ExportTypeEnum',
        'use_latin1': 'bool',
        'tsv_entities': 'str',
        'only_annotations': 'bool',
        'split_by': 'str',
        'coma_as_separator': 'bool',
        'format_dates_times': 'bool',
        'with_images': 'bool',
        'with_internal_ids': 'bool',
        'with_types_row': 'bool',
        'only_first_image': 'bool',
        'sum_subtotal': 'SummaryExportGroupingEnum',
        'pre_mapping': 'dict(str, int)',
        'formulae': 'dict(str, str)',
        'out_to_ftp': 'bool'
    }

    attribute_map = {
        'collection_id': 'collection_id',
        'project_id': 'project_id',
        'exp_type': 'exp_type',
        'use_latin1': 'use_latin1',
        'tsv_entities': 'tsv_entities',
        'only_annotations': 'only_annotations',
        'split_by': 'split_by',
        'coma_as_separator': 'coma_as_separator',
        'format_dates_times': 'format_dates_times',
        'with_images': 'with_images',
        'with_internal_ids': 'with_internal_ids',
        'with_types_row': 'with_types_row',
        'only_first_image': 'only_first_image',
        'sum_subtotal': 'sum_subtotal',
        'pre_mapping': 'pre_mapping',
        'formulae': 'formulae',
        'out_to_ftp': 'out_to_ftp'
    }

    def __init__(self, collection_id=None, project_id=None, exp_type=None, use_latin1=False, tsv_entities='', only_annotations=False, split_by='', coma_as_separator=False, format_dates_times=True, with_images=False, with_internal_ids=False, with_types_row=False, only_first_image=False, sum_subtotal=None, pre_mapping=None, formulae=None, out_to_ftp=False, local_vars_configuration=None):  # noqa: E501
        """ExportReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._collection_id = None
        self._project_id = None
        self._exp_type = None
        self._use_latin1 = None
        self._tsv_entities = None
        self._only_annotations = None
        self._split_by = None
        self._coma_as_separator = None
        self._format_dates_times = None
        self._with_images = None
        self._with_internal_ids = None
        self._with_types_row = None
        self._only_first_image = None
        self._sum_subtotal = None
        self._pre_mapping = None
        self._formulae = None
        self._out_to_ftp = None
        self.discriminator = None

        if collection_id is not None:
            self.collection_id = collection_id
        self.project_id = project_id
        self.exp_type = exp_type
        if use_latin1 is not None:
            self.use_latin1 = use_latin1
        if tsv_entities is not None:
            self.tsv_entities = tsv_entities
        if only_annotations is not None:
            self.only_annotations = only_annotations
        if split_by is not None:
            self.split_by = split_by
        if coma_as_separator is not None:
            self.coma_as_separator = coma_as_separator
        if format_dates_times is not None:
            self.format_dates_times = format_dates_times
        if with_images is not None:
            self.with_images = with_images
        if with_internal_ids is not None:
            self.with_internal_ids = with_internal_ids
        if with_types_row is not None:
            self.with_types_row = with_types_row
        if only_first_image is not None:
            self.only_first_image = only_first_image
        if sum_subtotal is not None:
            self.sum_subtotal = sum_subtotal
        if pre_mapping is not None:
            self.pre_mapping = pre_mapping
        if formulae is not None:
            self.formulae = formulae
        if out_to_ftp is not None:
            self.out_to_ftp = out_to_ftp

    @property
    def collection_id(self):
        """Gets the collection_id of this ExportReq.  # noqa: E501

        The Collection to export if requested.  # noqa: E501

        :return: The collection_id of this ExportReq.  # noqa: E501
        :rtype: int
        """
        return self._collection_id

    @collection_id.setter
    def collection_id(self, collection_id):
        """Sets the collection_id of this ExportReq.

        The Collection to export if requested.  # noqa: E501

        :param collection_id: The collection_id of this ExportReq.  # noqa: E501
        :type: int
        """

        self._collection_id = collection_id

    @property
    def project_id(self):
        """Gets the project_id of this ExportReq.  # noqa: E501

        The project(int) or projects (str, project ids list) to export.  # noqa: E501

        :return: The project_id of this ExportReq.  # noqa: E501
        :rtype: AnyOfintegerstring
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this ExportReq.

        The project(int) or projects (str, project ids list) to export.  # noqa: E501

        :param project_id: The project_id of this ExportReq.  # noqa: E501
        :type: AnyOfintegerstring
        """
        if self.local_vars_configuration.client_side_validation and project_id is None:  # noqa: E501
            raise ValueError("Invalid value for `project_id`, must not be `None`")  # noqa: E501

        self._project_id = project_id

    @property
    def exp_type(self):
        """Gets the exp_type of this ExportReq.  # noqa: E501

        The export type.  # noqa: E501

        :return: The exp_type of this ExportReq.  # noqa: E501
        :rtype: ExportTypeEnum
        """
        return self._exp_type

    @exp_type.setter
    def exp_type(self, exp_type):
        """Sets the exp_type of this ExportReq.

        The export type.  # noqa: E501

        :param exp_type: The exp_type of this ExportReq.  # noqa: E501
        :type: ExportTypeEnum
        """
        if self.local_vars_configuration.client_side_validation and exp_type is None:  # noqa: E501
            raise ValueError("Invalid value for `exp_type`, must not be `None`")  # noqa: E501

        self._exp_type = exp_type

    @property
    def use_latin1(self):
        """Gets the use_latin1 of this ExportReq.  # noqa: E501

        Export using latin 1 character set, AKA iso-8859-1. Default is utf-8.  # noqa: E501

        :return: The use_latin1 of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._use_latin1

    @use_latin1.setter
    def use_latin1(self, use_latin1):
        """Sets the use_latin1 of this ExportReq.

        Export using latin 1 character set, AKA iso-8859-1. Default is utf-8.  # noqa: E501

        :param use_latin1: The use_latin1 of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._use_latin1 = use_latin1

    @property
    def tsv_entities(self):
        """Gets the tsv_entities of this ExportReq.  # noqa: E501

        For 'TSV' type, the entities to export, one letter for each of O(bject), P(rocess), A(cquisition), S(ample), C(omments).  # noqa: E501

        :return: The tsv_entities of this ExportReq.  # noqa: E501
        :rtype: str
        """
        return self._tsv_entities

    @tsv_entities.setter
    def tsv_entities(self, tsv_entities):
        """Sets the tsv_entities of this ExportReq.

        For 'TSV' type, the entities to export, one letter for each of O(bject), P(rocess), A(cquisition), S(ample), C(omments).  # noqa: E501

        :param tsv_entities: The tsv_entities of this ExportReq.  # noqa: E501
        :type: str
        """

        self._tsv_entities = tsv_entities

    @property
    def only_annotations(self):
        """Gets the only_annotations of this ExportReq.  # noqa: E501

        For 'BAK' type, only save objects' last annotation data in backup.  # noqa: E501

        :return: The only_annotations of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._only_annotations

    @only_annotations.setter
    def only_annotations(self, only_annotations):
        """Sets the only_annotations of this ExportReq.

        For 'BAK' type, only save objects' last annotation data in backup.  # noqa: E501

        :param only_annotations: The only_annotations of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._only_annotations = only_annotations

    @property
    def split_by(self):
        """Gets the split_by of this ExportReq.  # noqa: E501

        For 'TSV' type, inside archives, split in one directory per... 'sample', 'acquisition', 'taxon' or '' (no split).  # noqa: E501

        :return: The split_by of this ExportReq.  # noqa: E501
        :rtype: str
        """
        return self._split_by

    @split_by.setter
    def split_by(self, split_by):
        """Sets the split_by of this ExportReq.

        For 'TSV' type, inside archives, split in one directory per... 'sample', 'acquisition', 'taxon' or '' (no split).  # noqa: E501

        :param split_by: The split_by of this ExportReq.  # noqa: E501
        :type: str
        """

        self._split_by = split_by

    @property
    def coma_as_separator(self):
        """Gets the coma_as_separator of this ExportReq.  # noqa: E501

        For 'TSV' type, use a , instead of . for decimal separator.  # noqa: E501

        :return: The coma_as_separator of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._coma_as_separator

    @coma_as_separator.setter
    def coma_as_separator(self, coma_as_separator):
        """Sets the coma_as_separator of this ExportReq.

        For 'TSV' type, use a , instead of . for decimal separator.  # noqa: E501

        :param coma_as_separator: The coma_as_separator of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._coma_as_separator = coma_as_separator

    @property
    def format_dates_times(self):
        """Gets the format_dates_times of this ExportReq.  # noqa: E501

        For 'TSV' type, format dates and times using - and : respectively.  # noqa: E501

        :return: The format_dates_times of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._format_dates_times

    @format_dates_times.setter
    def format_dates_times(self, format_dates_times):
        """Sets the format_dates_times of this ExportReq.

        For 'TSV' type, format dates and times using - and : respectively.  # noqa: E501

        :param format_dates_times: The format_dates_times of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._format_dates_times = format_dates_times

    @property
    def with_images(self):
        """Gets the with_images of this ExportReq.  # noqa: E501

        For 'BAK' and 'DOI' types, export images as well.  # noqa: E501

        :return: The with_images of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._with_images

    @with_images.setter
    def with_images(self, with_images):
        """Sets the with_images of this ExportReq.

        For 'BAK' and 'DOI' types, export images as well.  # noqa: E501

        :param with_images: The with_images of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._with_images = with_images

    @property
    def with_internal_ids(self):
        """Gets the with_internal_ids of this ExportReq.  # noqa: E501

        For 'TSV' type, export internal DB IDs.  # noqa: E501

        :return: The with_internal_ids of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._with_internal_ids

    @with_internal_ids.setter
    def with_internal_ids(self, with_internal_ids):
        """Sets the with_internal_ids of this ExportReq.

        For 'TSV' type, export internal DB IDs.  # noqa: E501

        :param with_internal_ids: The with_internal_ids of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._with_internal_ids = with_internal_ids

    @property
    def with_types_row(self):
        """Gets the with_types_row of this ExportReq.  # noqa: E501

        Add an EcoTaxa-compatible second line with types.  # noqa: E501

        :return: The with_types_row of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._with_types_row

    @with_types_row.setter
    def with_types_row(self, with_types_row):
        """Sets the with_types_row of this ExportReq.

        Add an EcoTaxa-compatible second line with types.  # noqa: E501

        :param with_types_row: The with_types_row of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._with_types_row = with_types_row

    @property
    def only_first_image(self):
        """Gets the only_first_image of this ExportReq.  # noqa: E501

        For 'DOI' type, export only first (displayed) image.  # noqa: E501

        :return: The only_first_image of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._only_first_image

    @only_first_image.setter
    def only_first_image(self, only_first_image):
        """Sets the only_first_image of this ExportReq.

        For 'DOI' type, export only first (displayed) image.  # noqa: E501

        :param only_first_image: The only_first_image of this ExportReq.  # noqa: E501
        :type: bool
        """

        self._only_first_image = only_first_image

    @property
    def sum_subtotal(self):
        """Gets the sum_subtotal of this ExportReq.  # noqa: E501

        For 'SUM', 'ABO', 'CNC' and 'BIV' types, if computations should be combined. Per A(cquisition) or S(ample) or <Empty>(just taxa).  # noqa: E501

        :return: The sum_subtotal of this ExportReq.  # noqa: E501
        :rtype: SummaryExportGroupingEnum
        """
        return self._sum_subtotal

    @sum_subtotal.setter
    def sum_subtotal(self, sum_subtotal):
        """Sets the sum_subtotal of this ExportReq.

        For 'SUM', 'ABO', 'CNC' and 'BIV' types, if computations should be combined. Per A(cquisition) or S(ample) or <Empty>(just taxa).  # noqa: E501

        :param sum_subtotal: The sum_subtotal of this ExportReq.  # noqa: E501
        :type: SummaryExportGroupingEnum
        """

        self._sum_subtotal = sum_subtotal

    @property
    def pre_mapping(self):
        """Gets the pre_mapping of this ExportReq.  # noqa: E501

        For 'ABO', 'CNC' and 'BIV' types types, mapping from present taxon (key) to output replacement one (value). Use a null replacement to _discard_ the present taxon.  # noqa: E501

        :return: The pre_mapping of this ExportReq.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._pre_mapping

    @pre_mapping.setter
    def pre_mapping(self, pre_mapping):
        """Sets the pre_mapping of this ExportReq.

        For 'ABO', 'CNC' and 'BIV' types types, mapping from present taxon (key) to output replacement one (value). Use a null replacement to _discard_ the present taxon.  # noqa: E501

        :param pre_mapping: The pre_mapping of this ExportReq.  # noqa: E501
        :type: dict(str, int)
        """

        self._pre_mapping = pre_mapping

    @property
    def formulae(self):
        """Gets the formulae of this ExportReq.  # noqa: E501

        Transitory: For 'CNC' and 'BIV' type, how to get values from DB free columns. Python syntax, prefixes are 'sam', 'ssm' and 'obj'.Variables used in computations are 'total_water_volume', 'subsample_coef' and 'individual_volume'  # noqa: E501

        :return: The formulae of this ExportReq.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._formulae

    @formulae.setter
    def formulae(self, formulae):
        """Sets the formulae of this ExportReq.

        Transitory: For 'CNC' and 'BIV' type, how to get values from DB free columns. Python syntax, prefixes are 'sam', 'ssm' and 'obj'.Variables used in computations are 'total_water_volume', 'subsample_coef' and 'individual_volume'  # noqa: E501

        :param formulae: The formulae of this ExportReq.  # noqa: E501
        :type: dict(str, str)
        """

        self._formulae = formulae

    @property
    def out_to_ftp(self):
        """Gets the out_to_ftp of this ExportReq.  # noqa: E501

        Copy result file to FTP area. Original file is still available.  # noqa: E501

        :return: The out_to_ftp of this ExportReq.  # noqa: E501
        :rtype: bool
        """
        return self._out_to_ftp

    @out_to_ftp.setter
    def out_to_ftp(self, out_to_ftp):
        """Sets the out_to_ftp of this ExportReq.

        Copy result file to FTP area. Original file is still available.  # noqa: E501

        :param out_to_ftp: The out_to_ftp of this ExportReq.  # noqa: E501
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
        if not isinstance(other, ExportReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExportReq):
            return True

        return self.to_dict() != other.to_dict()
