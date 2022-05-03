# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.28
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class TaxonModel(object):
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
        'renm_id': 'int',
        'name': 'str',
        'type': 'str',
        'nb_objects': 'int',
        'nb_children_objects': 'int',
        'display_name': 'str',
        'lineage': 'list[str]',
        'id_lineage': 'list[int]',
        'children': 'list[int]'
    }

    attribute_map = {
        'id': 'id',
        'renm_id': 'renm_id',
        'name': 'name',
        'type': 'type',
        'nb_objects': 'nb_objects',
        'nb_children_objects': 'nb_children_objects',
        'display_name': 'display_name',
        'lineage': 'lineage',
        'id_lineage': 'id_lineage',
        'children': 'children'
    }

    def __init__(self, id=None, renm_id=None, name=None, type=None, nb_objects=None, nb_children_objects=None, display_name=None, lineage=None, id_lineage=None, children=None, local_vars_configuration=None):  # noqa: E501
        """TaxonModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._renm_id = None
        self._name = None
        self._type = None
        self._nb_objects = None
        self._nb_children_objects = None
        self._display_name = None
        self._lineage = None
        self._id_lineage = None
        self._children = None
        self.discriminator = None

        self.id = id
        if renm_id is not None:
            self.renm_id = renm_id
        self.name = name
        self.type = type
        self.nb_objects = nb_objects
        self.nb_children_objects = nb_children_objects
        self.display_name = display_name
        self.lineage = lineage
        self.id_lineage = id_lineage
        self.children = children

    @property
    def id(self):
        """Gets the id of this TaxonModel.  # noqa: E501

        The taxon/category IDs.  # noqa: E501

        :return: The id of this TaxonModel.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TaxonModel.

        The taxon/category IDs.  # noqa: E501

        :param id: The id of this TaxonModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def renm_id(self):
        """Gets the renm_id of this TaxonModel.  # noqa: E501

        The advised replacement ID if the taxon/category is deprecated.  # noqa: E501

        :return: The renm_id of this TaxonModel.  # noqa: E501
        :rtype: int
        """
        return self._renm_id

    @renm_id.setter
    def renm_id(self, renm_id):
        """Sets the renm_id of this TaxonModel.

        The advised replacement ID if the taxon/category is deprecated.  # noqa: E501

        :param renm_id: The renm_id of this TaxonModel.  # noqa: E501
        :type: int
        """

        self._renm_id = renm_id

    @property
    def name(self):
        """Gets the name of this TaxonModel.  # noqa: E501

        The taxon/category verbatim name.  # noqa: E501

        :return: The name of this TaxonModel.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this TaxonModel.

        The taxon/category verbatim name.  # noqa: E501

        :param name: The name of this TaxonModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def type(self):
        """Gets the type of this TaxonModel.  # noqa: E501

        The taxon/category type, 'M' for Morpho or 'P' for Phylo.  # noqa: E501

        :return: The type of this TaxonModel.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TaxonModel.

        The taxon/category type, 'M' for Morpho or 'P' for Phylo.  # noqa: E501

        :param type: The type of this TaxonModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def nb_objects(self):
        """Gets the nb_objects of this TaxonModel.  # noqa: E501

        How many objects are classified in this category.  # noqa: E501

        :return: The nb_objects of this TaxonModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_objects

    @nb_objects.setter
    def nb_objects(self, nb_objects):
        """Sets the nb_objects of this TaxonModel.

        How many objects are classified in this category.  # noqa: E501

        :param nb_objects: The nb_objects of this TaxonModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and nb_objects is None:  # noqa: E501
            raise ValueError("Invalid value for `nb_objects`, must not be `None`")  # noqa: E501

        self._nb_objects = nb_objects

    @property
    def nb_children_objects(self):
        """Gets the nb_children_objects of this TaxonModel.  # noqa: E501

        How many objects are classified in this category children (not itself).  # noqa: E501

        :return: The nb_children_objects of this TaxonModel.  # noqa: E501
        :rtype: int
        """
        return self._nb_children_objects

    @nb_children_objects.setter
    def nb_children_objects(self, nb_children_objects):
        """Sets the nb_children_objects of this TaxonModel.

        How many objects are classified in this category children (not itself).  # noqa: E501

        :param nb_children_objects: The nb_children_objects of this TaxonModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and nb_children_objects is None:  # noqa: E501
            raise ValueError("Invalid value for `nb_children_objects`, must not be `None`")  # noqa: E501

        self._nb_children_objects = nb_children_objects

    @property
    def display_name(self):
        """Gets the display_name of this TaxonModel.  # noqa: E501

        The taxon/category display name.  # noqa: E501

        :return: The display_name of this TaxonModel.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this TaxonModel.

        The taxon/category display name.  # noqa: E501

        :param display_name: The display_name of this TaxonModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501

        self._display_name = display_name

    @property
    def lineage(self):
        """Gets the lineage of this TaxonModel.  # noqa: E501

        The taxon/category name of ancestors, including self, in first.  # noqa: E501

        :return: The lineage of this TaxonModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._lineage

    @lineage.setter
    def lineage(self, lineage):
        """Sets the lineage of this TaxonModel.

        The taxon/category name of ancestors, including self, in first.  # noqa: E501

        :param lineage: The lineage of this TaxonModel.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and lineage is None:  # noqa: E501
            raise ValueError("Invalid value for `lineage`, must not be `None`")  # noqa: E501

        self._lineage = lineage

    @property
    def id_lineage(self):
        """Gets the id_lineage of this TaxonModel.  # noqa: E501

        The taxon/category IDs of ancestors, including self, in first.  # noqa: E501

        :return: The id_lineage of this TaxonModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._id_lineage

    @id_lineage.setter
    def id_lineage(self, id_lineage):
        """Sets the id_lineage of this TaxonModel.

        The taxon/category IDs of ancestors, including self, in first.  # noqa: E501

        :param id_lineage: The id_lineage of this TaxonModel.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and id_lineage is None:  # noqa: E501
            raise ValueError("Invalid value for `id_lineage`, must not be `None`")  # noqa: E501

        self._id_lineage = id_lineage

    @property
    def children(self):
        """Gets the children of this TaxonModel.  # noqa: E501

        The taxon/category IDs of children.  # noqa: E501

        :return: The children of this TaxonModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._children

    @children.setter
    def children(self, children):
        """Sets the children of this TaxonModel.

        The taxon/category IDs of children.  # noqa: E501

        :param children: The children of this TaxonModel.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and children is None:  # noqa: E501
            raise ValueError("Invalid value for `children`, must not be `None`")  # noqa: E501

        self._children = children

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
        if not isinstance(other, TaxonModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxonModel):
            return True

        return self.to_dict() != other.to_dict()
