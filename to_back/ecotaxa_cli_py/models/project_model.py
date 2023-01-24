# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.30
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ProjectModel(object):
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
        'obj_free_cols': 'dict(str, str)',
        'sample_free_cols': 'dict(str, str)',
        'acquisition_free_cols': 'dict(str, str)',
        'process_free_cols': 'dict(str, str)',
        'bodc_variables': 'dict(str, str)',
        'init_classif_list': 'list[int]',
        'managers': 'list[MinUserModel]',
        'annotators': 'list[MinUserModel]',
        'viewers': 'list[MinUserModel]',
        'instrument': 'str',
        'instrument_url': 'str',
        'contact': 'MinUserModel',
        'highest_right': 'str',
        'license': 'LicenseEnum',
        'projid': 'int',
        'title': 'str',
        'visible': 'bool',
        'status': 'str',
        'objcount': 'float',
        'pctvalidated': 'float',
        'pctclassified': 'float',
        'classifsettings': 'str',
        'classiffieldlist': 'str',
        'popoverfieldlist': 'str',
        'comments': 'str',
        'description': 'str',
        'rf_models_used': 'str',
        'cnn_network_id': 'str'
    }

    attribute_map = {
        'obj_free_cols': 'obj_free_cols',
        'sample_free_cols': 'sample_free_cols',
        'acquisition_free_cols': 'acquisition_free_cols',
        'process_free_cols': 'process_free_cols',
        'bodc_variables': 'bodc_variables',
        'init_classif_list': 'init_classif_list',
        'managers': 'managers',
        'annotators': 'annotators',
        'viewers': 'viewers',
        'instrument': 'instrument',
        'instrument_url': 'instrument_url',
        'contact': 'contact',
        'highest_right': 'highest_right',
        'license': 'license',
        'projid': 'projid',
        'title': 'title',
        'visible': 'visible',
        'status': 'status',
        'objcount': 'objcount',
        'pctvalidated': 'pctvalidated',
        'pctclassified': 'pctclassified',
        'classifsettings': 'classifsettings',
        'classiffieldlist': 'classiffieldlist',
        'popoverfieldlist': 'popoverfieldlist',
        'comments': 'comments',
        'description': 'description',
        'rf_models_used': 'rf_models_used',
        'cnn_network_id': 'cnn_network_id'
    }

    def __init__(self, obj_free_cols=None, sample_free_cols=None, acquisition_free_cols=None, process_free_cols=None, bodc_variables=None, init_classif_list=[], managers=[], annotators=[], viewers=[], instrument=None, instrument_url=None, contact=None, highest_right='', license=None, projid=None, title=None, visible=None, status=None, objcount=None, pctvalidated=None, pctclassified=None, classifsettings=None, classiffieldlist=None, popoverfieldlist=None, comments=None, description=None, rf_models_used=None, cnn_network_id=None, local_vars_configuration=None):  # noqa: E501
        """ProjectModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._obj_free_cols = None
        self._sample_free_cols = None
        self._acquisition_free_cols = None
        self._process_free_cols = None
        self._bodc_variables = None
        self._init_classif_list = None
        self._managers = None
        self._annotators = None
        self._viewers = None
        self._instrument = None
        self._instrument_url = None
        self._contact = None
        self._highest_right = None
        self._license = None
        self._projid = None
        self._title = None
        self._visible = None
        self._status = None
        self._objcount = None
        self._pctvalidated = None
        self._pctclassified = None
        self._classifsettings = None
        self._classiffieldlist = None
        self._popoverfieldlist = None
        self._comments = None
        self._description = None
        self._rf_models_used = None
        self._cnn_network_id = None
        self.discriminator = None

        if obj_free_cols is not None:
            self.obj_free_cols = obj_free_cols
        if sample_free_cols is not None:
            self.sample_free_cols = sample_free_cols
        if acquisition_free_cols is not None:
            self.acquisition_free_cols = acquisition_free_cols
        if process_free_cols is not None:
            self.process_free_cols = process_free_cols
        if bodc_variables is not None:
            self.bodc_variables = bodc_variables
        if init_classif_list is not None:
            self.init_classif_list = init_classif_list
        if managers is not None:
            self.managers = managers
        if annotators is not None:
            self.annotators = annotators
        if viewers is not None:
            self.viewers = viewers
        if instrument is not None:
            self.instrument = instrument
        if instrument_url is not None:
            self.instrument_url = instrument_url
        if contact is not None:
            self.contact = contact
        if highest_right is not None:
            self.highest_right = highest_right
        if license is not None:
            self.license = license
        self.projid = projid
        self.title = title
        if visible is not None:
            self.visible = visible
        if status is not None:
            self.status = status
        if objcount is not None:
            self.objcount = objcount
        if pctvalidated is not None:
            self.pctvalidated = pctvalidated
        if pctclassified is not None:
            self.pctclassified = pctclassified
        if classifsettings is not None:
            self.classifsettings = classifsettings
        if classiffieldlist is not None:
            self.classiffieldlist = classiffieldlist
        if popoverfieldlist is not None:
            self.popoverfieldlist = popoverfieldlist
        if comments is not None:
            self.comments = comments
        if description is not None:
            self.description = description
        if rf_models_used is not None:
            self.rf_models_used = rf_models_used
        if cnn_network_id is not None:
            self.cnn_network_id = cnn_network_id

    @property
    def obj_free_cols(self):
        """Gets the obj_free_cols of this ProjectModel.  # noqa: E501

        Object free columns.  # noqa: E501

        :return: The obj_free_cols of this ProjectModel.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._obj_free_cols

    @obj_free_cols.setter
    def obj_free_cols(self, obj_free_cols):
        """Sets the obj_free_cols of this ProjectModel.

        Object free columns.  # noqa: E501

        :param obj_free_cols: The obj_free_cols of this ProjectModel.  # noqa: E501
        :type: dict(str, str)
        """

        self._obj_free_cols = obj_free_cols

    @property
    def sample_free_cols(self):
        """Gets the sample_free_cols of this ProjectModel.  # noqa: E501

        Sample free columns.  # noqa: E501

        :return: The sample_free_cols of this ProjectModel.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._sample_free_cols

    @sample_free_cols.setter
    def sample_free_cols(self, sample_free_cols):
        """Sets the sample_free_cols of this ProjectModel.

        Sample free columns.  # noqa: E501

        :param sample_free_cols: The sample_free_cols of this ProjectModel.  # noqa: E501
        :type: dict(str, str)
        """

        self._sample_free_cols = sample_free_cols

    @property
    def acquisition_free_cols(self):
        """Gets the acquisition_free_cols of this ProjectModel.  # noqa: E501

        Acquisition free columns.  # noqa: E501

        :return: The acquisition_free_cols of this ProjectModel.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._acquisition_free_cols

    @acquisition_free_cols.setter
    def acquisition_free_cols(self, acquisition_free_cols):
        """Sets the acquisition_free_cols of this ProjectModel.

        Acquisition free columns.  # noqa: E501

        :param acquisition_free_cols: The acquisition_free_cols of this ProjectModel.  # noqa: E501
        :type: dict(str, str)
        """

        self._acquisition_free_cols = acquisition_free_cols

    @property
    def process_free_cols(self):
        """Gets the process_free_cols of this ProjectModel.  # noqa: E501

        Process free columns.  # noqa: E501

        :return: The process_free_cols of this ProjectModel.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._process_free_cols

    @process_free_cols.setter
    def process_free_cols(self, process_free_cols):
        """Sets the process_free_cols of this ProjectModel.

        Process free columns.  # noqa: E501

        :param process_free_cols: The process_free_cols of this ProjectModel.  # noqa: E501
        :type: dict(str, str)
        """

        self._process_free_cols = process_free_cols

    @property
    def bodc_variables(self):
        """Gets the bodc_variables of this ProjectModel.  # noqa: E501

        BODC quantities from columns. Only the 3 keys listed in example are valid.  # noqa: E501

        :return: The bodc_variables of this ProjectModel.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._bodc_variables

    @bodc_variables.setter
    def bodc_variables(self, bodc_variables):
        """Sets the bodc_variables of this ProjectModel.

        BODC quantities from columns. Only the 3 keys listed in example are valid.  # noqa: E501

        :param bodc_variables: The bodc_variables of this ProjectModel.  # noqa: E501
        :type: dict(str, str)
        """

        self._bodc_variables = bodc_variables

    @property
    def init_classif_list(self):
        """Gets the init_classif_list of this ProjectModel.  # noqa: E501

        Favorite taxa used in classification.  # noqa: E501

        :return: The init_classif_list of this ProjectModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._init_classif_list

    @init_classif_list.setter
    def init_classif_list(self, init_classif_list):
        """Sets the init_classif_list of this ProjectModel.

        Favorite taxa used in classification.  # noqa: E501

        :param init_classif_list: The init_classif_list of this ProjectModel.  # noqa: E501
        :type: list[int]
        """

        self._init_classif_list = init_classif_list

    @property
    def managers(self):
        """Gets the managers of this ProjectModel.  # noqa: E501

        Managers of this project.  # noqa: E501

        :return: The managers of this ProjectModel.  # noqa: E501
        :rtype: list[MinUserModel]
        """
        return self._managers

    @managers.setter
    def managers(self, managers):
        """Sets the managers of this ProjectModel.

        Managers of this project.  # noqa: E501

        :param managers: The managers of this ProjectModel.  # noqa: E501
        :type: list[MinUserModel]
        """

        self._managers = managers

    @property
    def annotators(self):
        """Gets the annotators of this ProjectModel.  # noqa: E501

        Annotators of this project, if not manager.  # noqa: E501

        :return: The annotators of this ProjectModel.  # noqa: E501
        :rtype: list[MinUserModel]
        """
        return self._annotators

    @annotators.setter
    def annotators(self, annotators):
        """Sets the annotators of this ProjectModel.

        Annotators of this project, if not manager.  # noqa: E501

        :param annotators: The annotators of this ProjectModel.  # noqa: E501
        :type: list[MinUserModel]
        """

        self._annotators = annotators

    @property
    def viewers(self):
        """Gets the viewers of this ProjectModel.  # noqa: E501

        Viewers of this project, if not manager nor annotator.  # noqa: E501

        :return: The viewers of this ProjectModel.  # noqa: E501
        :rtype: list[MinUserModel]
        """
        return self._viewers

    @viewers.setter
    def viewers(self, viewers):
        """Sets the viewers of this ProjectModel.

        Viewers of this project, if not manager nor annotator.  # noqa: E501

        :param viewers: The viewers of this ProjectModel.  # noqa: E501
        :type: list[MinUserModel]
        """

        self._viewers = viewers

    @property
    def instrument(self):
        """Gets the instrument of this ProjectModel.  # noqa: E501

        This project's instrument code.  # noqa: E501

        :return: The instrument of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        """Sets the instrument of this ProjectModel.

        This project's instrument code.  # noqa: E501

        :param instrument: The instrument of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._instrument = instrument

    @property
    def instrument_url(self):
        """Gets the instrument_url of this ProjectModel.  # noqa: E501

        This project's instrument BODC definition.  # noqa: E501

        :return: The instrument_url of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._instrument_url

    @instrument_url.setter
    def instrument_url(self, instrument_url):
        """Sets the instrument_url of this ProjectModel.

        This project's instrument BODC definition.  # noqa: E501

        :param instrument_url: The instrument_url of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._instrument_url = instrument_url

    @property
    def contact(self):
        """Gets the contact of this ProjectModel.  # noqa: E501

        The contact person is a manager who serves as the contact person for other users and EcoTaxa's managers.  # noqa: E501

        :return: The contact of this ProjectModel.  # noqa: E501
        :rtype: MinUserModel
        """
        return self._contact

    @contact.setter
    def contact(self, contact):
        """Sets the contact of this ProjectModel.

        The contact person is a manager who serves as the contact person for other users and EcoTaxa's managers.  # noqa: E501

        :param contact: The contact of this ProjectModel.  # noqa: E501
        :type: MinUserModel
        """

        self._contact = contact

    @property
    def highest_right(self):
        """Gets the highest_right of this ProjectModel.  # noqa: E501

        The highest right for requester on this project. One of 'Manage', 'Annotate', 'View'.  # noqa: E501

        :return: The highest_right of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._highest_right

    @highest_right.setter
    def highest_right(self, highest_right):
        """Sets the highest_right of this ProjectModel.

        The highest right for requester on this project. One of 'Manage', 'Annotate', 'View'.  # noqa: E501

        :param highest_right: The highest_right of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._highest_right = highest_right

    @property
    def license(self):
        """Gets the license of this ProjectModel.  # noqa: E501

        Data licence.  # noqa: E501

        :return: The license of this ProjectModel.  # noqa: E501
        :rtype: LicenseEnum
        """
        return self._license

    @license.setter
    def license(self, license):
        """Sets the license of this ProjectModel.

        Data licence.  # noqa: E501

        :param license: The license of this ProjectModel.  # noqa: E501
        :type: LicenseEnum
        """

        self._license = license

    @property
    def projid(self):
        """Gets the projid of this ProjectModel.  # noqa: E501

        The project Id.  # noqa: E501

        :return: The projid of this ProjectModel.  # noqa: E501
        :rtype: int
        """
        return self._projid

    @projid.setter
    def projid(self, projid):
        """Sets the projid of this ProjectModel.

        The project Id.  # noqa: E501

        :param projid: The projid of this ProjectModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and projid is None:  # noqa: E501
            raise ValueError("Invalid value for `projid`, must not be `None`")  # noqa: E501

        self._projid = projid

    @property
    def title(self):
        """Gets the title of this ProjectModel.  # noqa: E501

        The project title.  # noqa: E501

        :return: The title of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this ProjectModel.

        The project title.  # noqa: E501

        :param title: The title of this ProjectModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and title is None:  # noqa: E501
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def visible(self):
        """Gets the visible of this ProjectModel.  # noqa: E501

        The project visibility.  # noqa: E501

        :return: The visible of this ProjectModel.  # noqa: E501
        :rtype: bool
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        """Sets the visible of this ProjectModel.

        The project visibility.  # noqa: E501

        :param visible: The visible of this ProjectModel.  # noqa: E501
        :type: bool
        """

        self._visible = visible

    @property
    def status(self):
        """Gets the status of this ProjectModel.  # noqa: E501

        The project status.  # noqa: E501

        :return: The status of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ProjectModel.

        The project status.  # noqa: E501

        :param status: The status of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def objcount(self):
        """Gets the objcount of this ProjectModel.  # noqa: E501

        The number of objects.  # noqa: E501

        :return: The objcount of this ProjectModel.  # noqa: E501
        :rtype: float
        """
        return self._objcount

    @objcount.setter
    def objcount(self, objcount):
        """Sets the objcount of this ProjectModel.

        The number of objects.  # noqa: E501

        :param objcount: The objcount of this ProjectModel.  # noqa: E501
        :type: float
        """

        self._objcount = objcount

    @property
    def pctvalidated(self):
        """Gets the pctvalidated of this ProjectModel.  # noqa: E501

        Percentage of validated images.  # noqa: E501

        :return: The pctvalidated of this ProjectModel.  # noqa: E501
        :rtype: float
        """
        return self._pctvalidated

    @pctvalidated.setter
    def pctvalidated(self, pctvalidated):
        """Sets the pctvalidated of this ProjectModel.

        Percentage of validated images.  # noqa: E501

        :param pctvalidated: The pctvalidated of this ProjectModel.  # noqa: E501
        :type: float
        """

        self._pctvalidated = pctvalidated

    @property
    def pctclassified(self):
        """Gets the pctclassified of this ProjectModel.  # noqa: E501

        Percentage of classified images.  # noqa: E501

        :return: The pctclassified of this ProjectModel.  # noqa: E501
        :rtype: float
        """
        return self._pctclassified

    @pctclassified.setter
    def pctclassified(self, pctclassified):
        """Sets the pctclassified of this ProjectModel.

        Percentage of classified images.  # noqa: E501

        :param pctclassified: The pctclassified of this ProjectModel.  # noqa: E501
        :type: float
        """

        self._pctclassified = pctclassified

    @property
    def classifsettings(self):
        """Gets the classifsettings of this ProjectModel.  # noqa: E501


        :return: The classifsettings of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._classifsettings

    @classifsettings.setter
    def classifsettings(self, classifsettings):
        """Sets the classifsettings of this ProjectModel.


        :param classifsettings: The classifsettings of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._classifsettings = classifsettings

    @property
    def classiffieldlist(self):
        """Gets the classiffieldlist of this ProjectModel.  # noqa: E501


        :return: The classiffieldlist of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._classiffieldlist

    @classiffieldlist.setter
    def classiffieldlist(self, classiffieldlist):
        """Sets the classiffieldlist of this ProjectModel.


        :param classiffieldlist: The classiffieldlist of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._classiffieldlist = classiffieldlist

    @property
    def popoverfieldlist(self):
        """Gets the popoverfieldlist of this ProjectModel.  # noqa: E501


        :return: The popoverfieldlist of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._popoverfieldlist

    @popoverfieldlist.setter
    def popoverfieldlist(self, popoverfieldlist):
        """Sets the popoverfieldlist of this ProjectModel.


        :param popoverfieldlist: The popoverfieldlist of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._popoverfieldlist = popoverfieldlist

    @property
    def comments(self):
        """Gets the comments of this ProjectModel.  # noqa: E501

        The project comments.  # noqa: E501

        :return: The comments of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        """Sets the comments of this ProjectModel.

        The project comments.  # noqa: E501

        :param comments: The comments of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._comments = comments

    @property
    def description(self):
        """Gets the description of this ProjectModel.  # noqa: E501

        The project description, i.e. main traits.  # noqa: E501

        :return: The description of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ProjectModel.

        The project description, i.e. main traits.  # noqa: E501

        :param description: The description of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def rf_models_used(self):
        """Gets the rf_models_used of this ProjectModel.  # noqa: E501


        :return: The rf_models_used of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._rf_models_used

    @rf_models_used.setter
    def rf_models_used(self, rf_models_used):
        """Sets the rf_models_used of this ProjectModel.


        :param rf_models_used: The rf_models_used of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._rf_models_used = rf_models_used

    @property
    def cnn_network_id(self):
        """Gets the cnn_network_id of this ProjectModel.  # noqa: E501


        :return: The cnn_network_id of this ProjectModel.  # noqa: E501
        :rtype: str
        """
        return self._cnn_network_id

    @cnn_network_id.setter
    def cnn_network_id(self, cnn_network_id):
        """Sets the cnn_network_id of this ProjectModel.


        :param cnn_network_id: The cnn_network_id of this ProjectModel.  # noqa: E501
        :type: str
        """

        self._cnn_network_id = cnn_network_id

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
        if not isinstance(other, ProjectModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectModel):
            return True

        return self.to_dict() != other.to_dict()
