"""
"""

class AuthenticationError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class InternalServerError(Exception):
    pass

class BadRequestError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)

class NotFoundError(Exception):
    pass


def assert_response_status(status, body=None):
    if status == 401:
        raise AuthenticationError()
    if status == 403:
        raise ForbiddenError()
    if status == 500:
        raise InternalServerError()
    if status == 400:
        raise BadRequestError(body)
    if status == 404:
        raise NotFoundError()
