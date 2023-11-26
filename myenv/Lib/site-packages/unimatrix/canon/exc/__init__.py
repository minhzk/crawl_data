"""Declares base exception classes that all Unimatrix projects should
recognize, and may raise to set an error condition with a well-defined
meaning.
"""
import functools
import uuid


class FailedOperation(Exception):
    """Represents an exception that was caused by a failure
    of a requested operation.
    """
    version = "unimatrixone.io/v1"
    default_status = 421
    default_code = 'UNKNOWN_ERROR'

    @classmethod
    def catch(cls, on_exception):
        """Returns a decorator that invokes callable `on_exception`
        when a :class:`FailedOperation` is raised.
        """
        def decorator(func):
            @functools.wraps(func)
            def f(*args, **kwargs): #pylint: disable=invalid-name
                try:
                    return func(*args, **kwargs)
                except FailedOperation as e: #pylint: disable=invalid-name
                    return on_exception(e)
            return f
        return decorator

    def __init__(self, status=None, code=None, stderr=None):
        super().__init__()
        self.code = code or self.default_code
        self.status = status or self.default_status
        self.stderr = stderr or ''
        self.uid = str(uuid.uuid4())

    def get_metadata(self):
        """Returns metadata describing the exception instance."""
        return {
            'uid': self.uid,
            'annotations': {
                'unimatrixone.io/http-status-code': self.status
            }
        }

    @property
    def dto(self):
        """Returns the exception as a Data Transfer Object (DTO) that is
        ready for serialization and transmission over the network.
        """
        return {
            'api_version': self.version,
            'kind': type(self).__name__,
            'metadata': self.get_metadata(),
            'spec': {
                'code': self.code
            }
        }


class AccessDenied(FailedOperation):
    """Raised when an operation fails due to request not
    having permission.
    """
    default_code = 'ACCESS_DENIED'
    default_status = 401


class ResourceDoesNotExist(FailedOperation):
    """Raised when an operation fails due to an upstream
    resource not existing.
    """
    default_code = 'DOES_NOT_EXIST'
    default_status = 404


class Unreachable(FailedOperation):
    """Raised when an operation fails due to an upstream
    resource not being reachable.
    """
    default_code = 'UNREACHABLE'
    default_status = 503


class Timeout(Unreachable):
    """Raised when an operation fails due to a timeout
    when accessing an upstream resource.
    """
