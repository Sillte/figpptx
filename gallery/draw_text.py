import matplotlib.pyplot as plt
from figpptx.comparer import Comparer

from matplotlib.axes import Axes


class TextCheck:
    """Text Check.
    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(dpi=72)

    def run(self):
        self.gallery(self.ax)
        Comparer().compare(self.ax.figure)

    @classmethod
    def gallery(cls, ax):
        ax.axis([0, 10, 0, 10])
        cls._rotation(ax)
        cls._style(ax)
        cls._color(ax)
        cls._japanese(ax)
        cls._russian(ax)
        cls._long_sentence(ax)
        return ax

    @classmethod
    def _rotation(cls, ax):
        t = "IS_OK_ROT?"
        ax.text(4, 1, t, ha="left", rotation=60, fontdict={"fontsize": 48})
        return ax

    @classmethod
    def _style(cls, ax):
        t = "IS_ITALIC_OK"
        ax.text(2, 1, t, ha="left", style="italic", fontdict={"fontsize": 36})
        return ax

    @classmethod
    def _color(cls, ax):
        t = "IS_COLOR_OK"
        ax.text(2, 4, t, ha="left", fontdict={"fontsize": 24, "color": "red"})

    @classmethod
    def _japanese(cls, ax):
        t = "占いCO 第一犠牲者●"
        ax.text(3, 3, t, ha="right")

    @classmethod
    def _russian(cls, ax):
        t = "что завтра будет хороший день!"
        ax.text(1, 2, t, fontdict={"fontsize": 12, "color": "C5"})

    @classmethod
    def _long_sentence(self, ax):
        t = (
            "Long long ago, there are siblings in a certain village."
            "They get along well and are popular among villagers. " 
            "At one day, Rumor emerges from nowhere that `Werewolves` plan to attack..."
        )
        ax.text(1, 5, t, fontsize=8, style="oblique", wrap=True)
        return ax


if __name__ == "__main__":
    TextCheck().run()
