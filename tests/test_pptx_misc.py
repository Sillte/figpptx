from pathlib import Path

from figpptx import pptx_misc
import pytest

_this_folder = Path(__file__).parent

def _to_object_name(target):
    return target.__class__.__name__.strip("_").capitalize()

@pytest.mark.parametrize("arg", [None, _this_folder / "__get_slide__.pptx"])
def test_get_slide(arg):
    slide = pptx_misc.get_slide(arg)
    assert _to_object_name(slide) == "Slide"

@pytest.mark.parametrize("arg", [None, _this_folder / "__get_presentation__.pptx"])
def test_get_presentation(arg):
    pres = pptx_misc.get_presentation(arg)
    assert _to_object_name(pres) == "Presentation"

print("aaaa")
if __name__ == "__main__":
    print("a")
    app = pptx_misc._get_application()
    print(_to_object_name(app.ActivePresentation.Slides))
    #print(app.ActivePresentation.Close())
    ##print(app.ActiveWindow.ViewType)
    ##print(app.__dict__["_username_"])
    # pytest.main([__file__])


