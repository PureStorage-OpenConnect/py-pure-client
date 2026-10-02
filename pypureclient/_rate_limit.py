"""
Retry policy for responses that mean "the server is overloaded, try later":

* HTTP 429 Too Many Requests (rate limiter)
* HTTP 503 Service Unavailable
* HTTP 500 whose body carries the error message "Server is busy".

All three wait the same way.

1. ``Retry-After`` header (RFC 7231): seconds
2. ``RateLimit-Reset`` header: seconds until the rate limit window resets
3. No usable header: exponential backoff 1s, 2s, 4s ... capped at 30s,
   plus 0-50% random jitter

A wait the server asked for gets a small random extra (0-0.5 s)
"""
import json
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ._transport.rest import ApiException

DEFAULT_RATE_LIMIT_WAIT = 1.0       # seconds, first wait when the server sends no hint
MAX_DEFAULT_RATE_LIMIT_WAIT = 30.0  # seconds, cap for the exponential backoff
SERVER_WAIT_JITTER = 0.5            # seconds, max random extra on top of a server-requested wait
LOGIN_RATE_LIMIT_RETRIES = 3        # retries of an overloaded login or token exchange
SERVER_BUSY_MESSAGE = "Server is busy"  # Purity middleware overload rejection, sent as HTTP 500


def is_overloaded(error):
    """
    Return True if the ApiException means the server is overloaded and the
    call is worth retrying after a wait: 429, 503, or 500 "Server is busy".
    """
    return error.status in (429, 503) or is_server_busy(error)


def is_server_busy(error):
    """
    Return True if the ApiException is Purity's overload rejection: HTTP 500
    with a body like ``{"errors": [{"message": "Server is busy"}]}``.

    Any body that is missing, not JSON, or not in that shape is not busy.
    """
    if error.status != 500 or not error.body:
        return False
    try:
        body = json.loads(error.body)
    except (TypeError, ValueError):
        return False
    if not isinstance(body, dict):
        return False
    errors = body.get('errors')
    if not isinstance(errors, list):
        return False
    return any(isinstance(err, dict) and err.get('message') == SERVER_BUSY_MESSAGE
               for err in errors)


def rate_limit_wait(headers, attempt):
    """
    Return how many seconds to wait before retrying an overloaded response.

    Args:
        headers: Response headers, a case-insensitive mapping or None.
        attempt (int): Number of overloaded responses already seen for this call.

    Returns:
        float: Seconds to wait. Never negative.
    """
    headers = headers or {}
    wait = _parse_retry_after(headers.get('Retry-After'))
    if wait is None:
        wait = _parse_seconds(headers.get('RateLimit-Reset'))
    if wait is not None:
        return wait + random.uniform(0, SERVER_WAIT_JITTER)
    wait = min(DEFAULT_RATE_LIMIT_WAIT * 2 ** attempt, MAX_DEFAULT_RATE_LIMIT_WAIT)
    return wait + random.uniform(0, wait / 2)


def call_with_rate_limit_retries(call, retries=LOGIN_RATE_LIMIT_RETRIES):
    """
    Call ``call()`` and retry it while the server is overloaded (see
    ``is_overloaded``), waiting as ``rate_limit_wait`` says.

    Used for login and token exchange, which run outside the client's own
    retry loop. The array's rate limiter and overload protection run before
    authentication, so a login is rejected like any other request.

    Args:
        call: Callable without arguments. Raises ApiException on HTTP errors.
        retries (int): Maximum number of retries after the first overloaded response.

    Returns:
        Whatever ``call`` returns.

    Raises:
        ApiException: Any other error at once, or the last overloaded
            response once retries are exhausted.
    """
    attempt = 0
    while True:
        try:
            return call()
        except ApiException as error:
            if not is_overloaded(error) or attempt >= retries:
                raise
            time.sleep(rate_limit_wait(error.headers, attempt))
            attempt += 1


def _parse_seconds(value):
    """Parse a non-negative integer number of seconds. Return None if invalid."""
    try:
        seconds = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


def _parse_retry_after(value):
    """Parse ``Retry-After`` as delay-seconds or as an HTTP-date. Return None if invalid."""
    seconds = _parse_seconds(value)
    if seconds is not None or not value:
        return seconds
    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    return max((retry_at - datetime.now(timezone.utc)).total_seconds(), 0.0)
