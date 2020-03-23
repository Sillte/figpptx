""" Converter for FancyBbox

* https://matplotlib.org/3.1.1/gallery/shapes_and_collections/fancybox_demo.html

Note
--------------------------------------------------------------------------------
This converter is imcomplete in many ways.
Especially, ``BoxStyle``'s ``transmute`` is not reflected.
"""

import matplotlib
from functools import singledispatch
from matplotlib.patches import FancyBboxPatch, BoxStyle
from figpptx import constants  # Definition of constants.
from figpptx import conversion_misc
from figpptx import ConverterManager, NonHandlingException


def _set_commons(shape, patch):
    # Conversion of color format of ``Line``.
    edgecolor = patch.get_edgecolor()
    linewidth = patch.get_linewidth()
    color, transparency = conversion_misc.to_color_infos(edgecolor)
    shape.Line.ForeColor.RGB = color
    shape.Line.Transparency = transparency
    shape.Line.ForeColor.Weight = linewidth

    # Conversion of color format of ``Fill``.
    fillcolor = patch.get_facecolor()
    color, transparency = conversion_misc.to_color_infos(fillcolor)
    shape.Fill.ForeColor.RGB = color
    shape.Fill.Transparency = transparency
    return shape


@singledispatch
def _generate(box_style, slide_editor, patch):
    raise NonHandlingException


@_generate.register(BoxStyle.Circle)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeOval, **box)
    shape = _set_commons(shape, patch)
    return shape


@_generate.register(BoxStyle.Square)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeRectangle, **box)
    shape = _set_commons(shape, patch)
    return shape


@_generate.register(BoxStyle.Round)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(
        Type=constants.msoShapeRoundedRectangle, **box
    )
    shape = _set_commons(shape, patch)
    return shape


@_generate.register(BoxStyle.LArrow)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeLeftArrow, **box)
    shape = _set_commons(shape, patch)
    return shape


@_generate.register(BoxStyle.RArrow)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeRightArrow, **box)
    shape = _set_commons(shape, patch)
    return shape


@_generate.register(BoxStyle.DArrow)
def _(box_style, slide_editor, patch):
    box = slide_editor.get_box(patch)
    shape = slide_editor.slide.Shapes.AddShape(
        Type=constants.msoShapeLeftRightArrow, **box
    )
    shape = _set_commons(shape, patch)
    return shape


@ConverterManager.register(matplotlib.patches.FancyBboxPatch)
def fancybbox_converter(slide_editor, artist):
    box_style = artist.get_boxstyle()
    shape = _generate(box_style, slide_editor, artist)
    return shape


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from figpptx.comparer import Comparer

    styles = [
        "circle",
        "square",
        "round",
        "larrow",
        "rarrow",
        "darrow",
    ]
    # fig = plt.figure()

    fig, ax = plt.subplots()
    for i, style in enumerate(styles):
        ys = 1 / (len(styles)) * (i)
        height = 1 / (2 * len(styles))
        boxstyle = BoxStyle(style, pad=0.01)
        p_bbox = FancyBboxPatch(
            (0.2, ys), 0.3, height, boxstyle=boxstyle, ec="black", fc=f"C{i}",
        )
        ax.add_patch(p_bbox)

    fig.tight_layout()
    comparer = Comparer()
    comparer.compare(fig)
