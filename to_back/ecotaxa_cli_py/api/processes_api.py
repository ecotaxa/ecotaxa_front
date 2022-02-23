# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.26
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


class ProcessesApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def process_query(self, process_id, **kwargs):  # noqa: E501
        """Process Query  # noqa: E501

        Returns **information about the process** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.process_query(process_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int process_id: Internal, the unique numeric id of this process. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: ProcessModel
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.process_query_with_http_info(process_id, **kwargs)  # noqa: E501

    def process_query_with_http_info(self, process_id, **kwargs):  # noqa: E501
        """Process Query  # noqa: E501

        Returns **information about the process** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.process_query_with_http_info(process_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int process_id: Internal, the unique numeric id of this process. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(ProcessModel, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'process_id'
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
                    " to method process_query" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'process_id' is set
        if self.api_client.client_side_validation and ('process_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['process_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `process_id` when calling `process_query`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'process_id' in local_var_params:
            path_params['process_id'] = local_var_params['process_id']  # noqa: E501

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
            '/process/{process_id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='ProcessModel',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_processes(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Processes  # noqa: E501

        Do the required **update for each process in the set.**  **Returns the number of updated entities.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_processes(bulk_update_req, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param BulkUpdateReq bulk_update_req: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: int
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.update_processes_with_http_info(bulk_update_req, **kwargs)  # noqa: E501

    def update_processes_with_http_info(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Processes  # noqa: E501

        Do the required **update for each process in the set.**  **Returns the number of updated entities.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_processes_with_http_info(bulk_update_req, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param BulkUpdateReq bulk_update_req: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(int, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'bulk_update_req'
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
                    " to method update_processes" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'bulk_update_req' is set
        if self.api_client.client_side_validation and ('bulk_update_req' not in local_var_params or  # noqa: E501
                                                        local_var_params['bulk_update_req'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `bulk_update_req` when calling `update_processes`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'bulk_update_req' in local_var_params:
            body_params = local_var_params['bulk_update_req']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerOrCookieAuth']  # noqa: E501

        return self.api_client.call_api(
            '/process_set/update', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='int',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
