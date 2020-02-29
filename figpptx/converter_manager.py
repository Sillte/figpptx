"""Converter Manager.

Example
-------

@ConverterManager.register(``type of artist``)
def sample_converter(slide_editor, artist):
    # generate shapes
    pass
    return [shapes]

Basic Procedure
---------------
From the given ``Artist``'s properties, generate ``Shape`` via ``slide_editor``.

Required Specification
--------------------------------------------

* If shapes are generated, it must return the generated shapes.
* If it decides  ``Artist`` should not be displayed, it raises ``NoDisplayException``.
* If it decides  ``Artist`` should be delegated to ``Renderer``, it raises ``NoDisplayException``.

Note
----
* Class for registration must be equivalent. Subclass does not match.
*``Figure`` and ``Axes`` is not accepted.

"""

from functools import wraps
from matplotlib.artist import Artist
import matplotlib.figure
from matplotlib.axes._base import _AxesBase
import inspect


""" These exceptions are intended to be used by each converter.
PPTXTranscriber catches these exceptions and decide processings.
"""


class NonDisplayException(Exception):
    """It is used for ``Artist`` which is not displayed.
    """

    pass


class NonHandlingException(Exception):
    """It is used for ``Artist` which is delegated to ``Renderer``.
    """

    pass


class ConverterManager:
    """ Fetch / Register of Converter.
    """

    roster = dict()

    @classmethod
    def fetch(cls, klass):
        """Fetch the function for `klass`.

        Args:
            klass: Artist class.
        Return:
            function. whose signature is (slide_editor: SlideEditor, artist: Artist).
        Raises:
            KeyError. If corresponding function does not exist for given ``klass``.
        """
        key = _to_key(klass)
        if key not in cls.roster:
            raise KeyError()
        return cls.roster[key]

    @classmethod
    def is_registered(cls, klass):
        klass = _to_cls(klass)
        key = _to_key(klass)
        return key in cls.roster

    @classmethod
    def register(cls, klass):
        klass = _to_cls(klass)
        if not issubclass(klass, Artist):
            raise ValueError(f"Class must be subclass of Artist: {klass}")
        if issubclass(klass, (matplotlib.figure.Figure, _AxesBase)):
            raise ValueError(f"Figure and Axis cannot be accepted.: {klass}")
        key = _to_key(klass)

        """ Overwrite the ``roster`` if multiple functions are defined
        for the specific class.
        """

        def wrapped(method):
            # Registration.
            cls.roster[key] = method
            return method

        return wrapped


def _to_key(klass):
    klass = _to_cls(klass)
    assert inspect.isclass(klass)
    return (klass.__module__, klass.__name__)


def _to_cls(klass):
    if inspect.isclass(klass):
        return klass
    else:
        return type(klass)


if __name__ == "__main__":
    pass
