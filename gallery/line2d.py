"""Check behaviors of ``Line2D``.
"""
import numpy as np
import matplotlib.pyplot as plt
from figpptx.comparer import Comparer


class Line2DCheck:
    """Line2DCheck.

    """
    @classmethod
    def run(cls, ax):
        cls.various_line2d(ax)
        Comparer().compare(ax.figure)

    @classmethod
    def various_line2d(cls, ax):
        ax.plot([0, 1], [0, 1])
        ax.plot([0, 1, 2], [2, 3, 1])
        return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(dpi=72)
    Line2DCheck.run(ax)
