import matplotlib
import matplotlib.lines
from matplotlib.transforms import TransformedPath
from figpptx.converter_manager import ConverterManager
from figpptx.converter_manager import NonHandlingException
from figpptx import constants


def hexcode_to_rgb(hex_code):
    assert hex_code[0] == "#"
    hs = tuple(map(lambda s: "".join(s), zip(*[iter(hex_code[1:])] * 2)))
    rgb = tuple(map(lambda s: int(s, 16), hs))
    return rgb


def rgb_to_int(rgb):
    rgb = tuple(map(lambda x: round(x * 255), rgb))
    return sum(rgb[index] << (8 * index) for index in range(3))


def _get_display_coordination(artist):
    """
    Ref: matplotlib.lines.Line2D.contains
    It is intended to transform the coordination system
    to ``display``.
    Is it really necessary?
    """
    transformed_path = TransformedPath(artist.get_path(), artist.get_transform())
    path, affine = transformed_path.get_transformed_path_and_affine()
    path = affine.transform_path(path)
    xy = path.vertices
    return xy


@ConverterManager.register(matplotlib.lines.Line2D)
def line2d_converter(slide_editor, target):
    if len(target.get_xdata()) != 2:
        raise NonHandlingException("Only simple line is handled.")

    slide = slide_editor.slide
    alpha = target.get_alpha()
    color = target.get_color()
    rgb = matplotlib.colors.to_rgb(color)
    display_data = _get_display_coordination(target)
    data = slide_editor.transform(display_data)
    x_data, y_data = data[:, 0], data[:, 1]
    shape = slide.Shapes.Addline(x_data[0], y_data[0], x_data[1], y_data[1])
    shape.Line.ForeColor.RGB = rgb_to_int(rgb)
    shape.Line.Weight = target.get_linewidth()
    shape.Line.Visible = constants.msoTrue
    
    if alpha is not None:
        shape.Line.Transparency = 1 - alpha

    # ``linestyle`` / ``dash_capstyle``.
    def _linestyle_converter(shape, target):
        # Ref: https://matplotlib.org/3.1.1/_modules/matplotlib/lines.html#Line2D.set_linestyle
        # Ref: https://docs.microsoft.com/ja-jp/office/vba/api/office.msolinedashstyle
        linestyle = target.get_linestyle()
        dash_capstyle = target.get_dash_capstyle()
        msoLineSolid = 1
        msoLineDash = 4
        msoLineDashDot = 5
        msoLineSquareDot = 2
        msoLineRoundDot = 3
        if linestyle in {"-", "solid"}:
            shape.Line.DashStyle = msoLineSolid
        elif linestyle in {"--", "dashed"}:
            shape.Line.DashStyle = msoLineDash
        elif linestyle in {"-.", "dashdot"}:
            shape.Line.DashStyle = msoLineDashDot
        elif linestyle in {":", "dotted"}:
            if dash_capstyle == "round":
                # This is not perfect.
                # ``LineCapStyle`` may be hint?
                shape.Line.DashStyle = msoLineRoundDot
            elif dash_capstyle == "butt":
                shape.Line.DashStyle = msoLineSquareDot
            elif dash_capstyle == "projecting":
                # This is experimental.
                # With no confidence.
                shape.Line.DashStyle = msoLineSquareDot | 8

    _linestyle_converter(shape, target)
    return [shape]


if __name__ == "__main__":
    pass
