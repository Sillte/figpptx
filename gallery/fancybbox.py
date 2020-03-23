import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from figpptx.comparer import Comparer

class TextConverter:
    """Get the feel of texts. 

    Ref: https://matplotlib.org/gallery/shapes_and_collections/fancybox_demo.html#sphx-glr-gallery-shapes-and-collections-fancybox-demo-py
    """

    @classmethod
    def run(cls, fig):
        fig, ax = plt.subplots()
        fig = TextConverter.gallery(fig)
        Comparer().compare(fig)

    @classmethod
    def gallery(cls, fig):
        fontsize = 0.3 * 72
        spacing = 1.2
        styles = mpatch.BoxStyle.get_styles()

        figheight = spacing * len(styles) + 0.5
        fontsize = 0.3 * 72
        fig.set_size_inches(figheight, figheight)

        styles = mpatch.BoxStyle.get_styles()
        for i, stylename in enumerate(sorted(styles)):
            fig.text(
                0.5,
                (spacing * (len(styles) - i) - 0.5) / figheight,
                stylename,
                ha="center",
                size=fontsize,
                transform=fig.transFigure,
                bbox=dict(boxstyle=stylename, fc="w", ec="k"),
            )
        return fig


if __name__ == "__main__":
    fig, ax = plt.subplots()
    TextConverter.run(fig)
