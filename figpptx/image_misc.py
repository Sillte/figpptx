import math
import matplotlib
import numpy as np
from typing import Sequence
from PIL import Image
from io import BytesIO
from contextlib import contextmanager
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from figpptx.slide_editor import SlideTransformer, Box


def to_image(arg, **kwargs):
    if isinstance(arg, matplotlib.figure.Figure):
        return fig_to_image(arg, **kwargs)
    elif isinstance(arg, Axes):
        is_tight = kwargs.pop("is_tight", True)
        return ax_to_image(arg, is_tight, **kwargs)
    elif isinstance(arg, Artist):
        return artists_to_image(arg)
    elif isinstance(arg, Image.Image):
        return arg.copy()

    if isinstance(arg, Sequence):
        if all(isinstance(elem, Artist) for elem in arg):
            return artists_to_image(arg)
        else:
            raise ValueError("All elements must be ``Artist``.")

    raise ValueError(f"``{arg}`` cannot be converted to image.")


def fig_to_image(fig, **kwargs):
    """Convert ``matplotlib.Figure`` to ``PIL.Image``.

    Args:
        kwargs (str):
            Keyword parameters for ``Figure.savefig`` except ``fname``.
    """
    # Ref: https://stackoverflow.com/questions/8598673/how-to-save-a-pylab-figure-into-in-memory-file-which-can-be-read-into-pil-image/8598881  # NOQA

    kwargs["format"] = kwargs.get("format", "png")
    kwargs["transparent"] = kwargs.get("transparent", True)
    buf = BytesIO()
    fig.savefig(buf, **kwargs)
    buf.seek(0)
    image = Image.open(buf).copy()
    buf.close()
    return image


def ax_to_image(ax, is_tight=True, **kwargs):
    """Convert ``matplotlib.Axes`` to ``PIL.Image``."""

    kwargs["transparent"] = kwargs.get("transparent", True)

    fig = ax.figure
    artists = fig.get_children()  # [TODO] Check ``get_axes`` is more apt?
    with _store_visibility(artists):
        for artist in artists:
            if artist is not ax:
                artist.set_visible(False)
        image = fig_to_image(fig, **kwargs)

    if is_tight:
        image = _crop_image(image, ax)

        bbox = ax.get_tightbbox(fig.canvas.get_renderer())
        xmin, xmax = math.floor(bbox.xmin), math.ceil(bbox.xmax)
        ymin, ymax = math.floor(bbox.ymin), math.ceil(bbox.ymax)
        image = image.crop([xmin, ymin, xmax, ymax])
    return image


def artists_to_image(artists, is_tight=True, **kwargs):
    if isinstance(artists, Artist):
        artists = [artists]

    if not artists:
        raise ValueError("``Empty Collection of Artists.``")
    # Check whether the all belongs to the same figure.
    figures = [artist.get_figure() for artist in artists]
    figures = [figure for figure in figures if figure]
    figures = set(figures)
    if not figures:
        raise ValueError("Figure does not exist.")
    elif 1 < len(figures):
        ValueError("All the ``Artists`` must belong to the same Figure.")
    figure = list(figures)[0]

    target_pairs = sum([_get_artist_pairs(artist) for artist in artists], [])
    target_ids = {id(pair[0]) for pair in target_pairs}
    pairs = _get_artist_pairs(figure)
    leaf_artists = [artist for artist, has_child in pairs if not has_child]
    with _store_visibility(leaf_artists):
        for artist in leaf_artists:
            if id(artist) not in target_ids:
                artist.set_visible(False)
        image = fig_to_image(figure, **kwargs)

    if is_tight:
        image = _crop_image(image, artists)

    return image


def _get_artist_pairs(root):
    result = list()

    def _inner(artist):
        children = artist.get_children()
        has_child = True if children else False
        for child in children:
            _inner(child)
        pair = (artist, has_child)
        result.append(pair)

    _inner(root)
    return result


def _get_bbox(image):
    """
    (2020-01-12)
    ``Image.getbbox()`` does not seem to work intendedly. (Really?)
    So, substitution is implemented.
    """

    assert image.mode == "RGBA"
    width, height = image.size
    array = np.array(image)
    alpha = array[:, :, -1]
    ys, xs = np.where(alpha != 0)
    xmin, xmax = np.min(xs) - 1, np.max(xs) + 1
    ymin, ymax = np.min(ys) - 1, np.max(ys) + 1
    xmin = np.clip(xmin, 0, width)
    xmax = np.clip(xmax, 0, width)
    ymin = np.clip(ymin, 0, height)
    ymax = np.clip(ymax, 0, height)
    return xmin, ymin, xmax, ymax


def _crop_image(fig_image, artist):
    """Crop the ``fig_image`` so that only ROI of ``target`` remains."""
    width, height = fig_image.size

    from figpptx import artist_misc

    transformer = SlideTransformer(0, 0, size=(width, height), offset=(0, 0))
    if isinstance(artist, Axes):
        fig = artist_misc.to_figure(artist)
        renderer = fig.canvas.get_renderer()
        bbox = artist.get_tightbbox(renderer)
        vertices = transformer.transform(bbox)
        box = Box.from_vertices(vertices)
    elif isinstance(artist, Artist):
        box = transformer.get_box(artist)
    elif isinstance(artist, Sequence):
        boxes = [transformer.get_box(elem) for elem in artist]
        box = Box.union(boxes)
    else:
        raise ValueError("Argument Error.", artist)

    xmin, xmax = math.floor(box.left), math.ceil(box.left + box.width)
    ymin, ymax = math.floor(box.top), math.ceil(box.top + box.height)
    xmin, xmax = max(0, xmin), min(xmax, width - 1)
    ymin, ymax = max(0, ymin), min(ymax, height - 1)
    image = fig_image.crop([xmin, ymin, xmax + 1, ymax + 1])
    return image


@contextmanager
def _store_visibility(artists):
    stored = dict()

    for artist in artists:
        stored[id(artist)] = artist.get_visible()

    def _restore():
        for artist in artists:
            artist.set_visible(stored[id(artist)])

    try:
        yield
    except Exception as e:
        _restore()
        raise e
    else:
        _restore()


if __name__ == "__main__":
    pass
