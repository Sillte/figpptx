import matplotlib.axis
from matplotlib.axes._base import _AxesBase
from collections.abc import Sequence
from figpptx.separator import SeparatorManager


# Used for internal registration system.
_roster = {}


def _to_key(klass):
    return (klass.__module__, klass.__name__)


@SeparatorManager.register("default")
class DefaultSeparator:
    """DefaultSeparator of ``figpptx``.

    This separator is prepared for `default`,
    that is, it reflects Author's experience and imagination.

    Note
    ----
    * As for ``Ticks`` / ``Axis``,  only ``label`` texts are converted as ``PowerPointObject``.

    """

    def register(klass):
        def wrapped(method):
            if isinstance(klass, Sequence):
                for elem in klass:
                    _roster[_to_key(elem)] = method
            else:
                _roster[_to_key(klass)] = method

            return method

        return wrapped

    def ax_method(self, axes):
        result = [axes.title]
        cands = ["_left_title", "_right_title"]
        for cand in cands:
            try:
                result.append(getattr(axes, cand))
            except AttributeError:
                pass
        exclude_ids = {id(elem) for elem in result}
        children = [elem for elem in axes.get_children() if id(elem) not in exclude_ids]
        return result + sum([self.dispatch(elem) for elem in children], [])

    @register((matplotlib.axis.XAxis, matplotlib.axis.YAxis))
    def axis(self, axis):
        return [axis.get_label()]

    @register((matplotlib.axis.YTick, matplotlib.axis.XTick))
    def tick(self, axis):
        return []

    def __call__(self, target):
        return self.dispatch(target)

    def dispatch(self, artist):
        if isinstance(artist, _AxesBase):
            return self.ax_method(artist)
        else:
            shape_artists = list()
            key = _to_key(type(artist))
            if key in _roster:
                shape_artists += _roster[key](self, artist)
            else:
                for child in artist.get_children():
                    shape_artists += self.dispatch(child)
            return shape_artists


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    sep = DefaultSeparator()
    result = sep(fig)
