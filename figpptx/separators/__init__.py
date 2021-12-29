""" You have to clarify import here.
"""

from . import default_separator  # NOQA

from figpptx.separator import SeparatorManager, get_leaf_artists


@SeparatorManager.register("rasterize")
def separator(target):
    """All of the artist are given to ``rasterize``."""

    def matchfunc(artist):
        return False

    return get_leaf_artists(target, matchfunc)


""" Due to micellaneous processings when ``fig`` and ``ax`` are given,
``matchfunc = lambda artist: True`` is different from `transcribe``.
"""
