# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.6
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


class TaxonomyTreeApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def query_taxa_set_taxon_set_query_get(self, ids, **kwargs):  # noqa: E501
        """Query Taxa Set  # noqa: E501

        Information about several taxa, including their lineage. The separator between numbers is arbitrary non-digit, e.g. \":\", \"|\" or \",\"  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.query_taxa_set_taxon_set_query_get(ids, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str ids: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: list[TaxonModel]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.query_taxa_set_taxon_set_query_get_with_http_info(ids, **kwargs)  # noqa: E501

    def query_taxa_set_taxon_set_query_get_with_http_info(self, ids, **kwargs):  # noqa: E501
        """Query Taxa Set  # noqa: E501

        Information about several taxa, including their lineage. The separator between numbers is arbitrary non-digit, e.g. \":\", \"|\" or \",\"  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.query_taxa_set_taxon_set_query_get_with_http_info(ids, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str ids: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(list[TaxonModel], status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'ids'
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
                    " to method query_taxa_set_taxon_set_query_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'ids' is set
        if self.api_client.client_side_validation and ('ids' not in local_var_params or  # noqa: E501
                                                        local_var_params['ids'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `ids` when calling `query_taxa_set_taxon_set_query_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'ids' in local_var_params and local_var_params['ids'] is not None:  # noqa: E501
            query_params.append(('ids', local_var_params['ids']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/taxon_set/query', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[TaxonModel]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def query_taxa_taxon_taxon_id_get(self, taxon_id, **kwargs):  # noqa: E501
        """Query Taxa  # noqa: E501

        Information about a single taxon, including its lineage.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.query_taxa_taxon_taxon_id_get(taxon_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int taxon_id: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: TaxonModel
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.query_taxa_taxon_taxon_id_get_with_http_info(taxon_id, **kwargs)  # noqa: E501

    def query_taxa_taxon_taxon_id_get_with_http_info(self, taxon_id, **kwargs):  # noqa: E501
        """Query Taxa  # noqa: E501

        Information about a single taxon, including its lineage.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.query_taxa_taxon_taxon_id_get_with_http_info(taxon_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param int taxon_id: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(TaxonModel, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'taxon_id'
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
                    " to method query_taxa_taxon_taxon_id_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'taxon_id' is set
        if self.api_client.client_side_validation and ('taxon_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['taxon_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `taxon_id` when calling `query_taxa_taxon_taxon_id_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'taxon_id' in local_var_params:
            path_params['taxon_id'] = local_var_params['taxon_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/taxon/{taxon_id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='TaxonModel',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def search_taxa_taxon_set_search_get(self, query, project_id, **kwargs):  # noqa: E501
        """Search Taxa  # noqa: E501

        Search for taxa by name.  Queries can be 'small', i.e. of length < 3 and even zero-length. For a public, unauthenticated call: - zero-length and small queries always return nothing. - otherwise, a full search is done and results are returned in alphabetical order.  Behavior for an authenticated call: - zero-length queries: return the MRU list in full. - small queries: the MRU list is searched, so that taxa in the recent list are returned, if matching. - otherwise, a full search is done. Results are ordered so that taxa in the project list are in first,     and are signalled as such in the response.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.search_taxa_taxon_set_search_get(query, project_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str query: (required)
        :param int project_id: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: list[TaxaSearchRsp]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.search_taxa_taxon_set_search_get_with_http_info(query, project_id, **kwargs)  # noqa: E501

    def search_taxa_taxon_set_search_get_with_http_info(self, query, project_id, **kwargs):  # noqa: E501
        """Search Taxa  # noqa: E501

        Search for taxa by name.  Queries can be 'small', i.e. of length < 3 and even zero-length. For a public, unauthenticated call: - zero-length and small queries always return nothing. - otherwise, a full search is done and results are returned in alphabetical order.  Behavior for an authenticated call: - zero-length queries: return the MRU list in full. - small queries: the MRU list is searched, so that taxa in the recent list are returned, if matching. - otherwise, a full search is done. Results are ordered so that taxa in the project list are in first,     and are signalled as such in the response.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.search_taxa_taxon_set_search_get_with_http_info(query, project_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str query: (required)
        :param int project_id: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(list[TaxaSearchRsp], status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
            'query',
            'project_id'
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
                    " to method search_taxa_taxon_set_search_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'query' is set
        if self.api_client.client_side_validation and ('query' not in local_var_params or  # noqa: E501
                                                        local_var_params['query'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `query` when calling `search_taxa_taxon_set_search_get`")  # noqa: E501
        # verify the required parameter 'project_id' is set
        if self.api_client.client_side_validation and ('project_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['project_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `project_id` when calling `search_taxa_taxon_set_search_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'query' in local_var_params and local_var_params['query'] is not None:  # noqa: E501
            query_params.append(('query', local_var_params['query']))  # noqa: E501
        if 'project_id' in local_var_params and local_var_params['project_id'] is not None:  # noqa: E501
            query_params.append(('project_id', local_var_params['project_id']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/taxon_set/search', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[TaxaSearchRsp]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def taxa_tree_status_taxa_status_get(self, **kwargs):  # noqa: E501
        """Taxa Tree Status  # noqa: E501

        Return the status of taxonomy tree w/r to freshness.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.taxa_tree_status_taxa_status_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: TaxonomyTreeStatus
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.taxa_tree_status_taxa_status_get_with_http_info(**kwargs)  # noqa: E501

    def taxa_tree_status_taxa_status_get_with_http_info(self, **kwargs):  # noqa: E501
        """Taxa Tree Status  # noqa: E501

        Return the status of taxonomy tree w/r to freshness.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.taxa_tree_status_taxa_status_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(TaxonomyTreeStatus, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = [
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
                    " to method taxa_tree_status_taxa_status_get" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['HTTPBearer']  # noqa: E501

        return self.api_client.call_api(
            '/taxa/status', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='TaxonomyTreeStatus',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)