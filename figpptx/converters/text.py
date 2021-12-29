import matplotlib.pyplot as plt
import matplotlib

from figpptx import ConverterManager
from figpptx import constants  # Definition of constants.
from figpptx.converter_manager import NonHandlingException
from figpptx import conversion_misc
from figpptx import image_misc
from figpptx import pptx_misc
from figpptx.converters import fancybox


@ConverterManager.register(matplotlib.text.Text)
def text_converter(slide_editor, artist):
    patch = artist.get_bbox_patch()
    box = slide_editor.get_box(artist)
    if artist.get_rotation() != 0:
        raise NonHandlingException

    if matplotlib.cbook.is_math_text(artist.get_text()):
        if patch:
            patch_shape = fancybox.fancybbox_converter(slide_editor, patch)
        image = image_misc.to_image(artist)
        text_shape = pptx_misc.paste_image(
            slide_editor.slide, image, left=box.Left, top=box.Top
        )
        return [patch_shape, text_shape]

    if patch:
        shape = fancybox.fancybbox_converter(slide_editor, patch)
    else:
        shape = slide_editor.slide.Shapes.AddTextbox(
            constants.msoTextOrientationHorizontal, **box
        )
        # Subtract the margin of TextFrame so that the top and left should be equivalent.
        # I feel this simple logic is not enough...
        shape.Top -= shape.TextFrame.MarginTop
        shape.Left -= shape.TextFrame.MarginLeft

    if not patch:
        shape.TextFrame.AutoSize = constants.ppAutoSizeShapeToFitText
    if artist.get_wrap():
        text = artist._get_wrapped_text()
    else:
        text = artist.get_text()
    shape.TextFrame.TextRange.Text = text
    shape.TextFrame.TextRange.Font.Size = artist.get_fontsize()
    shape.TextFrame.WordWrap = constants.msoFalse

    # Itatic
    style = artist.get_style()
    if style in {"italic", "oblique"}:
        shape.TextFrame.TextRange.Font.Italic = True

    # Color
    rgb = artist.get_color()
    # Is there a place to set ``alpha``?
    rgb_int, alpha = conversion_misc.to_color_infos(rgb)
    shape.TextFrame.TextRange.Font.Color.RGB = rgb_int

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
