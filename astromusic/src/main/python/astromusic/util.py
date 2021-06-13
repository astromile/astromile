import functools
import inspect
import warnings


class AstromusicDeprecationWarning(DeprecationWarning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, (type(b''), type(u''))):
        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = f'Class {func1.__name__} is deprecated: {reason}.'
            else:
                fmt1 = f'Function {func1.__name__} is deprecated: {reason}.'

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', AstromusicDeprecationWarning)
                warnings.warn(fmt1, category=AstromusicDeprecationWarning, stacklevel=2)
                warnings.simplefilter('default', AstromusicDeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = f'Class {func2.__name__} is deprecated.'
        else:
            fmt2 = f'Function {func2.__name__} is deprecated.'

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', AstromusicDeprecationWarning)
            warnings.warn(fmt2, category=AstromusicDeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', AstromusicDeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))


def test_deprecation():
    def normal_function():
        warnings.warn('ignore, this message is here for testing purposes',
                      category=DeprecationWarning,
                      stacklevel=2)

    @deprecated
    def deprecated_function():
        print("I'm deprecated")

    @deprecated('Use normal_function instead')
    def reasonably_deprecated_function():
        print("I'm deprecated, but there is a reason!")

    @deprecated
    class DeprecatedClass:
        def __init__(self):
            pass

    @deprecated("Never use classes, it's mauvais ton")
    class ReasonablyDeprecatedClass:
        def __init__(self):
            pass

    def run_logging(func):
        print('invoking', func.__name__)
        func()
        print('exiting', func.__name__)

    [run_logging(f) for f in [normal_function, deprecated_function, reasonably_deprecated_function]]
    [run_logging(c) for c in [DeprecatedClass, ReasonablyDeprecatedClass]]


if __name__ == '__main__':
    test_deprecation()
