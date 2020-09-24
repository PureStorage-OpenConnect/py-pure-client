import pprint

from .keywords import Headers, Parameters


class ResponseHeaders(object):
    """
    An object that includes headers from the server response.
    """

    def __init__(self, x_request_id, x_ratelimit_limit_second, x_ratelimit_limit_minute,
                 x_ratelimit_remaining_second, x_ratelimit_remaining_minute):
        """
        Initialize a ResponseHeaders.

        Args:
            x_request_id (str): The X-Request-ID from the client or generated
                by the server.
            x_ratelimit_limit_second (int): The number of requests available
                per second.
            x_ratelimit_limit_minute (int): The number of requests available
                per minute.
            x_ratelimit_remaining_second (int): The number of requests remaining
                in that second.
            x_ratelimit_remaining_minute (int): The number of requests remaining
                in that minute.
        """
        self.x_request_id = x_request_id
        self.x_ratelimit_limit_second = x_ratelimit_limit_second
        self.x_ratelimit_limit_minute = x_ratelimit_limit_minute
        self.x_ratelimit_remaining_second = x_ratelimit_remaining_second
        self.x_ratelimit_remaining_minute = x_ratelimit_remaining_minute

    def to_dict(self):
        """
        Return a dictionary of the class attributes.

        Returns:
            dict
        """
        return self.__dict__

    def __repr__(self):
        """
        Return a pretty formatted string of the object.

        Returns:
            str
        """
        return pprint.pformat(self.to_dict())


def _create_response_headers(headers):
    response_headers = None
    if headers and headers.get(Headers.x_request_id, None):
        response_headers = ResponseHeaders(headers.get(Headers.x_request_id, None),
                                           headers.get(Headers.x_ratelimit_sec, None),
                                           headers.get(Headers.x_ratelimit_min, None),
                                           headers.get(Headers.x_ratelimit_remaining_sec, None),
                                           headers.get(Headers.x_ratelimit_remaining_min, None))
    return response_headers


class Response(object):
    """
    An abstract response that is extended to a valid or error response.
    """

    def __init__(self, status_code, headers):
        """
        Initialize a Response.

        Args:
            status_code (int): The HTTP status code.
            headers (dict): Response headers from the server.
        """
        self.status_code = status_code
        self.headers = _create_response_headers(headers)


class ValidResponse(Response):
    """
    A response that indicates the request was successful and has the returned
    data.
    """

    def __init__(self, status_code, continuation_token, total_item_count,
                 items, headers, total=None, more_items_remaining=None):
        """
        Initialize a ValidResponse.

        Args:
            status_code (int): The HTTP status code.
            continuation_token (str): An opaque token to iterate over a
                collection of resources. May be None.
            total_item_count (int): The total number of items available in the
                collection.
            items (ItemIterator): An iterator over the items in the collection.
            headers (dict): Response headers from the server.
        """
        super(ValidResponse, self).__init__(status_code, headers)
        self.continuation_token = continuation_token
        self.total_item_count = total_item_count
        self.items = items
        if total is not None:
            self.total = total
        if more_items_remaining is not None:
            self.more_items_remaining = more_items_remaining

    def to_dict(self):
        """
        Return a dictionary of the class attributes. It will convert the items
        to a list of items by exhausting the iterator. If any items were
        previously iterated, they will be missed.

        Returns:
            dict
        """
        new_dict = dict(self.__dict__)
        if isinstance(self.items, ItemIterator):
            new_dict['items'] = [item.to_dict() for item in list(self.items)]

        new_dict['headers'] = (self.headers.to_dict
                               if self.headers is not None else None)

        if hasattr(self, 'total') and isinstance(self.total, list):
            new_dict['total'] = [item.to_dict() for item in self.total]
        return new_dict

    def __repr__(self):
        """
        Return a pretty formatted string of the object. Does not convert the
        items to a list of items by using the iterator.

        Returns:
            str
        """
        new_dict = dict(self.__dict__)
        if self.headers:
            new_dict['headers'] = self.headers.to_dict()
        return pprint.pformat(new_dict)


