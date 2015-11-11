class MarketoException(Exception):
    pass


class MarketoAPIException(MarketoException):
    pass


class InvalidCookieException(MarketoException):
    pass
