import time
from fastapi import Request, HTTPException


class RateLimiter:
    """
    Rate limiter class to limit the number of requests from clients.
    """
    def __init__(self, max_requests, window_time):
        """
        Initialize the RateLimiter instance.

        :param max_requests: Maximum number of requests allowed within the window time.
        :type max_requests: int
        :param window_time: Time window (in seconds) within which the maximum number of requests are allowed.
        :type window_time: int
        """
        self.requests = {}
        self.max_requests = max_requests
        self.window_time = window_time

    def is_allowed(self, client_id):
        """
        Check if the client is allowed to make a request based on rate limiting rules.

        :param client_id: Unique identifier for the client (e.g., client IP address).
        :type client_id: str
        :return: True if the request is allowed, False otherwise.
        :rtype: bool
        """
        current_time = time.time()
        request_info = self.requests.get(client_id)

        if request_info is None:
            self.requests[client_id] = [current_time, 1]
            return True

        last_request_time, request_count = request_info

        if current_time - last_request_time > self.window_time:
            self.requests[client_id] = [current_time, 1]
            return True

        if request_count < self.max_requests:
            self.requests[client_id][1] += 1
            return True

        return False


RATE_LIMITER = RateLimiter(3, 120)


async def rate_limit(request: Request):
    """
    Rate limit middleware to restrict the number of requests from clients.

    :param request: The incoming HTTP request.
    :type request: Request
    :raises HTTPException: If the number of requests exceeds the limit, raises a 429 Too Many Requests error.
    :return: True if the request is allowed, otherwise raises an exception.
    :rtype: bool
    """
    global RATE_LIMITER
    client_id = request.client.host
    if not RATE_LIMITER.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    return True
