import matplotlib.pyplot as plt
from figpptx.comparer import Comparer

class AxisCheck:
    """Check of ``ax.axis("off")``.
    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(dpi=72)

    def run(self):
        self.gallery(self.ax)
        Comparer().compare(self.ax.figure)

    @classmethod
    def gallery(cls, ax):
        ax.plot([0, 1], [0, 1])
        ax.axis("off")
        return ax


if __name__ == "__main__":
    AxisCheck().run()
