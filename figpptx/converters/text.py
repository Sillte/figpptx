import matplotlib.pyplot as plt
import matplotlib

from figpptx import ConverterManager
from figpptx import constants  # Definition of constants.
from figpptx import conversion_misc
from figpptx.converters import fancybox


@ConverterManager.register(matplotlib.text.Text)
def text_converter(slide_editor, artist):
    patch = artist.get_bbox_patch()
    if patch:
        shape = fancybox.fancybbox_converter(slide_editor, patch)
    else:
        box = slide_editor.get_box(artist)
        shape = slide_editor.slide.Shapes.AddTextBox(
            constants.msoTextOrientationHorizontal, **box
        )

    shape.TextFrame.TextRange.Text = artist.get_text()
    # shape.TextFrame.Autosize = False
    shape.TextFrame.Textrange.Font.Size = artist.get_fontsize()
    # shape.TextFrame.MarginLeft = 0
    # shape.TextFrame.MarginRight = 0
    # shape.TextFrame.MarginTop = 0
    # shape.TextFrame.MarginBottom = 0
    shape.TextFrame.WordWrap = constants.msoFalse

    # Itatic
    style = artist.get_style()
    if style in {"italic", "oblique"}:
        shape.TextFrame.Textrange.Font.Italic = True

    # Color
    rgb = artist.get_color()
    # Is there a place to set ``alpha``?
    rgb_int, alpha = conversion_misc.to_color_infos(rgb)
    shape.TextFrame.TextRange.Font.Color.RGB = rgb_int
    shape.Fill.Visible = False

    return shape


if __name__ == "__main__":
    # Ref: https://matplotlib.org/gallery/shapes_and_collections/fancybox_demo.html#sphx-glr-gallery-shapes-and-collections-fancybox-demo-py
    import matplotlib.patches as mpatch

    from figpptx.comparer import Comparer

    styles = mpatch.BoxStyle.get_styles()
    spacing = 1.2

    figheight = spacing * len(styles) + 0.5
    fig = plt.figure(figsize=(4 / 1.5, figheight / 1.5))
    fontsize = 0.3 * 72

    for i, stylename in enumerate(sorted(styles)):
        fig.text(
            0.5,
            (spacing * (len(styles) - i) - 0.5) / figheight,
            stylename,
            ha="center",
            size=fontsize,
            transform=fig.transFigure,
            bbox=dict(boxstyle=stylename, fc="w", ec="k"),
        )

    comparer = Comparer()
    comparer.compare(fig)
