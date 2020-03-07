""" Transcribe ``matplotlib.figure`` to slide of ``Powerpoint``.


Note
------
(2020-02-29)
You should cache ``CrudeRender``.
"""

import warnings
import matplotlib
from collections.abc import Collection, Sequence
from matplotlib.axes._base import _AxesBase
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.artist import Artist

from figpptx.renderers import CrudeRenderer, DummyRenderer
from figpptx.slide_editor import SlideEditor
from figpptx import pptx_misc
from figpptx.converter_manager import ConverterManager
from figpptx.converter_manager import NonDisplayException, NonHandlingException


class PPTXTranscriber:
    """ Transcribe of objects of ``matplotlib`` to Powerpoint.
    Args:
        slide: Slide Object.
        left: unit is pixel.
        top: unit is pixel.
        offset (Artist, 2-length Sequence, or None):  
            ``offset`` is used to calibrate set the reference point.  
            If ``None``, it is assumed only the given ``Aritist`` is drawn,
            otherwise, ``offset`` is subtracted.     
            For details, please refer to ``SlideEditor``. 
    """

    def __init__(self, slide, left=None, top=None, offset=None):
        # [TODO] ``handling of ``None`` of ``left`` and ``top`` should be revised.
        if left is None:
            left = 0
        if top is None:
            top = 0
        self.slide = slide
        self.left = left
        self.top = top
        self.offset = offset

    def transcribe(self, artist):
        """Transcribe ``Arist`` to PowerPoint Objects.

        """
        # Reduce the number of ``_apply_dummy_render``.
        if isinstance(artist, Collection):
            figures = [_to_figure(elem) for elem in artist]
            figures = list({id(elem): elem for elem in figures}.values())
            for fig in figures:
                self._apply_dummy_render(fig)
            return sum([self._transcribe(elem) for elem in artist], [])
        else:
            self._apply_dummy_render(_to_figure(artist))
            return self._transcribe(artist)

    def _transcribe(self, artist):
        # Construct the class instance for conversion of coordination.
        # [TODO]: Revise so that the size is appropriate for ``Artist``, not ``Figure``.
        width, height = _get_pixel_size(_to_figure(artist))
        if self.offset is None:
            offset = artist  # Artist is the reference.
        else:
            offset = self.offset
        slide_editor = SlideEditor(self.slide, left=self.left, top=self.top, size=(width, height), offset=offset)

        if isinstance(artist, matplotlib.figure.Figure):
            return self._transcribe_figure(artist, slide_editor)
        elif isinstance(artist, matplotlib.axes.Axes):
            return self._transcribe_axis(artist, slide_editor)
        elif isinstance(artist, Artist):
            return self._transcribe_artist(artist, slide_editor)
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

    def _transcribe_figure(self, fig, slide_editor):
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
                shapes += self._transcribe_axis(artist, slide_editor)
            else:
                shapes += self._transcribe_artist(artist, slide_editor)
        return shapes

    def _transcribe_axis(self, ax, slide_editor):
        """Transcribe Axis.


        This function is referred to ``matplotlib.figure.Figure.draw``.
        * https://github.com/matplotlib/matplotlib/blob/v3.1.2/lib/matplotlib/axes/_base.py#L2574
        """
        # [TODO] Is it all right? You should confirm.

        fig = _to_figure(ax)
        width, height = _get_pixel_size(fig)

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
                shapes += self._transcribe_axis(artist, slide_editor)
            else:
                shapes += self._transcribe_artist(artist, slide_editor)
        return shapes

    def _transcribe_artist(self, artist, slide_editor):
        fig = _to_figure(artist)
        width, height = _get_pixel_size(fig)

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
                if not isinstance(shapes, Sequence):
                    if shapes is None:
                        shapes = []
                        warnings.warn(
                            "Converter function should return ``list`` of ``Shapes``, not ``None``.",
                            UserWarning,
                        )
                    elif pptx_misc.is_object(shapes):
                        shapes = [shapes]
                    else:
                        raise ValueError(
                            "``convert`` function should return Sequence of Shapes."
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
    else:
        return artist.get_figure()
    raise ValueError("Given ``artist`` is not Artist.", artist)


def _get_pixel_size(fig):
    inch_width, inch_height = fig.get_size_inches()
    dpi = fig.get_dpi()
    return (inch_width * dpi, inch_height * dpi)


if __name__ == "__main__":
    pass
