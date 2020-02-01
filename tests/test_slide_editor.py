import pytest
from unittest.mock import Mock

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from figpptx.slide_editor import SlideEditor


@pytest.mark.parametrize(
    "instance, expected",
    [
        ((1, 2), (11, 58)),
        ([3, 5], [13, 55]),
        ([1, 2, 3, 5], [11, 58, 13, 55]),
        (np.array([[1, 2], [3, 5]]), np.array([[11, 58], [13, 55]])),
    ],
)
def test_transform(instance, expected):
    slide = Mock()
    left = 10
    top = 20
    size = (30, 40)
    editor = SlideEditor(slide, left=left, top=top, size=size)
    target = editor.transform(instance)
    assert np.allclose(np.array(target), np.array(expected))
    assert type(target) is type(expected)


if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
