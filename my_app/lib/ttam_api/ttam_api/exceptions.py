class OauthClientException(Exception):

    """ Base OauthClient Exception """
    pass


class UnauthenticatedException(OauthClientException):

    """ Got a 401 from the API """
    pass


class PermissionDenied(OauthClientException):

    """ Got a 403 from the API """
    pass


class APIError(OauthClientException):

    """ Got a 500 from the API """
    pass


class NotFound(OauthClientException):

    """ Got a 404 from the API """
    pass


class BadRequest(OauthClientException):

    """ Got a 400 from the API """
    pass


class Unprocessable(OauthClientException):

    """ Got a 422 from the API """
    pass
