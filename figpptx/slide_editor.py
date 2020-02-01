""" Slide Editor.
"""
import numpy as np


class SlideEditor:
    """ This Class possess all the information required for adding ``Shapes``.
    Here, the unit of coordination is ``pixel``.

    Args:
        slide: Slide Object.
        left: (the x-position of top-left corner.)
        top: (the y-position of top-left corner.)
        size: (Width, Height)
    """

    def __init__(self, slide, left, top, size):
        self.slide = slide
        self.left = left
        self.top = top
        self.size = size
        self.width, self.height = self.size

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
            data = self._inner_transform(data).reshape(-1)
            if klass is not np.ndarray:
                data = klass(data)
            return data

        assert data.shape[-1] == 2, "Last dim must 2."
        data = np.reshape(data, (-1, 2))
        return self._inner_transform(data)

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
