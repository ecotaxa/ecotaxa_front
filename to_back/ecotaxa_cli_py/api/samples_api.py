# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.41
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


class SamplesApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def sample_query(self, sample_id, **kwargs):  # noqa: E501
        """Sample Query  # noqa: E501

        Returns **information about the sample** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.sample_query(sample_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int sample_id: Internal, the unique numeric id of this sample. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: SampleModel
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.sample_query_with_http_info(sample_id, **kwargs)  # noqa: E501

    def sample_query_with_http_info(self, sample_id, **kwargs):  # noqa: E501
        """Sample Query  # noqa: E501

        Returns **information about the sample** corresponding to the given id.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.sample_query_with_http_info(sample_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int sample_id: Internal, the unique numeric id of this sample. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(SampleModel, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'sample_id'
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
                    " to method sample_query" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'sample_id' is set
        if self.api_client.client_side_validation and ('sample_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['sample_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `sample_id` when calling `sample_query`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'sample_id' in local_var_params:
            path_params['sample_id'] = local_var_params['sample_id']  # noqa: E501

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
            '/sample/{sample_id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='SampleModel',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def sample_set_get_stats(self, sample_ids, **kwargs):  # noqa: E501
        """Sample Set Get Stats  # noqa: E501

        Returns **classification statistics** for each sample of the given list. One block of stats is returned for each input ID.  EXPECT A SLOW RESPONSE : No cache of such information anywhere.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.sample_set_get_stats(sample_ids, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str sample_ids: String containing the list of one or more sample ids separated by non-num char. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: list[SampleTaxoStatsModel]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.sample_set_get_stats_with_http_info(sample_ids, **kwargs)  # noqa: E501

    def sample_set_get_stats_with_http_info(self, sample_ids, **kwargs):  # noqa: E501
        """Sample Set Get Stats  # noqa: E501

        Returns **classification statistics** for each sample of the given list. One block of stats is returned for each input ID.  EXPECT A SLOW RESPONSE : No cache of such information anywhere.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.sample_set_get_stats_with_http_info(sample_ids, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str sample_ids: String containing the list of one or more sample ids separated by non-num char. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(list[SampleTaxoStatsModel], status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'sample_ids'
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
                    " to method sample_set_get_stats" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'sample_ids' is set
        if self.api_client.client_side_validation and ('sample_ids' not in local_var_params or  # noqa: E501
                                                        local_var_params['sample_ids'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `sample_ids` when calling `sample_set_get_stats`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'sample_ids' in local_var_params and local_var_params['sample_ids'] is not None:  # noqa: E501
            query_params.append(('sample_ids', local_var_params['sample_ids']))  # noqa: E501

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
            '/sample_set/taxo_stats', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[SampleTaxoStatsModel]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def samples_search(self, project_ids, id_pattern, **kwargs):  # noqa: E501
        """Samples Search  # noqa: E501

        **Search for samples.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.samples_search(project_ids, id_pattern, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str project_ids: String containing the list of one or more project id separated by non-num char. (required)
        :param str id_pattern: Sample id textual pattern. Use * or '' for 'any matches'. Match is case-insensitive. (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: list[SampleModel]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.samples_search_with_http_info(project_ids, id_pattern, **kwargs)  # noqa: E501

    def samples_search_with_http_info(self, project_ids, id_pattern, **kwargs):  # noqa: E501
        """Samples Search  # noqa: E501

        **Search for samples.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.samples_search_with_http_info(project_ids, id_pattern, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str project_ids: String containing the list of one or more project id separated by non-num char. (required)
        :param str id_pattern: Sample id textual pattern. Use * or '' for 'any matches'. Match is case-insensitive. (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(list[SampleModel], status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'project_ids',
            'id_pattern'
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
                    " to method samples_search" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'project_ids' is set
        if self.api_client.client_side_validation and ('project_ids' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_ids'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_ids` when calling `samples_search`")  # noqa: E501
        # verify the required parameter 'id_pattern' is set
        if self.api_client.client_side_validation and ('id_pattern' not in local_var_params or  # noqa: E501
                                                        local_var_params['id_pattern'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `id_pattern` when calling `samples_search`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'project_ids' in local_var_params and local_var_params['project_ids'] is not None:  # noqa: E501
            query_params.append(('project_ids', local_var_params['project_ids']))  # noqa: E501
        if 'id_pattern' in local_var_params and local_var_params['id_pattern'] is not None:  # noqa: E501
            query_params.append(('id_pattern', local_var_params['id_pattern']))  # noqa: E501

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
            '/samples/search', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[SampleModel]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_samples(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Samples  # noqa: E501

        Do the required **update for each sample in the set.**  Any non-null field in the model is written to every impacted sample.  **Returns the number of updated entities.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_samples(bulk_update_req, async_req=True)
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
        return self.update_samples_with_http_info(bulk_update_req, **kwargs)  # noqa: E501

    def update_samples_with_http_info(self, bulk_update_req, **kwargs):  # noqa: E501
        """Update Samples  # noqa: E501

        Do the required **update for each sample in the set.**  Any non-null field in the model is written to every impacted sample.  **Returns the number of updated entities.**  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_samples_with_http_info(bulk_update_req, async_req=True)
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
                    " to method update_samples" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'bulk_update_req' is set
        if self.api_client.client_side_validation and ('bulk_update_req' not in local_var_params or  # noqa: E501
                                                        local_var_params['bulk_update_req'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `bulk_update_req` when calling `update_samples`")  # noqa: E501

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
            '/sample_set/update', 'POST',
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
