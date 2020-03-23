""" Renderer.draw_gouraud_triangle.

"""
import numpy as np
import matplotlib.pyplot as plt
from figpptx.comparer import Comparer


class PColorMeshCheck:
    """PColorMeshCheck.

    Especially, when ``shading`` is ``gouraud``,
    ``draw_gouraud_triangle`` is called.
    I'd like to check behavior.

    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(dpi=72)

    def run(self):
        self.gourand_mode(self.ax)
        Comparer().compare(self.ax.figure)

    @classmethod
    def flat_mode(cls, ax):
        xx, yy = np.meshgrid(range(10), range(10))
        zz = (xx - 5) ** 2 + (yy - 5) ** 2
        ax.pcolormesh(xx, yy, zz, shading="flat")
        ax.axis("off")
        return ax

    @classmethod
    def gourand_mode(cls, ax):
        xx, yy = np.meshgrid(range(10), range(10))
        zz = (xx - 5) ** 2 + (yy - 5) ** 2
        ax.pcolormesh(xx, yy, zz, shading="gouraud")
        ax.axis("off")
        return ax


if __name__ == "__main__":
    PColorMeshCheck().run()
