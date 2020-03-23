import matplotlib.pyplot as plt
import pytest
from PIL import Image
import figpptx
from matplotlib import rcdefaults
from matplotlib.figure import Figure

import figpptx
from figpptx import image_misc
from figpptx import pptx_misc
import matplotlib.patches as mpatches

from figpptx.renderers import CrudeRenderer, DummyRenderer

def test_fig_to_image():
    fig, ax = plt.subplots(dpi=72)
    ax.plot([0, 1], [1, 0], color="C2")
    text = ax.set_title("Hello, World!", fontsize=24)
    image = image_misc.to_image(fig)
    slide = pptx_misc.get_slide()
    pptx_misc.paste_image(slide, image)


if __name__ == "__main__":
    #pytest.main([__file__, "--capture=no"], )
    test_fig_to_image()


