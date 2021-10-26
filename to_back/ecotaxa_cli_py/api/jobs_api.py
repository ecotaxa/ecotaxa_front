# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.23
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from to_back.ecotaxa_cli_py.api_client import ApiClient
from to_back.ecotaxa_cli_py.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class JobsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def erase_job_jobs_job_id_delete(self, job_id, **kwargs):  # noqa: E501
        """Erase Job  # noqa: E501

        **Delete the job** from DB, with associated storage.  Return **NULL upon success.**  If the job is running then kill it.  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.erase_job_jobs_job_id_delete(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.erase_job_jobs_job_id_delete_with_http_info(job_id, **kwargs)  # noqa: E501

    def erase_job_jobs_job_id_delete_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Erase Job  # noqa: E501

        **Delete the job** from DB, with associated storage.  Return **NULL upon success.**  If the job is running then kill it.  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.erase_job_jobs_job_id_delete_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method erase_job_jobs_job_id_delete" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `erase_job_jobs_job_id_delete`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_job_file_jobs_job_id_file_get(self, job_id, **kwargs):  # noqa: E501
        """Get Job File  # noqa: E501

        **Return the file produced by given job.**  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_file_jobs_job_id_file_get(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.get_job_file_jobs_job_id_file_get_with_http_info(job_id, **kwargs)  # noqa: E501

    def get_job_file_jobs_job_id_file_get_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Get Job File  # noqa: E501

        **Return the file produced by given job.**  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_file_jobs_job_id_file_get_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_job_file_jobs_job_id_file_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `get_job_file_jobs_job_id_file_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'application/zip', 'text/tab-separated-values'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}/file', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_job_jobs_job_id_get(self, job_id, **kwargs):  # noqa: E501
        """Get Job  # noqa: E501

        Returns **information about the job** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_jobs_job_id_get(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: JobModel
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.get_job_jobs_job_id_get_with_http_info(job_id, **kwargs)  # noqa: E501

    def get_job_jobs_job_id_get_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Get Job  # noqa: E501

        Returns **information about the job** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_jobs_job_id_get_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(JobModel, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_job_jobs_job_id_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `get_job_jobs_job_id_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='JobModel',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_job_log_file_jobs_job_id_log_get(self, job_id, **kwargs):  # noqa: E501
        """Get Job Log File  # noqa: E501

        **Return the log file produced by given job.**  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_log_file_jobs_job_id_log_get(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.get_job_log_file_jobs_job_id_log_get_with_http_info(job_id, **kwargs)  # noqa: E501

    def get_job_log_file_jobs_job_id_log_get_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Get Job Log File  # noqa: E501

        **Return the log file produced by given job.**  🔒 The job must be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_log_file_jobs_job_id_log_get_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_job_log_file_jobs_job_id_log_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `get_job_log_file_jobs_job_id_log_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}/log', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def list_jobs_jobs_get(self, for_admin, **kwargs):  # noqa: E501
        """List Jobs  # noqa: E501

        **Return the jobs** for current user, or all of them if admin is asked for.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.list_jobs_jobs_get(for_admin, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param bool for_admin: If FALSE return the jobs for current user, else return all of them. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: list[JobModel]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.list_jobs_jobs_get_with_http_info(for_admin, **kwargs)  # noqa: E501

    def list_jobs_jobs_get_with_http_info(self, for_admin, **kwargs):  # noqa: E501
        """List Jobs  # noqa: E501

        **Return the jobs** for current user, or all of them if admin is asked for.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.list_jobs_jobs_get_with_http_info(for_admin, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param bool for_admin: If FALSE return the jobs for current user, else return all of them. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(list[JobModel], status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'for_admin'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list_jobs_jobs_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'for_admin' is set
        if self.api_client.client_side_validation and ('for_admin' not in local_var_params or  # noqa: E501
                                                        local_var_params['for_admin'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `for_admin` when calling `list_jobs_jobs_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'for_admin' in local_var_params and local_var_params['for_admin'] is not None:  # noqa: E501
            query_params.append(('for_admin', local_var_params['for_admin']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[JobModel]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def reply_job_question_jobs_job_id_answer_post(self, job_id, **kwargs):  # noqa: E501
        """Reply Job Question  # noqa: E501

        **Send answers to last question.** The job resumes after it receives the reply.  Return **NULL upon success.**  *Note: It's only about data storage here.*   If the data is technically NOK e.g. not a JS object, standard 422 error should be thrown.  If the data is incorrect from consistency point of view, the job will return in Asking state.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.reply_job_question_jobs_job_id_answer_post(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param object body:
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.reply_job_question_jobs_job_id_answer_post_with_http_info(job_id, **kwargs)  # noqa: E501

    def reply_job_question_jobs_job_id_answer_post_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Reply Job Question  # noqa: E501

        **Send answers to last question.** The job resumes after it receives the reply.  Return **NULL upon success.**  *Note: It's only about data storage here.*   If the data is technically NOK e.g. not a JS object, standard 422 error should be thrown.  If the data is incorrect from consistency point of view, the job will return in Asking state.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.reply_job_question_jobs_job_id_answer_post_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param object body:
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id',
            'body'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method reply_job_question_jobs_job_id_answer_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `reply_job_question_jobs_job_id_answer_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}/answer', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def restart_job_jobs_job_id_restart_get(self, job_id, **kwargs):  # noqa: E501
        """Restart Job  # noqa: E501

        **Restart the job related to the given id.**  Return **NULL upon success.**  🔒 The job must be in a restartable state, and be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.restart_job_jobs_job_id_restart_get(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.restart_job_jobs_job_id_restart_get_with_http_info(job_id, **kwargs)  # noqa: E501

    def restart_job_jobs_job_id_restart_get_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Restart Job  # noqa: E501

        **Restart the job related to the given id.**  Return **NULL upon success.**  🔒 The job must be in a restartable state, and be accessible to current user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.restart_job_jobs_job_id_restart_get_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int job_id: Internal, the unique numeric id of this job. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'job_id'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method restart_job_jobs_job_id_restart_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'job_id' is set
        if self.api_client.client_side_validation and ('job_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['job_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `job_id` when calling `restart_job_jobs_job_id_restart_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'job_id' in local_var_params:
            path_params['job_id'] = local_var_params['job_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/jobs/{job_id}/restart', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
