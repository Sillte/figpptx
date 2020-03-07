from figpptx import transcribe, rasterize
from figpptx import pptx_misc
from figpptx import image_misc
from figpptx import artist_misc


class Comparer:
    """ Compare  the result of ``rasterize`` and ``transcribe``.
    Mainly, it is used for checking behaviors to
    develop ``converters`` for ``PPTXTranscriber``.
    """

    def __init__(self, slide=None):
        self._slide = slide

    @property
    def slide(self):
        return pptx_misc.get_slide(self._slide)

    def compare(self, artist):
        """ Args:
        """
        fig = artist_misc.to_figure(artist)
        fig.set_dpi(72)
        slide_size = pptx_misc.get_slide_size(self.slide)

        # To know the size of image proactively.
        image = image_misc.to_image(artist)
        left1, top1, left2, top2 = _decide_positions(slide_size, image.size)

        rasterize(artist, slide=self.slide, left=left1, top=top1)
        transcribe(artist, slide=self.slide, left=left2, top=top2)


def _decide_positions(slide_size, image_size):
    slide_width, slide_height = slide_size
    image_width, image_height = image_size
    width_margin = (slide_width / 2 - image_width) / 2
    height_margin = (slide_height - image_height) / 2
    width_margin = max(0, width_margin)
    height_margin = max(0, height_margin)

    left1, top1 = width_margin, height_margin
    left2, top2 = slide_width / 2 + width_margin, height_margin
    return left1, top1, left2, top2
