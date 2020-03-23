import figpptx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import BoxStyle

from figpptx import ConverterManager, NonHandlingException
from figpptx import constants  # Definition of constants.
from figpptx import conversion_misc


@ConverterManager.register(matplotlib.text.Text)
def func(slide_editor, artist):
    patch = artist.get_bbox_patch()
    if patch is None:
        raise NonHandlingException  # Delegate to ``CrudeRenderer``.

    boxstyle = patch.get_boxstyle()
    if isinstance(boxstyle, BoxStyle.Circle):
        # Acquire the coordinate information of ``Artist``.
        box = slide_editor.get_box(patch)

        # ``box`` is a dict which constains ``Left``, ``Top``, ``Width`` and ``Height``.
        shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeOval, **box)
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

        # Setting Text Properties.
        shape.TextFrame.TextRange.Text = artist.get_text()
        shape.TextFrame.TextRange.Font.Size = artist.get_fontsize()
        color, _ = conversion_misc.to_color_infos(artist.get_color())
        shape.TextFrame.TextRange.Font.Color.RGB = color
        shape.TextFrame.WordWrap = constants.msoFalse
        return shape
    else:
        raise NonHandlingException  # Delegate to ``CrudeRenderer``.


if __name__ == "__main__":
    fig, ax = plt.subplots(dpi=72)
    ax.axis("off")
    style = "circle"
    fig.text(
        0.1,
        0.5,
        "circle",
        horizontalalignment="left",
        size=14,
        transform=fig.transFigure,
        bbox=dict(boxstyle=style, fc="w", ec="red"),
    )

    figpptx.transcribe(fig)
