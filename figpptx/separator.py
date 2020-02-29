"""Separator.

Note
----
## `Seperator`'s requirement.

### Arguments of ``separator``.
It is called with the signature(artist: Artist).

### Return of ``separator``.
If the return is 2-length **tuple** of Sequences, then it is regarded as ``(shape_artists, image_artists)``.
If the return is Sequence, then it is interpreted as ``shape_artists``.
``image_artists`` is calculated as the other (leaf) artists.


"""

from functools import wraps
import inspect
import warnings
from collections.abc import Collection, Sequence
from matplotlib.artist import Artist


class SeparatorManager:
    """

    Example
    --------
    @SeparatorManager.register("key")
    def sample_separator(artist):
        ...
        return (shape_artists, image_artists)

    then, users can fetch separator with ``key``.
    """

    roster = dict()

    @classmethod
    def register(cls, key):
        key = key.lower()
        if key in cls.roster:
            warnings.warn(f"{key} is already used, but overridden.")

        def wrapped(method):
            if inspect.isclass(method):
                # When ``class`` is registered,
                # the registered instance is generated with no parameters.
                target = method()
            else:
                target = method
            assert callable(target)
            cls.roster[key] = target

            return method

        return wrapped

    @classmethod
    def fetch(cls, separator):
        if isinstance(separator, str):
            key = separator.lower()
            return cls.roster[key]
        assert callable(separator)
        return separator


class SeparatorInterpreter:
    """Interpret output of ``separator``.

    Args:
        separator: Separator.
        artist: Artist
    """

    def __init__(self, separator, artist):
        """
        """
        self.separator = SeparatorManager.fetch(separator)
        self.artist = artist
        self._original_output = self.separator(self.artist)

    @property
    def original_output(self):
        return self._original_output

    @property
    def partition(self):
        """(shape_artists, image_artists).
        """
        return self._interpret(self.original_output, self.artist)

    def _interpret(self, separator_result, target):
        """Interpret return of ``Separator``.

        Convert output of ``separator`` as the follows.

        Return:
            2-length tuple, `(shape_artist, image_artist)`.
            `shape_artist` is  used for ``transcribe``.
            `image_artist` is  used for ``rasterize``.

        Note
        ----
        For specification, please refer to docString of this module.

        When 1- Artists / Sequence is given, only the leaf ``artists``  are returned.
        """
        # If 2-length tuple, then it returns as is.
        if len(separator_result) == 2 and all(
            isinstance(elem, Sequence) for elem in separator_result
        ):
            return separator_result

        assert isinstance(separator_result, Sequence)
        # Then, they are regarded as `shape_artist`.
        allmatch = _to_match_func(None)
        shape_leaf_artists = sum(
            [_get_leaf_artists(elem, allmatch) for elem in separator_result], []
        )
        all_leaf_artists = _get_leaf_artists(target, allmatch)

        shape_left_ids = {id(elem) for elem in shape_leaf_artists}
        image_leaf_artists = [
            elem for elem in all_leaf_artists if id(elem) not in shape_left_ids
        ]
        return shape_leaf_artists, image_leaf_artists


class FindobjSeparator:
    """Separator similar to ``Artist.findobj``.

    """

    def __init__(self, match):
        self.match = _to_match_func(match)

    def __call__(self, target):
        """
        Args:
            target: Artist.
        Return: 2-length tuple. (shape_artists, image_artists)
            shape_artists (list): Leaf Artists for conversion of shape.
            image_artists (list): Leaf Artists for an image.
        """
        shape_leaf_artists = _get_leaf_artists(target, self.match)
        allmatch = _to_match_func(None)
        all_leaf_artists = _get_leaf_artists(target, allmatch)
        shape_left_ids = {id(elem) for elem in shape_leaf_artists}
        image_leaf_artists = [
            elem for elem in all_leaf_artists if id(elem) not in shape_left_ids
        ]
        return shape_leaf_artists, image_leaf_artists


def _get_leaf_artists(root_artist, matchfunc):
    """Return all the leaf artists.
    which

    Args:
        root_artist: Artist.
        matchfunc: callable: artist -> bool.

    Return:
        All the decendant Artists matched with `matchfunc`.

    Note
    ----
    As you might notice, this class is similar to `Artist.findobj`.
    However, only leaf artists are gathered.
    * https://matplotlib.org/_modules/matplotlib/artist.html#Artist.findobj

    """

    def _inner(artist, is_target):
        if matchfunc(artist):
            is_target = True
        children = artist.get_children()
        if children:
            result = sum([_inner(elem, is_target) for elem in children], [])
        else:
            if is_target:
                result = [artist]
            else:
                result = []
        return result

    result = _inner(root_artist, False)
    return result


def _to_match_func(match):
    """Return a function, (artist -> bool).

    Note
    ----
    Implementation Policy: Extend behavior of``Artist.findobj`` (3.1.2).

    Reference
    * https://matplotlib.org/_modules/matplotlib/artist.html#Artist.findobj
    """

    def _to_id(elem):
        if isinstance(elem, int):
            return elem
        return id(elem)

    if match is None:
        return lambda artist: True
    elif callable(match):
        return match
    elif isinstance(match, int):
        return lambda artist: id(artist) == match
    elif isinstance(match, Artist):
        return lambda artist: (artist is match)
    elif isinstance(match, type) and issubclass(match, Artist):
        return lambda artist: isinstance(artist, match)
    elif isinstance(match, Collection):
        id_set = {_to_id(elem) for elem in match}
        return lambda artist: id(artist) in id_set
    else:
        raise ValueError("Cannot handle given ``match``.")
