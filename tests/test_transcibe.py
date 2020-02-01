import pytest

import matplotlib.pyplot as plt
from PIL import Image

from figpptx import transcribe


def test_trascribe():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0], color="C5")
    transcribe(fig)
    transcribe(ax)


if __name__ == "__main__":
    pytest.main([__file__])
