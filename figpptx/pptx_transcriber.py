""" Transcribe ``matplotlib.figure`` to slide of ``Powerpoint``.


Note
------
(2020-02-29)
You should cache ``CrudeRender``.
"""

import warnings
import matplotlib
from collections.abc import Collection
from matplotlib.axes._base import _AxesBase
from matplotlib.artist import Artist

from figpptx.renderers import CrudeRenderer, DummyRenderer
from figpptx.slide_editor import SlideEditor
from figpptx.converter_manager import ConverterManager
from figpptx.converter_manager import NonDisplayException, NonHandlingException


class PPTXTranscriber:
    """ Transcribe of objects of ``matplotlib`` to
    Args:
        slide:
        left:
        right:
    """

    def __init__(self, slide, left=None, top=None):
        # [TODO] ``handling of ``None`` of ``left`` and ``top`` should be revised.
        if left is None:
            left = 0
        if top is None:
            top = 0
        self.slide = slide
        self.left = left
        self.top = top

    def transcribe(self, artist, parent_figure=None):
        # [TODO] You should revise this so that calling ``_apply_dummy_reander`` should be 1.
        if isinstance(artist, Collection):
            result = list()
            for elem in artist:
                result += self.transcribe(elem, parent_figure=parent_figure)
            return result

        # If parent_figure is not given, infer.
        if parent_figure is None:
            parent_figure = _to_figure(artist)
        self._apply_dummy_render(parent_figure)

        if isinstance(artist, matplotlib.figure.Figure):
            return self._transcribe_figure(artist)
        elif isinstance(artist, _AxesBase):
            return self._transcribe_axis(artist)
        elif isinstance(artist, Artist):
            return self._transcribe_artist(artist, parent_figure)
        raise ValueError(f"``artist``, {type(artist)} cannot be handled.")

    def _apply_dummy_render(self, fig):
        """Apply rendering using `Null` Renderer,

        I am uncertain whether it is necessary,
        in order to invoke events which assumed to
        happen when ``matplotlib.figure.Figure.draw`` is called.
        """
        width, height = _get_pixel_size(fig)
        dummy_renderer = DummyRenderer(width, height)
        try:
            fig.draw(dummy_renderer)
        except ValueError as e:
            print(e)

    def _transcribe_figure(self, fig):
        """Transcribe Figure.


        This function is referred to ``matplotlib.figure.Figure.draw``.
        * https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/figure.py#L1675
        """

        artists = fig.get_children()
        artists.remove(fig.patch)  # Patch is not necessary.

        artists = sorted(
            (artist for artist in artists if not artist.get_animated()),
            key=lambda artist: artist.get_zorder(),
        )

        shapes = list()
        for artist in artists:
            if isinstance(artist, _AxesBase):
                shapes += self._transcribe_axis(artist)
            else:
                shapes += self._transcribe_artist(artist, parent_figure=fig)
        return shapes

    def _transcribe_axis(self, ax):
        """Transcribe Figure.


        This function is referred to ``matplotlib.figure.Figure.draw``.
        * https://github.com/matplotlib/matplotlib/blob/v3.1.2/lib/matplotlib/axes/_base.py#L2574
        """
        # [TODO] Is it all right? You should confirm.

        fig = _to_figure(ax)
        width, height = _get_pixel_size(fig)

        slide_editor = SlideEditor(
            self.slide, left=self.left, top=self.top, size=(width, height)
        )

        artists = ax.get_children()

        # If ``axison`` is False, ``spine`` is not drawn.
        if not (ax.axison and ax._frameon):
            for spine in ax.spines.values():
                artists.remove(spine)

        # (2020/01/08), Currently, I feel it is not necessary to call
        # ax._update_title_position(renderer)

        if not ax.axison:
            for _axis in (ax.xaxis, ax.yaxis):
                artists.remove(_axis)

        artists.remove(ax.patch)  # Patch is not necessary.
        artists = sorted(
            (artist for artist in artists if not artist.get_animated()),
            key=lambda artist: artist.get_zorder(),
        )

        shapes = list()
        for artist in artists:
            if isinstance(artist, _AxesBase):
                shapes += self._transcribe_axis(artist)
            else:
                shapes += self._transcribe_artist(artist)
        return shapes

    def _transcribe_artist(self, artist, parent_figure=None, crude_render=None):
        if parent_figure is None:
            fig = artist.axes.figure
        else:
            fig = parent_figure

        width, height = _get_pixel_size(fig)

        slide_editor = SlideEditor(
            self.slide, left=self.left, top=self.top, size=(width, height)
        )

        if crude_render is None:
            crude_renderer = CrudeRenderer(slide_editor)

        if ConverterManager.is_registered(artist):
            converter = ConverterManager.fetch(artist)
            try:
                shapes = converter(slide_editor, artist)
            except NonDisplayException:
                pass
            except NonHandlingException:
                artist.draw(crude_renderer)
                shapes = crude_renderer.made_shapes
            else:
                if shapes is None:
                    shapes = []
                    warnings.warn(
                        "Converter function should return ``list`` of ``Shapes``, not ``None``.",
                        UserWarning,
                    )
        else:
            artist.draw(crude_renderer)
            shapes = crude_renderer.made_shapes
        return shapes


def _to_figure(artist):
    """Return Figure of ``artist``.
    """
    if isinstance(artist, matplotlib.figure.Figure):
        return artist
    elif isinstance(artist, _AxesBase):
        return artist.figure
    elif isinstance(artist, Artist):
        return artist.axes.figure
    raise ValueError("Given ``artist`` is not Artist.", artist)


def _get_pixel_size(fig):
    inch_width, inch_height = fig.get_size_inches()
    dpi = fig.get_dpi()
    return (inch_width * dpi, inch_height * dpi)


if __name__ == "__main__":
    pass
