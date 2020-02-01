import pytest

import matplotlib.pyplot as plt
from figpptx import rasterize
from PIL import Image

def test_rasterize():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0], color="C5")
    image = Image.new("RGBA", size=(100, 100), color=(255, 0, 0, 255))
    rasterize(fig)
    rasterize(ax)
    rasterize(image)



if __name__ == "__main__":
    pytest.main([__file__])
