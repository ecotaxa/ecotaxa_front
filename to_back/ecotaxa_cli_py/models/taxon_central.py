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


class TaxonCentral(object):
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
        'id': 'int',
        'parent_id': 'int',
        'name': 'str',
        'id_source': 'str',
        'taxotype': 'str',
        'display_name': 'str',
        'lastupdate_datetime': 'datetime',
        'id_instance': 'int',
        'taxostatus': 'str',
        'rename_to': 'int',
        'source_url': 'str',
        'source_desc': 'str',
        'creator_email': 'str',
        'creation_datetime': 'datetime',
        'nbrobj': 'int',
        'nbrobjcum': 'int'
    }

    attribute_map = {
        'id': 'id',
        'parent_id': 'parent_id',
        'name': 'name',
        'id_source': 'id_source',
        'taxotype': 'taxotype',
        'display_name': 'display_name',
        'lastupdate_datetime': 'lastupdate_datetime',
        'id_instance': 'id_instance',
        'taxostatus': 'taxostatus',
        'rename_to': 'rename_to',
        'source_url': 'source_url',
        'source_desc': 'source_desc',
        'creator_email': 'creator_email',
        'creation_datetime': 'creation_datetime',
        'nbrobj': 'nbrobj',
        'nbrobjcum': 'nbrobjcum'
    }

    def __init__(self, id=None, parent_id=None, name=None, id_source=None, taxotype=None, display_name=None, lastupdate_datetime=None, id_instance=None, taxostatus=None, rename_to=None, source_url=None, source_desc=None, creator_email=None, creation_datetime=None, nbrobj=None, nbrobjcum=None, local_vars_configuration=None):  # noqa: E501
        """TaxonCentral - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._parent_id = None
        self._name = None
        self._id_source = None
        self._taxotype = None
        self._display_name = None
        self._lastupdate_datetime = None
        self._id_instance = None
        self._taxostatus = None
        self._rename_to = None
        self._source_url = None
        self._source_desc = None
        self._creator_email = None
        self._creation_datetime = None
        self._nbrobj = None
        self._nbrobjcum = None
        self.discriminator = None

        self.id = id
        if parent_id is not None:
            self.parent_id = parent_id
        self.name = name
        if id_source is not None:
            self.id_source = id_source
        self.taxotype = taxotype
        if display_name is not None:
            self.display_name = display_name
        if lastupdate_datetime is not None:
            self.lastupdate_datetime = lastupdate_datetime
        if id_instance is not None:
            self.id_instance = id_instance
        self.taxostatus = taxostatus
        if rename_to is not None:
            self.rename_to = rename_to
        if source_url is not None:
            self.source_url = source_url
        if source_desc is not None:
            self.source_desc = source_desc
        if creator_email is not None:
            self.creator_email = creator_email
        if creation_datetime is not None:
            self.creation_datetime = creation_datetime
        if nbrobj is not None:
            self.nbrobj = nbrobj
        if nbrobjcum is not None:
            self.nbrobjcum = nbrobjcum

    @property
    def id(self):
        """Gets the id of this TaxonCentral.  # noqa: E501

        The unique numeric id of the taxon.  # noqa: E501

        :return: The id of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TaxonCentral.

        The unique numeric id of the taxon.  # noqa: E501

        :param id: The id of this TaxonCentral.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def parent_id(self):
        """Gets the parent_id of this TaxonCentral.  # noqa: E501

        The unique numeric id of the taxon parent.  # noqa: E501

        :return: The parent_id of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._parent_id

    @parent_id.setter
    def parent_id(self, parent_id):
        """Sets the parent_id of this TaxonCentral.

        The unique numeric id of the taxon parent.  # noqa: E501

        :param parent_id: The parent_id of this TaxonCentral.  # noqa: E501
        :type: int
        """

        self._parent_id = parent_id

    @property
    def name(self):
        """Gets the name of this TaxonCentral.  # noqa: E501

        The name of the taxon.  # noqa: E501

        :return: The name of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this TaxonCentral.

        The name of the taxon.  # noqa: E501

        :param name: The name of this TaxonCentral.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def id_source(self):
        """Gets the id_source of this TaxonCentral.  # noqa: E501

        The source ID.  # noqa: E501

        :return: The id_source of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._id_source

    @id_source.setter
    def id_source(self, id_source):
        """Sets the id_source of this TaxonCentral.

        The source ID.  # noqa: E501

        :param id_source: The id_source of this TaxonCentral.  # noqa: E501
        :type: str
        """

        self._id_source = id_source

    @property
    def taxotype(self):
        """Gets the taxotype of this TaxonCentral.  # noqa: E501

        The taxon type, 'M' for Morpho or 'P' for Phylo.  # noqa: E501

        :return: The taxotype of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._taxotype

    @taxotype.setter
    def taxotype(self, taxotype):
        """Sets the taxotype of this TaxonCentral.

        The taxon type, 'M' for Morpho or 'P' for Phylo.  # noqa: E501

        :param taxotype: The taxotype of this TaxonCentral.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and taxotype is None:  # noqa: E501
            raise ValueError("Invalid value for `taxotype`, must not be `None`")  # noqa: E501

        self._taxotype = taxotype

    @property
    def display_name(self):
        """Gets the display_name of this TaxonCentral.  # noqa: E501

        The display name of the taxon. It is suffixed in EcoTaxoServer with (Deprecated) when taxostatus is 'D'  # noqa: E501

        :return: The display_name of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this TaxonCentral.

        The display name of the taxon. It is suffixed in EcoTaxoServer with (Deprecated) when taxostatus is 'D'  # noqa: E501

        :param display_name: The display_name of this TaxonCentral.  # noqa: E501
        :type: str
        """

        self._display_name = display_name

    @property
    def lastupdate_datetime(self):
        """Gets the lastupdate_datetime of this TaxonCentral.  # noqa: E501

        Taxon last update. Date, with format YYYY-MM-DD hh:mm:ss.  # noqa: E501

        :return: The lastupdate_datetime of this TaxonCentral.  # noqa: E501
        :rtype: datetime
        """
        return self._lastupdate_datetime

    @lastupdate_datetime.setter
    def lastupdate_datetime(self, lastupdate_datetime):
        """Sets the lastupdate_datetime of this TaxonCentral.

        Taxon last update. Date, with format YYYY-MM-DD hh:mm:ss.  # noqa: E501

        :param lastupdate_datetime: The lastupdate_datetime of this TaxonCentral.  # noqa: E501
        :type: datetime
        """

        self._lastupdate_datetime = lastupdate_datetime

    @property
    def id_instance(self):
        """Gets the id_instance of this TaxonCentral.  # noqa: E501

        The instance Id.  # noqa: E501

        :return: The id_instance of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._id_instance

    @id_instance.setter
    def id_instance(self, id_instance):
        """Sets the id_instance of this TaxonCentral.

        The instance Id.  # noqa: E501

        :param id_instance: The id_instance of this TaxonCentral.  # noqa: E501
        :type: int
        """

        self._id_instance = id_instance

    @property
    def taxostatus(self):
        """Gets the taxostatus of this TaxonCentral.  # noqa: E501

        The taxon status, N for Not approved, A for Approved or D for Deprecated.  # noqa: E501

        :return: The taxostatus of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._taxostatus

    @taxostatus.setter
    def taxostatus(self, taxostatus):
        """Sets the taxostatus of this TaxonCentral.

        The taxon status, N for Not approved, A for Approved or D for Deprecated.  # noqa: E501

        :param taxostatus: The taxostatus of this TaxonCentral.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and taxostatus is None:  # noqa: E501
            raise ValueError("Invalid value for `taxostatus`, must not be `None`")  # noqa: E501

        self._taxostatus = taxostatus

    @property
    def rename_to(self):
        """Gets the rename_to of this TaxonCentral.  # noqa: E501

        The advised replacement Name if the taxon is deprecated.  # noqa: E501

        :return: The rename_to of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._rename_to

    @rename_to.setter
    def rename_to(self, rename_to):
        """Sets the rename_to of this TaxonCentral.

        The advised replacement Name if the taxon is deprecated.  # noqa: E501

        :param rename_to: The rename_to of this TaxonCentral.  # noqa: E501
        :type: int
        """

        self._rename_to = rename_to

    @property
    def source_url(self):
        """Gets the source_url of this TaxonCentral.  # noqa: E501

        The source url.  # noqa: E501

        :return: The source_url of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._source_url

    @source_url.setter
    def source_url(self, source_url):
        """Sets the source_url of this TaxonCentral.

        The source url.  # noqa: E501

        :param source_url: The source_url of this TaxonCentral.  # noqa: E501
        :type: str
        """

        self._source_url = source_url

    @property
    def source_desc(self):
        """Gets the source_desc of this TaxonCentral.  # noqa: E501

        The source description.  # noqa: E501

        :return: The source_desc of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._source_desc

    @source_desc.setter
    def source_desc(self, source_desc):
        """Sets the source_desc of this TaxonCentral.

        The source description.  # noqa: E501

        :param source_desc: The source_desc of this TaxonCentral.  # noqa: E501
        :type: str
        """

        self._source_desc = source_desc

    @property
    def creator_email(self):
        """Gets the creator_email of this TaxonCentral.  # noqa: E501

        Email of the creator of the taxon.  # noqa: E501

        :return: The creator_email of this TaxonCentral.  # noqa: E501
        :rtype: str
        """
        return self._creator_email

    @creator_email.setter
    def creator_email(self, creator_email):
        """Sets the creator_email of this TaxonCentral.

        Email of the creator of the taxon.  # noqa: E501

        :param creator_email: The creator_email of this TaxonCentral.  # noqa: E501
        :type: str
        """

        self._creator_email = creator_email

    @property
    def creation_datetime(self):
        """Gets the creation_datetime of this TaxonCentral.  # noqa: E501

        Taxon creation date. Date, with format YYYY-MM-DD hh:mm:ss.  # noqa: E501

        :return: The creation_datetime of this TaxonCentral.  # noqa: E501
        :rtype: datetime
        """
        return self._creation_datetime

    @creation_datetime.setter
    def creation_datetime(self, creation_datetime):
        """Sets the creation_datetime of this TaxonCentral.

        Taxon creation date. Date, with format YYYY-MM-DD hh:mm:ss.  # noqa: E501

        :param creation_datetime: The creation_datetime of this TaxonCentral.  # noqa: E501
        :type: datetime
        """

        self._creation_datetime = creation_datetime

    @property
    def nbrobj(self):
        """Gets the nbrobj of this TaxonCentral.  # noqa: E501

        Number of objects in this category exactly.  # noqa: E501

        :return: The nbrobj of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._nbrobj

    @nbrobj.setter
    def nbrobj(self, nbrobj):
        """Sets the nbrobj of this TaxonCentral.

        Number of objects in this category exactly.  # noqa: E501

        :param nbrobj: The nbrobj of this TaxonCentral.  # noqa: E501
        :type: int
        """

        self._nbrobj = nbrobj

    @property
    def nbrobjcum(self):
        """Gets the nbrobjcum of this TaxonCentral.  # noqa: E501

        Number of objects in this category and descendant ones.  # noqa: E501

        :return: The nbrobjcum of this TaxonCentral.  # noqa: E501
        :rtype: int
        """
        return self._nbrobjcum

    @nbrobjcum.setter
    def nbrobjcum(self, nbrobjcum):
        """Sets the nbrobjcum of this TaxonCentral.

        Number of objects in this category and descendant ones.  # noqa: E501

        :param nbrobjcum: The nbrobjcum of this TaxonCentral.  # noqa: E501
        :type: int
        """

        self._nbrobjcum = nbrobjcum

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
        if not isinstance(other, TaxonCentral):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxonCentral):
            return True

        return self.to_dict() != other.to_dict()
