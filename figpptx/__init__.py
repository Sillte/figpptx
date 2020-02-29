""" figpptx.
"""

from figpptx.pptx_transcriber import PPTXTranscriber
from figpptx import pptx_misc
from figpptx import image_misc
from figpptx import artist_misc
from figpptx.arguments_solver import PositionSolver
from figpptx.separator import FindobjSeparator, SeparatorInterpreter

from figpptx.converter_manager import ConverterManager

# Registeration of methods related to ``ConverterManager``.
from figpptx import converters  # NOQA

# Registeration of methods related to ``SeparatorManager``.
from figpptx import separators  # NOQA


def rasterize(target, slide=None, **kwargs):
    """ Convert to ``PIL.Image``.
    and paste it to ``Slide``.

    Return: Shape.
    """
    slide = pptx_misc.get_slide(arg=slide)
    image = image_misc.to_image(target)
    left, top = PositionSolver(slide, image.size).configure(kwargs)
    shape = pptx_misc.paste_image(slide, image, left=left, top=top)

    # Post process.
    pptx_misc.select([shape])
    return shape


def transcribe(target, slide=None, **kwargs):
    """Convert to Objects of PowerPoint.

    Return: list of shapes.
    """
    kwargs = {key.lower(): value for key, value in kwargs.items()}
    slide = pptx_misc.get_slide(arg=slide)

    left = kwargs.get("left", None)
    top = kwargs.get("top", None)
    if left is None or top is None:
        image = image_misc.to_image(target)
        left, top = PositionSolver(slide, image.size).configure(kwargs)

    transcriber = PPTXTranscriber(slide, left=left, top=top)
    shapes = transcriber.transcribe(target)
    pptx_misc.select(shapes)
    return shapes


def send(target, slide=None, separator="default", match=None, **kwargs):
    """Send `target` to PowerPoint.
    """

    kwargs = {key.lower(): value for key, value in kwargs.items()}
    slide = pptx_misc.get_slide(arg=slide)

    left = kwargs.get("left", None)
    top = kwargs.get("top", None)
    if left is None or top is None:
        image = image_misc.to_image(target)
        left, top = PositionSolver(slide, image.size).configure(kwargs)

    if match is not None:
        separator = FindobjSeparator(match)

    shape_artists, image_artists = SeparatorInterpreter(separator, target).partition

    slide = pptx_misc.get_slide(arg=slide)

    image_shape = rasterize(image_artists, slide=slide, left=left, top=top)

    parent_figure = artist_misc.to_figure(target)
    transcriber = PPTXTranscriber(slide, left=left, top=top)
    shapes = transcriber.transcribe(shape_artists, parent_figure=parent_figure)

    grouped_shape = pptx_misc.group([image_shape, *shapes])
    pptx_misc.select([grouped_shape])
    return grouped_shape
