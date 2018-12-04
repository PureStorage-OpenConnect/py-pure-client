class Parameters(object):
    '''
    A class for static parameter names.
    '''
    aggregation = 'aggregation'
    authorization = 'authorization'
    continuation_token = 'continuation_token'
    end_time = 'end_time'
    filter = 'filter'
    ids = 'ids'
    keys = 'keys'
    limit = 'limit'
    names = 'names'
    namespaces = 'namespaces'
    offset = 'offset'
    references = 'references'
    resolution = 'resolution'
    resources = 'resources'
    resource_ids = 'resource_ids'
    resource_names = 'resource_names'
    resource_types = 'resource_types'
    sort = 'sort'
    source_ids = 'source_ids'
    source_names = 'source_names'
    start_time = 'start_time'
    tag = 'tag'
    x_request_id = 'x_request_id'

    @staticmethod
    def get_str_parameters():
        '''
        Get parameters that are expected to be quoted strings.

        Returns:
            list[str]
        '''
        return [Parameters.aggregation, Parameters.continuation_token]

    @staticmethod
    def get_list_parameters():
        '''
        Get parameters that are expected to be a list of unquoted strings.

        Returns:
            list[str]
        '''
        return [Parameters.sort]

    @staticmethod
    def get_list_str_parameters():
        '''
        Get parameters that are expected to be a list of quoted strings.

        Returns:
            list[str]
        '''
        return [Parameters.ids, Parameters.names, Parameters.keys,
                Parameters.namespaces, Parameters.resource_types,
                Parameters.resource_ids, Parameters.resource_names,
                Parameters.source_ids, Parameters.source_names]


class Headers(object):
    '''
    A class for static header names.
    '''
    authorization = 'Authorization'
    x_request_id = 'X-Request-ID'
    x_ratelimit_sec = 'X-RateLimit-Limit-second'
    x_ratelimit_min = 'X-RateLimit-Limit-minute'
    x_ratelimit_remaining_sec = 'X-RateLimit-Remaining-second'
    x_ratelimit_remaining_min = 'X-RateLimit-Remaining-minute'


class Responses(object):
    '''
    A class for static response names.
    '''
    context = 'context'
    errors = 'errors'
    message = 'message'
