# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.27
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class JobModel(object):
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
        'params': 'object',
        'result': 'object',
        'errors': 'list[str]',
        'question': 'object',
        'reply': 'object',
        'inside': 'object',
        'id': 'int',
        'owner_id': 'int',
        'type': 'str',
        'state': 'str',
        'step': 'int',
        'progress_pct': 'int',
        'progress_msg': 'str',
        'creation_date': 'datetime',
        'updated_on': 'datetime'
    }

    attribute_map = {
        'params': 'params',
        'result': 'result',
        'errors': 'errors',
        'question': 'question',
        'reply': 'reply',
        'inside': 'inside',
        'id': 'id',
        'owner_id': 'owner_id',
        'type': 'type',
        'state': 'state',
        'step': 'step',
        'progress_pct': 'progress_pct',
        'progress_msg': 'progress_msg',
        'creation_date': 'creation_date',
        'updated_on': 'updated_on'
    }

    def __init__(self, params=None, result=None, errors=[], question=None, reply=None, inside=None, id=None, owner_id=None, type=None, state=None, step=None, progress_pct=None, progress_msg=None, creation_date=None, updated_on=None, local_vars_configuration=None):  # noqa: E501
        """JobModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._params = None
        self._result = None
        self._errors = None
        self._question = None
        self._reply = None
        self._inside = None
        self._id = None
        self._owner_id = None
        self._type = None
        self._state = None
        self._step = None
        self._progress_pct = None
        self._progress_msg = None
        self._creation_date = None
        self._updated_on = None
        self.discriminator = None

        if params is not None:
            self.params = params
        if result is not None:
            self.result = result
        if errors is not None:
            self.errors = errors
        if question is not None:
            self.question = question
        if reply is not None:
            self.reply = reply
        if inside is not None:
            self.inside = inside
        self.id = id
        self.owner_id = owner_id
        self.type = type
        if state is not None:
            self.state = state
        if step is not None:
            self.step = step
        if progress_pct is not None:
            self.progress_pct = progress_pct
        if progress_msg is not None:
            self.progress_msg = progress_msg
        self.creation_date = creation_date
        self.updated_on = updated_on

    @property
    def params(self):
        """Gets the params of this JobModel.  # noqa: E501

        Creation parameters.  # noqa: E501

        :return: The params of this JobModel.  # noqa: E501
        :rtype: object
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this JobModel.

        Creation parameters.  # noqa: E501

        :param params: The params of this JobModel.  # noqa: E501
        :type: object
        """

        self._params = params

    @property
    def result(self):
        """Gets the result of this JobModel.  # noqa: E501

        Final result of the run.  # noqa: E501

        :return: The result of this JobModel.  # noqa: E501
        :rtype: object
        """
        return self._result

    @result.setter
    def result(self, result):
        """Sets the result of this JobModel.

        Final result of the run.  # noqa: E501

        :param result: The result of this JobModel.  # noqa: E501
        :type: object
        """

        self._result = result

    @property
    def errors(self):
        """Gets the errors of this JobModel.  # noqa: E501

        The errors seen during last step.  # noqa: E501

        :return: The errors of this JobModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this JobModel.

        The errors seen during last step.  # noqa: E501

        :param errors: The errors of this JobModel.  # noqa: E501
        :type: list[str]
        """

        self._errors = errors

    @property
    def question(self):
        """Gets the question of this JobModel.  # noqa: E501

        The data provoking job move to Asking state.  # noqa: E501

        :return: The question of this JobModel.  # noqa: E501
        :rtype: object
        """
        return self._question

    @question.setter
    def question(self, question):
        """Sets the question of this JobModel.

        The data provoking job move to Asking state.  # noqa: E501

        :param question: The question of this JobModel.  # noqa: E501
        :type: object
        """

        self._question = question

    @property
    def reply(self):
        """Gets the reply of this JobModel.  # noqa: E501

        The data provided as a reply to the question.  # noqa: E501

        :return: The reply of this JobModel.  # noqa: E501
        :rtype: object
        """
        return self._reply

    @reply.setter
    def reply(self, reply):
        """Sets the reply of this JobModel.

        The data provided as a reply to the question.  # noqa: E501

        :param reply: The reply of this JobModel.  # noqa: E501
        :type: object
        """

        self._reply = reply

    @property
    def inside(self):
        """Gets the inside of this JobModel.  # noqa: E501

        Internal state of the job.  # noqa: E501

        :return: The inside of this JobModel.  # noqa: E501
        :rtype: object
        """
        return self._inside

    @inside.setter
    def inside(self, inside):
        """Sets the inside of this JobModel.

        Internal state of the job.  # noqa: E501

        :param inside: The inside of this JobModel.  # noqa: E501
        :type: object
        """

        self._inside = inside

    @property
    def id(self):
        """Gets the id of this JobModel.  # noqa: E501

        Job unique identifier.  # noqa: E501

        :return: The id of this JobModel.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this JobModel.

        Job unique identifier.  # noqa: E501

        :param id: The id of this JobModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def owner_id(self):
        """Gets the owner_id of this JobModel.  # noqa: E501

        The user who created and thus owns the job.   # noqa: E501

        :return: The owner_id of this JobModel.  # noqa: E501
        :rtype: int
        """
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        """Sets the owner_id of this JobModel.

        The user who created and thus owns the job.   # noqa: E501

        :param owner_id: The owner_id of this JobModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and owner_id is None:  # noqa: E501
            raise ValueError("Invalid value for `owner_id`, must not be `None`")  # noqa: E501

        self._owner_id = owner_id

    @property
    def type(self):
        """Gets the type of this JobModel.  # noqa: E501

        The job type, e.g. import, export...   # noqa: E501

        :return: The type of this JobModel.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this JobModel.

        The job type, e.g. import, export...   # noqa: E501

        :param type: The type of this JobModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def state(self):
        """Gets the state of this JobModel.  # noqa: E501

        What the job is doing. Could be 'P' for Pending (Waiting for an execution thread), 'R' for Running (Being executed inside a thread), 'A' for Asking (Needing user information before resuming), 'E' for Error (Stopped with error), 'F' for Finished (Done).  # noqa: E501

        :return: The state of this JobModel.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this JobModel.

        What the job is doing. Could be 'P' for Pending (Waiting for an execution thread), 'R' for Running (Being executed inside a thread), 'A' for Asking (Needing user information before resuming), 'E' for Error (Stopped with error), 'F' for Finished (Done).  # noqa: E501

        :param state: The state of this JobModel.  # noqa: E501
        :type: str
        """

        self._state = state

    @property
    def step(self):
        """Gets the step of this JobModel.  # noqa: E501

        Where in the workflow the job is.   # noqa: E501

        :return: The step of this JobModel.  # noqa: E501
        :rtype: int
        """
        return self._step

    @step.setter
    def step(self, step):
        """Sets the step of this JobModel.

        Where in the workflow the job is.   # noqa: E501

        :param step: The step of this JobModel.  # noqa: E501
        :type: int
        """

        self._step = step

    @property
    def progress_pct(self):
        """Gets the progress_pct of this JobModel.  # noqa: E501

        The progress percentage for UI.   # noqa: E501

        :return: The progress_pct of this JobModel.  # noqa: E501
        :rtype: int
        """
        return self._progress_pct

    @progress_pct.setter
    def progress_pct(self, progress_pct):
        """Sets the progress_pct of this JobModel.

        The progress percentage for UI.   # noqa: E501

        :param progress_pct: The progress_pct of this JobModel.  # noqa: E501
        :type: int
        """

        self._progress_pct = progress_pct

    @property
    def progress_msg(self):
        """Gets the progress_msg of this JobModel.  # noqa: E501

        The message for UI, short version.   # noqa: E501

        :return: The progress_msg of this JobModel.  # noqa: E501
        :rtype: str
        """
        return self._progress_msg

    @progress_msg.setter
    def progress_msg(self, progress_msg):
        """Sets the progress_msg of this JobModel.

        The message for UI, short version.   # noqa: E501

        :param progress_msg: The progress_msg of this JobModel.  # noqa: E501
        :type: str
        """

        self._progress_msg = progress_msg

    @property
    def creation_date(self):
        """Gets the creation_date of this JobModel.  # noqa: E501

        The date of creation of the Job, as text formatted according to the ISO 8601 standard.  # noqa: E501

        :return: The creation_date of this JobModel.  # noqa: E501
        :rtype: datetime
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this JobModel.

        The date of creation of the Job, as text formatted according to the ISO 8601 standard.  # noqa: E501

        :param creation_date: The creation_date of this JobModel.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and creation_date is None:  # noqa: E501
            raise ValueError("Invalid value for `creation_date`, must not be `None`")  # noqa: E501

        self._creation_date = creation_date

    @property
    def updated_on(self):
        """Gets the updated_on of this JobModel.  # noqa: E501

        Last time that anything changed in present line.   # noqa: E501

        :return: The updated_on of this JobModel.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_on

    @updated_on.setter
    def updated_on(self, updated_on):
        """Sets the updated_on of this JobModel.

        Last time that anything changed in present line.   # noqa: E501

        :param updated_on: The updated_on of this JobModel.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and updated_on is None:  # noqa: E501
            raise ValueError("Invalid value for `updated_on`, must not be `None`")  # noqa: E501

        self._updated_on = updated_on

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
        if not isinstance(other, JobModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, JobModel):
            return True

        return self.to_dict() != other.to_dict()
