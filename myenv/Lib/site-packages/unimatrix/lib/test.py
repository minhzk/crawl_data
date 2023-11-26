"""Provides testing helper functions and classes."""
import asyncio
import functools
import inspect
import os
import types
import unittest

from unimatrix.lib.environ import parselist


__all__ = ['needs']


#: The current testing stage as defined by the operating system environment
#: variable ``TEST_STAGE``.
TEST_STAGE = os.getenv('TEST_STAGE')

#: The current testing scope as defined by the operating system environment
#: variable ``TEST_SCOPE``.
TEST_SCOPE = os.getenv('TEST_SCOPE')

#: Used to specify `unit` tests.
TEST_UNIT = 'unit'

#: Used to specify `integration` tests.
TEST_INTEGRATION = 'integration'

#: Used to specify `system` tests.
TEST_SYSTEM = 'system'


def needs(capabilities):
    """Return a decorator that skips the test if the required capabilities
    are not satisfied by the test environment. For a description of
    allowed values, refer to :envvar:`TEST_STACK_CAPABILITIES`.

    Args:
        capabilities (list): the list of capabilities required by
            the decorated test.

    A test can declare its required capabilities with the :func:`needs`
    decorator. The decorator may be used at the class or at the
    function level:

    .. code:: python

        class DatabaseTestCase(unittest.TestCase):

            @unimatrix.lib.test.needs('rdbms:postgres')
            def test_run_on_any_version(self):
                ... tests

            @unimatrix.lib.test.needs('rdbms:postgres:13')
            def test_run_on_postgres_13(self):
                ... tests
    """
    if isinstance(capabilities, str):
        capabilities = [capabilities]
    required = set(capabilities)
    provided = parselist(os.environ, 'TEST_STACK_CAPABILITIES', sep=';', cls=set)

    # Quite inefficient
    for cap in set(provided):
        for i in range(len(str.split(cap, ':'))):
            parent = str.join(':', str.rsplit(cap, ':', i+1)[:-i+1])
            if not parent:
                break
            provided.add(parent)

    missing = list(sorted(required - provided))
    if not missing:
        return unittest.skipIf(False, "Required capabilities satisfied.")

    return unittest.skipIf(bool(missing),
        f"Capabilities not satisfied: {','.join(missing)}")


class TestCaseSelector:
    """A class, method or function decorator that skips tests based on the
    configured testing environment.

    Args:
        name (:obj:`str`): the :term:`Test Stage` in which the decorated
            callable must run.
        scopes (:obj:`list`): a list of scopes in which the decorated callable
            must run. If `scopes` is ``None`` and a scope is defined, then the
            test is skipped.
    """

    def __init__(self, name, scopes=None, current_stage=None, current_scope=None):
        self._stage = name
        self._scopes = scopes
        self._current_stage = current_stage
        self._current_scope = current_scope

    def get_current_scope(self):
        """Returns the current testing scope or ``None``."""
        return self._current_scope or TEST_SCOPE

    def get_current_stage(self):
        """Returns the current testing stage or ``None``."""
        return self._current_stage or TEST_STAGE

    def scopes(self, scopes):
        """Add `scopes` to the testing scopes in which the decorated test
        must run.
        """
        if scopes is None:
            return self
        if self._scopes is None:
            self._scopes = []
        self._scopes.extend(scopes)
        return self

    def scope(self, scope):
        """Like :meth:`scopes`, but with a single positional argument of
        type :obj:`str`. Use when only a single scope is to be indicated.
        """
        return self.scopes([scope])

    def skip(self, message): #pylint: disable=no-self-use
        """Ensure that the decorated object is skipped."""
        raise unittest.SkipTest(message)

    def must_skip(self):
        """Return a :obj:`tuple` containing a :obj:`bool` and :obj:`str`
        indicating if a test must be skipped under the current environment,
        and the reason.
        """
        reason_stage = "Test only runs in the '%s' stage" % self._stage
        reason_scope = "Test only runs in the '%s' scope" % self._stage
        current_stage = self.get_current_stage()
        current_scope = self.get_current_scope()
        must_skip = False
        reason = None
        if (current_stage != self._stage)\
        or not current_stage:
            must_skip = True
            reason = reason_stage

        if (current_scope and current_scope not in (self._scopes or []))\
        or (not current_scope and self._scopes):
            must_skip = True
            reason = reason_scope

        return must_skip, reason


    def __call__(self, decoratable):
        """Decorates a decoratable object (class, method or function) and
        raises :exc:`unittest.SkipTest` if the decorated object must be
        skipped by the test runner in the current environment.
        """
        return self._decorate_type(decoratable)\
            if not isinstance(decoratable, types.FunctionType)\
            else self._decorate_function(decoratable)

    def _decorate_type(self, cls):
        must_skip, reason = self.must_skip()
        if must_skip:
            cls.__unittest_skip__ = True
            cls.__unittest_skip_why__ = reason
        return cls

    def _decorate_function(self, func):
        must_skip, reason = self.must_skip()
        if must_skip:
            @functools.wraps(func)
            def decorator(*args, **kwargs): #pylint: disable=unused-argument
                self.skip(reason)
            func = decorator
        return func


def async_test(func):
    """Decorator to run a test asynchronously."""
    @functools.wraps(func)
    def f(self, *args, **kwargs):
        return self.loop.run_until_complete(
            func(self, *args, **kwargs))

    return f


class AsyncTestCaseMetaclass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        if name == 'AsyncTestCase':
            return super_new(cls, name, bases, attrs)

        # Ensure that the loop is created on each run of the test class.
        setup = attrs.pop('setUp', None) or (lambda self: None)
        def setUp(self):
            self.loop = asyncio.new_event_loop()
            if inspect.iscoroutinefunction(setup):
                f = lambda self: self.loop.run_until_complete(setup(self))
            else:
                f = setup
            return f(self)
        attrs['setUp'] = setUp

        for attname, function in list(dict.items(attrs)):
            if not inspect.iscoroutinefunction(function)\
            or not (str.startswith(attname, 'test_') or attname == 'tearDown'):
                continue
            attrs[attname] = async_test(function)

        return super_new(cls, name, bases, attrs)


class AsyncTestCase(unittest.TestCase, metaclass=AsyncTestCaseMetaclass):
    pass


unit = TestCaseSelector(TEST_UNIT) #pylint: disable=invalid-name
integration = TestCaseSelector(TEST_INTEGRATION) #pylint: disable=invalid-name
system = TestCaseSelector(TEST_SYSTEM) #pylint: disable=invalid-name
