"""Renderer

Reference
---------
* https://matplotlib.org/3.1.1/api/backend_bases_api.html
"""

from matplotlib.backend_bases import RendererBase
import matplotlib.path as mpath
import numpy as np
from PIL import Image

import warnings

from figpptx import constants
from figpptx import pptx_misc


def to_color_infos(rgb):
    if len(rgb) == 4:
        alpha = rgb[3]
        rgb = rgb[:3]
    elif len(rgb) == 3:
        alpha = 1
    assert len(rgb) == 3
    rgb = tuple(map(lambda x: int(round(x * 255)), rgb))
    rgb_int = sum(rgb[index] << (8 * index) for index in range(3))
    return rgb_int, alpha


class CrudeRenderer(RendererBase):
    """Last resolution for rendering of Artist.

    Args:
        slide_editor
        slide: Slide object.
        size: 2-length (width, height)

    """

    def __init__(self, slide_editor):
        super().__init__()
        self.slide_editor = slide_editor
        self.slide = self.slide_editor.slide
        self._made_shapes = list()

    @property
    def made_shapes(self):
        """Return the generated shapes."""
        return self._made_shapes

    @property
    def height(self):
        return self.slide_editor.height

    @property
    def width(self):
        return self.slide_editor.width

    def draw_path(self, gc, path, transform, rgbFace=None):
        slide = self.slide
        msoEditingAuto = constants.msoEditingAuto
        msoSegmentLine = constants.msoSegmentLine
        msoSegmentCurve = constants.msoSegmentCurve
        msoEditingCorner = constants.msoEditingCorner
        form = None
        sx, sy = None, None
        array = None
        shapes = list()
        arrays = list()

        for index, (vertex, code) in enumerate(path.iter_segments(transform=transform)):
            # print("code", code, "vertex", vertex)
            vertex = self.slide_editor.transform(vertex)
            if (not form) and code == mpath.Path.MOVETO:
                x, y = vertex
                form = slide.Shapes.BuildFreeform(msoEditingAuto, x, y)
                array = [(x, y)]
                sx, sy = x, y
            elif form and code == mpath.Path.MOVETO:
                shape = form.ConvertToShape()
                shapes.append(shape)
                arrays.append(array)
                array = None

                x, y = vertex
                form = slide.Shapes.BuildFreeform(msoEditingAuto, x, y)
                array = [(x, y)]
                sx, sy = x, y

            elif code == mpath.Path.CLOSEPOLY:
                """You must not use vertex when code is 79."""
                x, y = vertex
                form.AddNodes(msoSegmentLine, msoEditingAuto, sx, sy)
                shape = form.ConvertToShape()
                shapes.append(shape)
                arrays.append(array)
                array = None
                form, sx, sy = None, None, None
            elif code == mpath.Path.STOP:
                assert False, "Not expected."
                shape = form.ConvertToShape()
                shapes.append(shape)
                arrays.append(array)
                array = None
                form, sx, sy = None, None, None
            elif code == mpath.Path.LINETO:
                assert len(vertex) == 2
                x, y = vertex
                form.AddNodes(msoSegmentLine, msoEditingAuto, x, y)
                array.append((x, y))
            elif code == mpath.Path.CURVE3:
                x, y, x1, y1 = vertex
                form.AddNodes(msoSegmentCurve, msoEditingCorner, x, y, x1, y1)
                array.append((x, y))
            elif code == mpath.Path.CURVE4:
                x, y, x1, y1, x2, y2 = vertex
                form.AddNodes(msoSegmentCurve, msoEditingCorner, x, y, x1, y1, x2, y2)
                array.append((x, y))
            else:
                raise ValueError("...", "code", code)
        if form is not None:
            shape = form.ConvertToShape()
            shapes.append(shape)
            arrays.append(array)
            form, sx, sy = None, None, None
            array = None

        assert len(shapes) == len(arrays)
        for shape, array in zip(shapes, arrays):
            if rgbFace is None or len(array) <= 2:
                shape.Fill.Visible = False
            else:
                int_rgb, alpha = to_color_infos(rgbFace)
                shape.Fill.ForeColor.RGB = int_rgb
                shape.Fill.Transparency = 1 - alpha
                shape.Fill.Visible = constants.msoTrue

            line_weight = gc.get_linewidth()
            shape.Line.Weight = line_weight
            if not line_weight:
                shape.Line.Visible = constants.msoFalse
            else:
                shape.Line.Visible = constants.msoTrue
            int_rgb, alpha = to_color_infos(gc.get_rgb())
            shape.Line.ForeColor.RGB = int_rgb
            shape.Line.Transparency = 1 - alpha


        # make a Group.
        if 1 < len(shapes):
            for index, shape in enumerate(shapes):
                if index == 0:
                    shape.Select(True)
                shape.Select(False)
            shape = self.slide.Application.ActiveWindow.Selection.ShapeRange.Group()

        self._made_shapes.append(shape)

    def draw_image(self, gc, x, y, im, transform=None):
        image = Image.fromarray(im[::-1, ...])
        slide = self.slide_editor.slide
        width, height = self.slide_editor.size
        x, y = self.slide_editor.transform([x, y])
        x, y = x, y - image.height
        shape = pptx_misc.paste_image(slide, image, left=x, top=y)
        self._made_shapes.append(shape)

    def draw_gouraud_triangle(self, gc, points, colors, transform):
        """
        Tries to draw Gourand Triangle, however cannot...

        Note
        ----
        (2020-01-23) I feel it is impossible to
        gourand - triangles.
        Hence, instread of using gradation,
        the average color is used as a substitute.
        """

        warnings.warn(
            "Draw of ``Gourand Triangle`` does not work correctly.", UserWarning
        )

        def _make_triangle(slide, points):
            sx, sy = points[0]
            form = slide.Shapes.BuildFreeform(constants.msoEditingAuto, sx, sy)
            x, y = points[1]
            form.AddNodes(constants.msoSegmentLine, constants.msoEditingAuto, x, y)
            x, y = points[2]
            form.AddNodes(constants.msoSegmentLine, constants.msoEditingAuto, x, y)
            form.AddNodes(constants.msoSegmentLine, constants.msoEditingAuto, sx, sy)
            shape = form.ConvertToShape()
            return shape

        points = transform.transform(points)
        points = np.array(self.slide_editor.transform(points))
        color = np.mean(colors, axis=0)
        int_rgb, alpha = to_color_infos(color)

        slide = self.slide_editor.slide
        shape = _make_triangle(slide, points)
        shape.Fill.ForeColor.RGB = int_rgb
        shape.Fill.Transparency = 1 - alpha
        shape.Fill.Visible = constants.msoTrue
        shape.Line.Visible = constants.msoFalse

        self._made_shapes.append(shape)

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        # I do not understand why ``y`` is minus...
        y = -y + prop.get_size()
        x, y = self.slide_editor.transform((x, y))
        # msoTrue = -1
        msoFalse = 0
        ppAutoSizeShapeToFitText = 1
        msoTextOrientationHorizontal = 1
        arg_dict = {
            "Left": x,
            "Top": y,
            "Width": 100,
            "Height": 100,
            "Orientation": msoTextOrientationHorizontal,
        }
        shape = self.slide.Shapes.AddTextbox(**arg_dict)
        shape.TextFrame.TextRange.Text = s
        shape.TextFrame.AutoSize = ppAutoSizeShapeToFitText
        shape.TextFrame.TextRange.Font.Size = prop.get_size()
        shape.TextFrame.MarginLeft = 0
        shape.TextFrame.MarginRight = 0
        shape.TextFrame.MarginTop = 0
        shape.TextFrame.MarginBottom = 0
        shape.TextFrame.WordWrap = msoFalse

        # Itatic
        style = prop.get_style()
        if style in {"italic", "oblique"}:
            shape.TextFrame.Textrange.Font.Italic = True

        # Color
        rgb = gc.get_rgb()
        # Is there a place to set ``alpha``?
        rgb_int, alpha = to_color_infos(rgb)
        shape.TextFrame.TextRange.Font.Color.RGB = rgb_int
        shape.Fill.Visible = False

        # Rotation.
        pivot = (shape.Left, shape.Top + shape.Height)
        _rotate_offset(shape, angle, pivot)

        self._made_shapes.append(shape)


