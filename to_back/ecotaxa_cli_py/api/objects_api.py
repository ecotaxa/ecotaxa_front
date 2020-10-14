# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.4
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


class ObjectsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def classify_object_set_object_set_classify_post(self, classify_req, **kwargs):  # noqa: E501
        """Classify Object Set  # noqa: E501

        Change classification and/or qualification for a set of objects. Current user needs at least Annotate right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.classify_object_set_object_set_classify_post(classify_req, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param ClassifyReq classify_req: (required)
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
        return self.classify_object_set_object_set_classify_post_with_http_info(classify_req, **kwargs)  # noqa: E501

    def classify_object_set_object_set_classify_post_with_http_info(self, classify_req, **kwargs):  # noqa: E501
        """Classify Object Set  # noqa: E501

        Change classification and/or qualification for a set of objects. Current user needs at least Annotate right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.classify_object_set_object_set_classify_post_with_http_info(classify_req, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param ClassifyReq classify_req: (required)
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
            'classify_req'
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
                    " to method classify_object_set_object_set_classify_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'classify_req' is set
        if self.api_client.client_side_validation and ('classify_req' not in local_var_params or  # noqa: E501
                                                        local_var_params['classify_req'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `classify_req` when calling `classify_object_set_object_set_classify_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'classify_req' in local_var_params:
            body_params = local_var_params['classify_req']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/classify', 'POST',
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

    def erase_object_set_object_set_delete(self, request_body, **kwargs):  # noqa: E501
        """Erase Object Set  # noqa: E501

        Delete the objects with given object ids. Current user needs Manage right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.erase_object_set_object_set_delete(request_body, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param list[int] request_body: (required)
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
        return self.erase_object_set_object_set_delete_with_http_info(request_body, **kwargs)  # noqa: E501

    def erase_object_set_object_set_delete_with_http_info(self, request_body, **kwargs):  # noqa: E501
        """Erase Object Set  # noqa: E501

        Delete the objects with given object ids. Current user needs Manage right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.erase_object_set_object_set_delete_with_http_info(request_body, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param list[int] request_body: (required)
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
            'request_body'
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
                    " to method erase_object_set_object_set_delete" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'request_body' is set
        if self.api_client.client_side_validation and ('request_body' not in local_var_params or  # noqa: E501
                                                        local_var_params['request_body'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `request_body` when calling `erase_object_set_object_set_delete`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'request_body' in local_var_params:
            body_params = local_var_params['request_body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/', 'DELETE',
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

    def get_object_set_object_set_project_id_query_post(self, project_id, project_filters, **kwargs):  # noqa: E501
        """Get Object Set  # noqa: E501

        Return object ids for the given project with the filters.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_object_set_object_set_project_id_query_post(project_id, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param ProjectFilters project_filters: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: ObjectSetQueryRsp
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.get_object_set_object_set_project_id_query_post_with_http_info(project_id, project_filters, **kwargs)  # noqa: E501

    def get_object_set_object_set_project_id_query_post_with_http_info(self, project_id, project_filters, **kwargs):  # noqa: E501
        """Get Object Set  # noqa: E501

        Return object ids for the given project with the filters.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_object_set_object_set_project_id_query_post_with_http_info(project_id, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param ProjectFilters project_filters: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(ObjectSetQueryRsp, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'project_id',
            'project_filters'
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
                    " to method get_object_set_object_set_project_id_query_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'project_id' is set
        if self.api_client.client_side_validation and ('project_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_id` when calling `get_object_set_object_set_project_id_query_post`")  # noqa: E501
        # verify the required parameter 'project_filters' is set
        if self.api_client.client_side_validation and ('project_filters' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_filters'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_filters` when calling `get_object_set_object_set_project_id_query_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'project_id' in local_var_params:
            path_params['project_id'] = local_var_params['project_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'project_filters' in local_var_params:
            body_params = local_var_params['project_filters']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/{project_id}/query', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='ObjectSetQueryRsp',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post(self, project_id, project_filters, **kwargs):  # noqa: E501
        """Reset Object Set To Predicted  # noqa: E501

        Reset to Predicted all objects for the given project with the filters.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post(project_id, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param ProjectFilters project_filters: (required)
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
        return self.reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post_with_http_info(project_id, project_filters, **kwargs)  # noqa: E501

    def reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post_with_http_info(self, project_id, project_filters, **kwargs):  # noqa: E501
        """Reset Object Set To Predicted  # noqa: E501

        Reset to Predicted all objects for the given project with the filters.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post_with_http_info(project_id, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param ProjectFilters project_filters: (required)
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
            'project_id',
            'project_filters'
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
                    " to method reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'project_id' is set
        if self.api_client.client_side_validation and ('project_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_id` when calling `reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post`")  # noqa: E501
        # verify the required parameter 'project_filters' is set
        if self.api_client.client_side_validation and ('project_filters' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_filters'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_filters` when calling `reset_object_set_to_predicted_object_set_project_id_reset_to_predicted_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'project_id' in local_var_params:
            path_params['project_id'] = local_var_params['project_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'project_filters' in local_var_params:
            body_params = local_var_params['project_filters']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/{project_id}/reset_to_predicted', 'POST',
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

    def revert_object_set_to_history_object_set_project_id_revert_to_history_post(self, project_id, dry_run, project_filters, **kwargs):  # noqa: E501
        """Revert Object Set To History  # noqa: E501

        Revert all objects for the given project, with the filters, to the target. - param `filters`: The set of filters to apply to get the target objects. - param `dry_run`: If set, then no real write but consequences of the revert will be replied. - param `target`: Use null/None for reverting using the last annotation from anyone, or a user id     for the last annotation from this user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.revert_object_set_to_history_object_set_project_id_revert_to_history_post(project_id, dry_run, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param bool dry_run: (required)
        :param ProjectFilters project_filters: (required)
        :param int target:
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: ObjectSetRevertToHistoryRsp
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.revert_object_set_to_history_object_set_project_id_revert_to_history_post_with_http_info(project_id, dry_run, project_filters, **kwargs)  # noqa: E501

    def revert_object_set_to_history_object_set_project_id_revert_to_history_post_with_http_info(self, project_id, dry_run, project_filters, **kwargs):  # noqa: E501
        """Revert Object Set To History  # noqa: E501

        Revert all objects for the given project, with the filters, to the target. - param `filters`: The set of filters to apply to get the target objects. - param `dry_run`: If set, then no real write but consequences of the revert will be replied. - param `target`: Use null/None for reverting using the last annotation from anyone, or a user id     for the last annotation from this user.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.revert_object_set_to_history_object_set_project_id_revert_to_history_post_with_http_info(project_id, dry_run, project_filters, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int project_id: (required)
        :param bool dry_run: (required)
        :param ProjectFilters project_filters: (required)
        :param int target:
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(ObjectSetRevertToHistoryRsp, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'project_id',
            'dry_run',
            'project_filters',
            'target'
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
                    " to method revert_object_set_to_history_object_set_project_id_revert_to_history_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'project_id' is set
        if self.api_client.client_side_validation and ('project_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_id` when calling `revert_object_set_to_history_object_set_project_id_revert_to_history_post`")  # noqa: E501
        # verify the required parameter 'dry_run' is set
        if self.api_client.client_side_validation and ('dry_run' not in local_var_params or  # noqa: E501
                                                        local_var_params['dry_run'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `dry_run` when calling `revert_object_set_to_history_object_set_project_id_revert_to_history_post`")  # noqa: E501
        # verify the required parameter 'project_filters' is set
        if self.api_client.client_side_validation and ('project_filters' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_filters'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_filters` when calling `revert_object_set_to_history_object_set_project_id_revert_to_history_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'project_id' in local_var_params:
            path_params['project_id'] = local_var_params['project_id']  # noqa: E501

        query_params = []
        if 'dry_run' in local_var_params and local_var_params['dry_run'] is not None:  # noqa: E501
            query_params.append(('dry_run', local_var_params['dry_run']))  # noqa: E501
        if 'target' in local_var_params and local_var_params['target'] is not None:  # noqa: E501
            query_params.append(('target', local_var_params['target']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'project_filters' in local_var_params:
            body_params = local_var_params['project_filters']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/{project_id}/revert_to_history', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='ObjectSetRevertToHistoryRsp',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_object_set_object_set_update_post(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Object Set  # noqa: E501

        Update all the objects with given IDs and values Current user needs Manage right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_object_set_object_set_update_post(bulk_update_req, async_req=True)
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
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.update_object_set_object_set_update_post_with_http_info(bulk_update_req, **kwargs)  # noqa: E501

    def update_object_set_object_set_update_post_with_http_info(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Object Set  # noqa: E501

        Update all the objects with given IDs and values Current user needs Manage right on all projects of specified objects.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_object_set_object_set_update_post_with_http_info(bulk_update_req, async_req=True)
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
        :return: tuple(object, status_code(int), headers(HTTPHeaderDict))
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
                    " to method update_object_set_object_set_update_post" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'bulk_update_req' is set
        if self.api_client.client_side_validation and ('bulk_update_req' not in local_var_params or  # noqa: E501
                                                        local_var_params['bulk_update_req'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `bulk_update_req` when calling `update_object_set_object_set_update_post`")  # noqa: E501

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
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/object_set/update', 'POST',
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