class ErrorResponse(Response):
    """
    A response that indicates there was an error with the request and has the
    list of errors.
    """

    def __init__(self, status_code, errors, headers):
        """
        Initialize an ErrorResponse.

        Args:
            status_code (int): The HTTP status code.
            errors (list[ApiError]): The list of errors encountered.
            headers (dict): Response headers from the
                server.
        """
        super(ErrorResponse, self).__init__(status_code,
                                            headers)
        self.errors = errors

    def to_dict(self):
        """
        Return a dictionary of the class attributes.

        Returns:
            dict
        """
        new_dict = dict(self.__dict__)
        new_dict['errors'] = [err.to_dict() for err in new_dict['errors']]
        new_dict['headers'] = (self.headers.to_dict
                               if self.headers is not None else None)
        return new_dict

    def __repr__(self):
        """
        Return a pretty formatted string of the object.

        Returns:
            str
        """
        return pprint.pformat(self.to_dict())


class ApiError(object):
    """
    An object that models the error response from the server.
    """

    def __init__(self, context, message):
        """
        Initialize an ApiError.

        Args:
            context (str): The context in which the error occurred.
            message (str): The error message.
        """
        self.context = context
        self.message = message

    def to_dict(self):
        """
        Return a dictionary of the class attributes.

        Returns:
            dict
        """
        return self.__dict__

    def __repr__(self):
        """
        Return a pretty formatted string of the object.

        Returns:
            str
        """
        return pprint.pformat(self.to_dict())


class ItemIterator(object):
    """
    An iterator for items of a collection returned by the server.
    """

    def __init__(self, client, api_endpoint, kwargs,  continuation_token,
                 total_item_count, items, x_request_id, more_items_remaining=None,
                 response_size_limit=1000):
        """
        Initialize an ItemIterator.

        Args:
            client (Client): A Pure1 Client that can call the API.
            api_endpoint (function): The function that corresponds to the
                internal API call.
            kwargs (dict): The kwargs of the initial call.
            continuation_token (str): The continuation token provided by the
                server. May be None.
            total_item_count (int): The total number of items available in the
                collection.
            items (list[object]): The items returned from the initial response.
            x_request_id (str): The X-Request-ID to use for all subsequent calls.
        """
        self._response_size_limit = response_size_limit
        self._client = client
        self._api_endpoint = api_endpoint
        self._kwargs = kwargs
        self._continuation_token = '\'{}\''.format(continuation_token)
        self._total_item_count = total_item_count
        self._more_items_remaining = more_items_remaining
        self._items = items
        self._x_request_id = x_request_id
        self._index = 0

    def __iter__(self):
        """
        Creates a new iterator.

        Returns:
            ItemIterator
        """
        return self

    def __next__(self):
        """
        Get the next item in the collection. If there are no items left to get
        from the last response, it calls the API again to get more items.

        Returns:
            object

        Raises:
            StopIteration: If there are no more items to return, or if there
                was an error calling the API.
        """
        # If we've reached the end of the desired limit, stop
        if Parameters.limit in self._kwargs and self._kwargs.get(Parameters.limit) <= self._index:
            raise StopIteration
        # If we've reached the end of all possible items, stop
        if self._total_item_count is not None and self._total_item_count <= self._index:
            raise StopIteration
        if self._response_size_limit is None:
            item_index = self._index
        else:
            item_index = self._index % self._response_size_limit
        # If we've reached the end of the current collection, get more data
        if item_index == len(self._items):
            if self._more_items_remaining is False:
                raise StopIteration
            self._refresh_data()
        # Return the next item in the current list if possible
        if item_index < len(self._items):
            to_return = self._items[item_index]
            self._index += 1
            return to_return
        # If no new data was given, just stop
        raise StopIteration

    # Required for python2 compatibility
    next = __next__

    def __len__(self):
        """
        Get the length of collection. Number of items returned is not guaranteed
        to be the length of collection at the start.

        Returns:
            int
        """
        return self._total_item_count or len(self._items)

    def _refresh_data(self):
        """
        Call the API to collect more items and updates the internal state.

        Raises:
            StopIteration: If there was an error calling the API.
        """
        # Use continuation token if provided
        if Parameters.continuation_token in self._kwargs:
            self._kwargs[Parameters.continuation_token] = self._continuation_token
        else: # Use offset otherwise (no continuation token with sorts)
            self._kwargs[Parameters.offset] = len(self._items)
        if self._x_request_id is not None:
            self._kwargs[Parameters.x_request_id] = self._x_request_id
        # Call the API again and update internal state
        response, is_error = self._client._call_api(self._api_endpoint,
                                                    self._kwargs)
        if is_error is True:
            raise StopIteration
        body, _, _ = response
        self._continuation_token = '\'{}\''.format(body.continuation_token)
        self._total_item_count = body.total_item_count
        self._items = body.items
