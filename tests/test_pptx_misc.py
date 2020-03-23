from pathlib import Path

from figpptx import pptx_misc
import pytest

_this_folder = Path(__file__).parent

def _to_object_name(target):
    return getattr(type(target), "__com_interface__").__name__.strip("_").capitalize()

@pytest.mark.parametrize("arg", [None, _this_folder / "__get_slide__.pptx"])
def test_get_slide(arg):
    slide = pptx_misc.get_slide(arg)
    assert _to_object_name(slide) == "Slide"

@pytest.mark.parametrize("arg", [None, _this_folder / "__get_presentation__.pptx"])
def test_get_presentation(arg):
    pres = pptx_misc.get_presentation(arg)
    assert _to_object_name(pres) == "Presentation"


if __name__ == "__main__":
    pytest.main([__file__])


