"""Micellaneous functions used for ``converter``.

This module gathres utility functions used at conversion
from ``matplotlib`` to ``PowerPoint``.


Implementation Policy
----------------------

Returned properties of this function are expected to correspond
to Object properties.

For example, ``to_color_info`` returns ``Transparency``, not ``alpha``.
This is because

"""
import matplotlib.colors as mcolors
from matplotlib.artist import Artist
from figpptx import image_misc
from figpptx import pptx_misc
from figpptx.slide_editor import Box


def to_color_infos(rgb):
    """ From color of ``matplotlib`` to one of PowerPoint.
    Args:
        rgb: color represented in ``matplotlib`` format.

    Returns: 2-tuple.  (rgb_int, transparency).
        `rgb_int` is expected to ``RGB.Color`` of PowerPoint Object.
        `transparency ` corresponds to  `RGB.Transparency`.
    """
    rgba = mcolors.to_rgba(rgb)
    rgb, alpha = rgba[:3], rgba[3]
    rgb = tuple(map(lambda x: int(round(x * 255)), rgb))
    rgb_int = sum(rgb[index] << (8 * index) for index in range(3))
    transparency = 1 - alpha
    return rgb_int, transparency


def to_image_shape(slide_editor, artists):
    """ Convert ``artist`` to ``Shape`` as ``PIL.Image``.

    Note
    ----------------------------------
    This function takes a long time especially when
    there are many aritists in figure of the the ``artist``.
    This function is expected to be called only a few.
    """
    if isinstance(artists, Artist):
        artists = [artists]
    boxes = [slide_editor.get_box(artist) for artist in artists]
    box = Box.union(boxes)
    # box = slide_editor.get_box(artist)
    image = image_misc.to_image(artists)
    shape = pptx_misc.paste_image(slide_editor.slide, image)
    print("box", box)
    for key, value in box.items():
        setattr(shape, key, value)
    return shape
