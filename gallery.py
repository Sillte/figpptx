"""Gather methods/functions and perform display. 

For all the methods and functions which can provide
examples of ``Figure`` and `` Axes``, 
make slides and let developers to confirm the results.


Note:
    The specification of targets are as follows:
    * The required arugments must be one and its name is ``fig`` or ``ax``.
    * They are classmethods.
    * They are NOT private. 

```python
class SampleClass:
    @classmethod
    def sample1(cls, fig):
        pass

    @classmethod
    def sample2(cls, fig):
        pass
```


"""
import importlib
import inspect
from pathlib import Path
import matplotlib.pyplot as plt

from figpptx import pptx_misc
from figpptx import constants
from figpptx.comparer import Comparer


def _read_arg(method, cls):
    if method.__self__ is not cls:
        raise ValueError()
    if method.__name__[0] == "_":
        raise ValueError()
    sig = inspect.signature(method)
    required_parameters = [
        p.name
        for k, p in sig.parameters.items()
        if p.default is inspect.Parameter.empty
    ]
    if len(required_parameters) != 1:
        raise ValueError()
    arg = required_parameters[0]
    return arg


def _callable_provider(path):
    """Return the info to call the target.

    Returns:
        list of (``callable``, ``arg``)

    Note:
        `arg` is str, and ``ax`` or  ``fig``.
    """
    assert path.suffix == ".py"

    spec = importlib.util.spec_from_file_location(str(path), str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    classes = inspect.getmembers(module, inspect.isclass)
    targets = list()
    for name, cls in classes:
        methods = inspect.getmembers(cls, inspect.ismethod)
        for name, method in methods:
            try:
                arg = _read_arg(method, cls)
            except ValueError:
                pass
            else:
                targets.append((method, arg))
    return targets


class GalleryExecutor:
    """Gather the sample scripts and execute it.
    """

    slide = None

    def __init__(self, slide=None):
        self.slide = None

    @classmethod
    def execute(cls, folders):
        if isinstance(folders, (str, Path)):
            folders = [Path(folders)]
        folders = [Path(folder) for folder in folders]
        files = sorted(sum((list(folder.glob("*.py")) for folder in folders), []))
        pairs = sum([_callable_provider(f) for f in files], [])
        for method, arg in pairs:
            cls._next_slide()
            cls._make_comparison(cls.slide, method, arg)

    @classmethod
    def _make_comparison(cls, slide, method, arg):
        comparer = Comparer(slide)
        fig, ax = plt.subplots(dpi=72)
        arg_object = cls._convert(arg, fig, ax)
        method(**{arg: arg_object})

        # [TODO] Corrently, only figure is considered as the argument of ``Comparer``.
        comparer.compare(fig)
        plt.close(fig)

    @classmethod
    def _next_slide(cls):
        if cls.slide is None:
            slide = pptx_misc.get_slide()
            cls.slide = slide
            return slide
        slide = pptx_misc.get_slide(cls.slide)
        slide_index = slide.SlideIndex
        slides = slide.Parent.Slides
        slide = slides.Add(slide_index + 1, constants.ppLayoutBlank)
        cls.slide = slide
        return slide

    @classmethod
    def _convert(cls, arg: str, fig, ax):
        if arg == "fig":
            return fig
        elif arg == "ax":
            return ax
        raise ValueError(f"Cannnot handle arg ``{arg}``.")


if __name__ == "__main__":
    GalleryExecutor.execute(["gallery"])
