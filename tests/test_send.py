import matplotlib.pyplot as plt
import pytest
from PIL import Image
from figpptx import pptx_misc
from figpptx import constants 

import figpptx

def get_typename(target):
    return pptx_misc._to_object_type(target)

def _get_empty_slide():
    slide = pptx_misc.get_slide()
    slide_index = slide.SlideIndex
    slides = slide.Parent.Slides
    slide = slides.Add(slide_index + 1, constants.ppLayoutBlank)
    return slide

def _get_shapes(slide, individual=True):
    shapes = slide.Shapes
    def _group_to_individual(shape):
        if shape.Type == constants.msoGroup:
            group_shapes = shape.GroupItems
            return [group_shapes.Item(index + 1) for index in range(group_shapes.Count)]
        return [shape]
    if individual:
        shapes = sum([_group_to_individual(shape) for shape in shapes], [])
    return shapes


def test_default():
    """Confirm default behavior of ``send``. 
    """
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 2])
    slide = _get_empty_slide()
    text = ax.set_title("TITLE TEXT")
    ax.set_xlabel("X_LABEL")
    ax.set_ylabel("Y_LABEL")
    shape = figpptx.send(fig, slide=slide)
    assert get_typename(shape) == "Shape"
    shapes = _get_shapes(slide, individual=True)
    assert {shape.Type for shape in shapes} == {constants.msoPicture, constants.msoTextBox}


def test_match():
    """Confirm behavior when ``match`` is used.
    """
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 2])
    slide = _get_empty_slide()
    text = ax.set_title("TITLE TEXT")
    shape = figpptx.send(fig, slide=slide, match=text)
    assert get_typename(shape) == "Shape"
    shapes = _get_shapes(slide, individual=True)
    assert len(shapes) == 2
    assert {shape.Type for shape in shapes} == {constants.msoPicture, constants.msoTextBox}



if __name__ == "__main__":
    #print(_get_shapes(_get_empty_slide()))
    pytest.main([__file__, "--capture=no"])
