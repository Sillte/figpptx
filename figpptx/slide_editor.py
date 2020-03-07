""" Slide Editor.
"""
import numpy as np
from collections import UserDict
from collections.abc import Sequence
from figpptx.renderers import CrudeRenderer, DummyRenderer
from matplotlib.artist import Artist
from figpptx import artist_misc


class SlideEditor:
    """ This Class possess all the information required for adding ``Shapes``.
    Here, the unit of coordination is ``pixel``.

    Args:
        slide: Slide Object.
        left: (the x-position of top-left corner.)
        top: (the y-position of top-left corner.)
        size: (Width, Height)
        offsets: (x, y): the offsets of the transformation.
           If 2-lenght tuple is given, the units are regarded as ``pixel``in Slide.  
           If ``Artist`` is given, then

    Note
    --------------------------------------------------------------------------------
    Without SlideEditor, the position of matplotlib is based on ``Figure``.
    When artist is not ``Figure``, you should calibrate coordinations 
    in order to modify ``Artist``'s coordination with ``offsets``. 
    """

    def __init__(self, slide, left, top, size, *, offset=(0, 0)):
        self.slide = slide
        self.left = left
        self.top = top
        self.size = size
        self.width, self.height = self.size

        self.dummy_render = DummyRenderer(self.width, self.height)
        self.offset = self._to_offset(self.left, self.top, offset)
        #self.offset = np.array([0, 0])
        print("OFFSET", self.offset)

    def transform(self, data):
        """ Convert the screen coordination of ``matplolib`` to ``Slide Object``.
        Args:
            data (np.ndarray): data must be able to converted to
                             If ``data``'s dimension is 1, then
                             ``data`` is interpreted as `[x0, y0, x1, y1, x2, y2, ...]`.
                             `len(data) == 2 ` must hold.
                             If ``data``'s dimension is 2, then
                             ``data`` is interpreted as (N, 2).

        Returns:
            Return the coordinate positions after transformation.
            If ``data`` is 1D, then the type is the same as the argument ``data``.
            Otherwise, `np.ndarray` is returned.
        """
        klass = type(data)
        if klass is not np.ndarray:
            data = np.array(data)  # For efficiency.

        if data.ndim == 1:
            assert len(data) % 2 == 0, "If ``ndim`` = 1, then the length must be even."
            data = data.reshape(len(data) // 2, 2)
            data = self._inner_transform(data)
            data -= self.offset[None, :]
            data = data.reshape(-1)
            if klass is not np.ndarray:
                data = klass(data)
            return data

        assert data.shape[-1] == 2, "Last dim must 2."
        shape = data.shape
        data = np.reshape(data, (-1, 2))
        data =  self._inner_transform(data)
        data -= self.offset[None, :]
        data = data.reshape(shape)
        return data

    def get_box(self, artist):
        """Return coordination of ``Slide`` which tightly contains ``artist``.

        Return: ``dict`` which contains ``Left``, ``Top``, ``Width``, ``Height``.
        """
        bbox = artist.get_window_extent(self.dummy_render)
        # Conversion from screen-coords in matplolib to slide-coords in Powerpoint.
        vertices = self.transform(bbox)
        xmin, xmax = min(vertices[:, 0]), max(vertices[:, 0])
        ymin, ymax = min(vertices[:, 1]), max(vertices[:, 1])
        left, top, width, height = xmin, ymin, xmax - xmin, ymax - ymin
        return Box(left, top, width, height)

    def _inner_transform(self, points):
        in_x, in_y = points[..., 0], points[..., 1]
        out_x = in_x + self.left
        out_y = in_y + self.top

        """ Inversion along y-axis is required.
        """
        out_ymin = self.top
        out_ymax = self.top + self.height
        out_x, out_y = out_x, (out_ymax - (out_y - out_ymin))
        result = np.stack((out_x, out_y), axis=-1)
        return result

    def _to_offset(self, left, top, offset):
        if isinstance(offset, Artist):
            artist = offset
            fig = artist_misc.to_figure(artist)
            bbox = artist.get_window_extent(self.dummy_render)
            bbox = np.array(bbox)
            vertices = self._inner_transform(bbox) 
            xmin = min(vertices[:, 0])
            ymin = min(vertices[:, 1])
            offset = (xmin - left, ymin - top)
        assert len(offset) == 2
        return np.array(offset)



class Box(UserDict):
    """ This class keeps coordinate information.
    ``Left``, ``Top``, ``Width``, and ``Height``.
    """

    def __init__(self, left, top, width, height):
        self.data = {"Left": left, "Top": top, "Width": width, "Height": height}

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    def __getattr__(self, key):
        n_key = key.capitalize()
        if n_key in self.data:
            return self.data[n_key]
        return super().__getattribute__(key)

    @classmethod
    def union(cls, *args):
        args = cls._flatten(args)
        left = min(arg.left for arg in args)
        top = min(arg.top for arg in args)
        right = max(arg.right for arg in args)
        bottom = max(arg.bottom for arg in args)
        width = right - left
        height = bottom - top
        return Box(left, top, width, height)

    @classmethod
    def _flatten(cls, *args):
        result = []
        for arg in args:
            if isinstance(arg, Box):
                result.append(arg)
            elif isinstance(arg, Sequence):
                result += cls._flatten(*arg)
            else:
                raise ValueError("Invalid Argument.")
        return result


"""
class SlideTransformer:
    def __init__(self,
                 in_region=(0, 0, 640, 480),
                 out_region=(0, 0, 640, 480),
                 x_inversion=False,
                 y_inversion=True):
        self.y_inversion = y_inversion
        self.x_inversion = x_inversion
        self.forward = self._gen_forward(in_region, out_region)

    def _gen_forward(self, in_region, out_region):
        in_xmin, in_ymin, in_xmax, in_ymax =  in_region
        out_xmin, out_ymin, out_xmax, out_ymax =  out_region
        def _forward(in_x, in_y):
            px = in_x / (in_xmax - in_xmin) * (out_xmax - out_xmin) + out_xmin
            py = in_y / (in_ymax - in_ymin) * (out_ymax - out_ymin) + out_ymin
            return px, py

        transform = _forward
        def _invert(out_x, out_y):
            if self.y_inversion:
                out_x, out_y = out_x, (out_ymax - (out_y - out_ymin))
            if self.x_inversion:
                out_x, out_y = (out_xmax - (out_x - out_xmin)), out_y
            return out_x, out_y

        return lambda in_x, in_y: _invert(*_forward(in_x, in_y))

    def transform(self, data):
        assert len(data) % 2 == 0
        result = list()
        for x_data, y_data in zip(*[iter(data)] * 2):
            x_data, y_data = self.forward(x_data, y_data)
            result += [x_data, y_data]
        return tuple(result)
"""

if __name__ == "__main__":
    pass
