class Parameters(object):
    """
    A class for static parameter names.
    """
    continuation_token = 'continuation_token'
    filter = 'filter'
    limit = 'limit'
    offset = 'offset'
    sort = 'sort'
    x_request_id = 'x_request_id'


class Headers(object):
    """
    A class for static header names.
    """
    api_token = 'api-token'
    authorization = 'Authorization'
    x_auth_token = 'x-auth-token'
    x_request_id = 'X-Request-ID'
    x_ratelimit_sec = 'X-RateLimit-Limit-second'
    x_ratelimit_min = 'X-RateLimit-Limit-minute'
    x_ratelimit_remaining_sec = 'X-RateLimit-Remaining-second'
    x_ratelimit_remaining_min = 'X-RateLimit-Remaining-minute'


class Responses(object):
    """
    A class for static response names.
    """
    context = 'context'
    errors = 'errors'
    message = 'message'
