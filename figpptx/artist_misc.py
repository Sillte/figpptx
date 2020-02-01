"""Miscellaneous functions for ``matplotlib.artist.Artist``.
"""
import matplotlib
from collections.abc import Collection


def to_figure(artist):
    """Return Figure of ``artist``.
    """
    if isinstance(artist, matplotlib.figure.Figure):
        return artist
    elif isinstance(artist, matplotlib.axes._base._AxesBase):
        return artist.figure
    elif isinstance(artist, matplotlib.artist.Artist):
        return artist.axes.figure
    raise ValueError("Given ``artist`` is not Artist.", artist)


def to_unique_figures(artists):
    """Return unique figure.
    """
    if not isinstance(artists, Collection):
        return to_figure(artists)

    figure = None
    for artist in artists:
        try:
            t_figure = artist.axes.figure
        except AttributeError:
            pass
        else:
            if figure and (t_figure is not figure):
                raise ValueError("All the ``Artists`` must belong to the same Figure.")
            figure = t_figure
    if figure is None:
        ValueError("No figure is found.")
    return figure


def get_artist_pairs(fig):
    """Return Artists.

    Returns: `list` of pair, (Artist, has_child).
        has_child (bool):
    """
    result = list()

    def _inner(artist):
        children = artist.get_children()
        has_child = True if children else False
        for child in children:
            _inner(child)
        pair = (artist, has_child)
        result.append(pair)

    _inner(fig)
    return result
