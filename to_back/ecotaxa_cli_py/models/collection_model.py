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


class CollectionModel(object):
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
        'external_id': 'str',
        'external_id_system': 'str',
        'title': 'str',
        'short_title': 'str',
        'citation': 'str',
        'license': 'str',
        'abstract': 'str',
        'description': 'str',
        'project_ids': 'list[int]',
        'provider_user': 'MinUserModel',
        'contact_user': 'MinUserModel',
        'creator_users': 'list[MinUserModel]',
        'creator_organisations': 'list[str]',
        'associate_users': 'list[MinUserModel]',
        'associate_organisations': 'list[str]'
    }

    attribute_map = {
        'id': 'id',
        'external_id': 'external_id',
        'external_id_system': 'external_id_system',
        'title': 'title',
        'short_title': 'short_title',
        'citation': 'citation',
        'license': 'license',
        'abstract': 'abstract',
        'description': 'description',
        'project_ids': 'project_ids',
        'provider_user': 'provider_user',
        'contact_user': 'contact_user',
        'creator_users': 'creator_users',
        'creator_organisations': 'creator_organisations',
        'associate_users': 'associate_users',
        'associate_organisations': 'associate_organisations'
    }

    def __init__(self, id=None, external_id=None, external_id_system=None, title=None, short_title=None, citation=None, license=None, abstract=None, description=None, project_ids=None, provider_user=None, contact_user=None, creator_users=[], creator_organisations=[], associate_users=[], associate_organisations=[], local_vars_configuration=None):  # noqa: E501
        """CollectionModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._external_id = None
        self._external_id_system = None
        self._title = None
        self._short_title = None
        self._citation = None
        self._license = None
        self._abstract = None
        self._description = None
        self._project_ids = None
        self._provider_user = None
        self._contact_user = None
        self._creator_users = None
        self._creator_organisations = None
        self._associate_users = None
        self._associate_organisations = None
        self.discriminator = None

        self.id = id
        self.external_id = external_id
        self.external_id_system = external_id_system
        self.title = title
        if short_title is not None:
            self.short_title = short_title
        if citation is not None:
            self.citation = citation
        if license is not None:
            self.license = license
        if abstract is not None:
            self.abstract = abstract
        if description is not None:
            self.description = description
        self.project_ids = project_ids
        if provider_user is not None:
            self.provider_user = provider_user
        if contact_user is not None:
            self.contact_user = contact_user
        if creator_users is not None:
            self.creator_users = creator_users
        if creator_organisations is not None:
            self.creator_organisations = creator_organisations
        if associate_users is not None:
            self.associate_users = associate_users
        if associate_organisations is not None:
            self.associate_organisations = associate_organisations

    @property
    def id(self):
        """Gets the id of this CollectionModel.  # noqa: E501

        The collection Id.  # noqa: E501

        :return: The id of this CollectionModel.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this CollectionModel.

        The collection Id.  # noqa: E501

        :param id: The id of this CollectionModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def external_id(self):
        """Gets the external_id of this CollectionModel.  # noqa: E501

        The external Id.  # noqa: E501

        :return: The external_id of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._external_id

    @external_id.setter
    def external_id(self, external_id):
        """Sets the external_id of this CollectionModel.

        The external Id.  # noqa: E501

        :param external_id: The external_id of this CollectionModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and external_id is None:  # noqa: E501
            raise ValueError("Invalid value for `external_id`, must not be `None`")  # noqa: E501

        self._external_id = external_id

    @property
    def external_id_system(self):
        """Gets the external_id_system of this CollectionModel.  # noqa: E501

        The external Id system.  # noqa: E501

        :return: The external_id_system of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._external_id_system

    @external_id_system.setter
    def external_id_system(self, external_id_system):
        """Sets the external_id_system of this CollectionModel.

        The external Id system.  # noqa: E501

        :param external_id_system: The external_id_system of this CollectionModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and external_id_system is None:  # noqa: E501
            raise ValueError("Invalid value for `external_id_system`, must not be `None`")  # noqa: E501

        self._external_id_system = external_id_system

    @property
    def title(self):
        """Gets the title of this CollectionModel.  # noqa: E501

        The collection title.  # noqa: E501

        :return: The title of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this CollectionModel.

        The collection title.  # noqa: E501

        :param title: The title of this CollectionModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and title is None:  # noqa: E501
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def short_title(self):
        """Gets the short_title of this CollectionModel.  # noqa: E501

        The collection short title.  # noqa: E501

        :return: The short_title of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._short_title

    @short_title.setter
    def short_title(self, short_title):
        """Sets the short_title of this CollectionModel.

        The collection short title.  # noqa: E501

        :param short_title: The short_title of this CollectionModel.  # noqa: E501
        :type: str
        """

        self._short_title = short_title

    @property
    def citation(self):
        """Gets the citation of this CollectionModel.  # noqa: E501

        The collection citation.  # noqa: E501

        :return: The citation of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._citation

    @citation.setter
    def citation(self, citation):
        """Sets the citation of this CollectionModel.

        The collection citation.  # noqa: E501

        :param citation: The citation of this CollectionModel.  # noqa: E501
        :type: str
        """

        self._citation = citation

    @property
    def license(self):
        """Gets the license of this CollectionModel.  # noqa: E501

        The collection license.  # noqa: E501

        :return: The license of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._license

    @license.setter
    def license(self, license):
        """Sets the license of this CollectionModel.

        The collection license.  # noqa: E501

        :param license: The license of this CollectionModel.  # noqa: E501
        :type: str
        """

        self._license = license

    @property
    def abstract(self):
        """Gets the abstract of this CollectionModel.  # noqa: E501

        The collection abstract.  # noqa: E501

        :return: The abstract of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._abstract

    @abstract.setter
    def abstract(self, abstract):
        """Sets the abstract of this CollectionModel.

        The collection abstract.  # noqa: E501

        :param abstract: The abstract of this CollectionModel.  # noqa: E501
        :type: str
        """

        self._abstract = abstract

    @property
    def description(self):
        """Gets the description of this CollectionModel.  # noqa: E501

        The collection description.  # noqa: E501

        :return: The description of this CollectionModel.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CollectionModel.

        The collection description.  # noqa: E501

        :param description: The description of this CollectionModel.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def project_ids(self):
        """Gets the project_ids of this CollectionModel.  # noqa: E501

        The list of composing project IDs.  # noqa: E501

        :return: The project_ids of this CollectionModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._project_ids

    @project_ids.setter
    def project_ids(self, project_ids):
        """Sets the project_ids of this CollectionModel.

        The list of composing project IDs.  # noqa: E501

        :param project_ids: The project_ids of this CollectionModel.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and project_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `project_ids`, must not be `None`")  # noqa: E501

        self._project_ids = project_ids

    @property
    def provider_user(self):
        """Gets the provider_user of this CollectionModel.  # noqa: E501

        Is the person who         is responsible for the content of this metadata record. Writer of the title and abstract.  # noqa: E501

        :return: The provider_user of this CollectionModel.  # noqa: E501
        :rtype: MinUserModel
        """
        return self._provider_user

    @provider_user.setter
    def provider_user(self, provider_user):
        """Sets the provider_user of this CollectionModel.

        Is the person who         is responsible for the content of this metadata record. Writer of the title and abstract.  # noqa: E501

        :param provider_user: The provider_user of this CollectionModel.  # noqa: E501
        :type: MinUserModel
        """

        self._provider_user = provider_user

    @property
    def contact_user(self):
        """Gets the contact_user of this CollectionModel.  # noqa: E501

        Is the person who         should be contacted in cases of questions regarding the content of the dataset or any data restrictions.         This is also the person who is most likely to stay involved in the dataset the longest.  # noqa: E501

        :return: The contact_user of this CollectionModel.  # noqa: E501
        :rtype: MinUserModel
        """
        return self._contact_user

    @contact_user.setter
    def contact_user(self, contact_user):
        """Sets the contact_user of this CollectionModel.

        Is the person who         should be contacted in cases of questions regarding the content of the dataset or any data restrictions.         This is also the person who is most likely to stay involved in the dataset the longest.  # noqa: E501

        :param contact_user: The contact_user of this CollectionModel.  # noqa: E501
        :type: MinUserModel
        """

        self._contact_user = contact_user

    @property
    def creator_users(self):
        """Gets the creator_users of this CollectionModel.  # noqa: E501

        All people who         are responsible for the creation of the collection. Data creators should receive credit         for their work and should therefore be included in the citation.  # noqa: E501

        :return: The creator_users of this CollectionModel.  # noqa: E501
        :rtype: list[MinUserModel]
        """
        return self._creator_users

    @creator_users.setter
    def creator_users(self, creator_users):
        """Sets the creator_users of this CollectionModel.

        All people who         are responsible for the creation of the collection. Data creators should receive credit         for their work and should therefore be included in the citation.  # noqa: E501

        :param creator_users: The creator_users of this CollectionModel.  # noqa: E501
        :type: list[MinUserModel]
        """

        self._creator_users = creator_users

    @property
    def creator_organisations(self):
        """Gets the creator_organisations of this CollectionModel.  # noqa: E501

        All         organisations who are responsible for the creation of the collection. Data creators should         receive credit for their work and should therefore be included in the citation.  # noqa: E501

        :return: The creator_organisations of this CollectionModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._creator_organisations

    @creator_organisations.setter
    def creator_organisations(self, creator_organisations):
        """Sets the creator_organisations of this CollectionModel.

        All         organisations who are responsible for the creation of the collection. Data creators should         receive credit for their work and should therefore be included in the citation.  # noqa: E501

        :param creator_organisations: The creator_organisations of this CollectionModel.  # noqa: E501
        :type: list[str]
        """

        self._creator_organisations = creator_organisations

    @property
    def associate_users(self):
        """Gets the associate_users of this CollectionModel.  # noqa: E501

        Other person(s)         associated with the collection.  # noqa: E501

        :return: The associate_users of this CollectionModel.  # noqa: E501
        :rtype: list[MinUserModel]
        """
        return self._associate_users

    @associate_users.setter
    def associate_users(self, associate_users):
        """Sets the associate_users of this CollectionModel.

        Other person(s)         associated with the collection.  # noqa: E501

        :param associate_users: The associate_users of this CollectionModel.  # noqa: E501
        :type: list[MinUserModel]
        """

        self._associate_users = associate_users

    @property
    def associate_organisations(self):
        """Gets the associate_organisations of this CollectionModel.  # noqa: E501

        Other         organisation(s) associated with the collection.  # noqa: E501

        :return: The associate_organisations of this CollectionModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._associate_organisations

    @associate_organisations.setter
    def associate_organisations(self, associate_organisations):
        """Sets the associate_organisations of this CollectionModel.

        Other         organisation(s) associated with the collection.  # noqa: E501

        :param associate_organisations: The associate_organisations of this CollectionModel.  # noqa: E501
        :type: list[str]
        """

        self._associate_organisations = associate_organisations

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
        if not isinstance(other, CollectionModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CollectionModel):
            return True

        return self.to_dict() != other.to_dict()
