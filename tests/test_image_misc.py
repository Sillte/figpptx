import matplotlib.pyplot as plt
import pytest
from PIL import Image
import figpptx
from matplotlib import rcdefaults


def test_fig_to_image():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0], color="C2")
    text = ax.set_title("Hello, World!", fontsize=16)
    figpptx.send(fig, match=text)


if __name__ == "__main__":
    pytest.main([__file__])


