import matplotlib
import numpy as np
from collections.abc import Sequence
from PIL import Image
from io import BytesIO
from contextlib import contextmanager
from matplotlib.artist import Artist
from matplotlib.axes._axes import _AxesBase


def to_image(arg, **kwargs):
    if isinstance(arg, matplotlib.figure.Figure):
        return fig_to_image(arg, **kwargs)
    elif isinstance(arg, _AxesBase):
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
    buf = BytesIO()
    fig.savefig(buf, **kwargs)
    buf.seek(0)
    image = Image.open(buf).copy()
    buf.close()
    return image


def ax_to_image(ax, is_tight=True, **kwargs):
    """ Convert ``matplotlib.Axes`` to ``PIL.Image``.
    """
    kwargs["transparent"] = kwargs.get("transparent", True)

    fig = ax.figure
    artists = fig.get_children()  # [TODO] Check ``get_axes`` is more apt?
    with _store_visibility(artists):
        for artist in artists:
            if artist is not ax:
                artist.set_visible(False)
        image = fig_to_image(fig, **kwargs)

    if is_tight:
        # bbox = image.getbbox()
        bbox = _get_bbox(image)
        if bbox:
            print(bbox)
            image = image.crop(bbox)
        """
        bbox = ax.get_tightbbox(fig.canvas.get_renderer())
        xmin, xmax = math.floor(bbox.xmin), math.ceil(bbox.xmax)
        ymin, ymax = math.floor(bbox.ymin), math.ceil(bbox.ymax)
        image = image.crop([xmin, ymin, xmax, ymax])
        """
    return image


def artists_to_image(artists, is_tight=True, **kwargs):
    if isinstance(artists, Artist):
        artists = [artists]

    if not artists:
        raise ValueError("``Empty Collection of Artists.``")
    # Check whether the all belongs to the same figure.
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

    pairs = _get_artist_pairs(figure)
    target_ids = {id(artist) for artist in artists}
    leaf_artists = [artist for artist, has_child in pairs if not has_child]
    with _store_visibility(leaf_artists):
        for artist in leaf_artists:
            if id(artist) not in target_ids:
                artist.set_visible(False)
        image = fig_to_image(figure, **kwargs)

    if is_tight:
        # bbox = image.getbbox()   # It seems not to work to my intention...
        bbox = _get_bbox(image)
        if bbox:
            print(bbox)
            image = image.crop(bbox)
    return image


def _get_artist_pairs(fig):
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


def _get_bbox(image):
    """
    Note
    -------------------------------------
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