def _rotate_offset(shape, angle, pivot):
    """
    Rotate ``shape`` `angle` degrees
    clockwise along ``pivot.

    Args:
        angle:
            degree.
        pivot:
            (`x`, `y`), pivot of the rotation.
    """
    if angle == 0:
        return
    cx = shape.Left + shape.Width / 2
    cy = shape.Top + shape.Height / 2

    theta = -angle / 180 * np.pi  # Sign of angle.

    # Rotation matrix.
    rotmat = np.array(
        [[np.cos(theta), -np.sin(theta)], [+np.sin(theta), np.cos(theta)]]
    )
    px, py = pivot
    # Pivot's position after Rotation.
    tx, ty = rotmat @ np.array([px - cx, py - cy]) + np.array([cx, cy])
    # Pivot is equal in before and after.
    shape.Left += px - tx
    shape.Top += py - ty
    shape.Rotation = -angle  # Sign of angle.

    """ # A candidate of code.
    However, it is a little diffuclt.
    rotmat = np.array([[1 - np.cos(theta), + np.sin(theta) ],
                       [- np.sin(theta),  1 - np.cos(theta)]])
    px, py = pivot
    tx, ty = rotmat @ np.array([px - cx, py - cy])
    shape.Left += tx
    shape.Top += ty
    shape.Rotation = - angle  # Definition of Rotation.
    """


class DummyRenderer(RendererBase):
    """Dummy Renderer.
    This class is used for calling of the ``Figure/Axes`` draw
    so that adjustement functions are called according to settings.

    Ref:
    * https://matplotlib.org/3.1.1/api/backend_bases_api.html?highlight=renderer%20draw_path_collection#matplotlib.backend_bases.RendererBase  # NOQA
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        super().__init__()

    def draw_path(self, gc, path, transform, rgbFace=None):
        pass

    def draw_image(self, gc, x, y, im, transform=None):
        pass

    def draw_gouraud_triangle(self, gc, points, colors, transform):
        pass

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        pass

    def draw_markers(self, gc, marker_path, marker_trans, path, trans, rgbFace=None):
        pass

    def draw_path_collection(
        self,
        gc,
        master_transform,
        paths,
        all_transforms,
        offsets,
        offsetTrans,
        facecolors,
        edgecolors,
        linewidths,
        linestyles,
        antialiaseds,
        urls,
        offset_position,
    ):
        pass

    def draw_quad_mesh(
        self,
        gc,
        master_transform,
        meshWidth,
        meshHeight,
        coordinates,
        offsets,
        offsetTrans,
        facecolors,
        antialiased,
        edgecolors,
    ):
        pass
