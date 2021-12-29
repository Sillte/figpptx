""" Functions related to `PowerPoint`.

Note as a diary.
-------------------------------------------
(2020-01-11)
I'd like the function about ``PowerPoint`` to be minimum requirement
since this library is expected only to focus on conversion of data
from ``matplotlib.Figure``.
"""

import os
from pywintypes import com_error
from win32com.client import CDispatch, DispatchBaseClass
import win32com.client
from contextlib import contextmanager
from pathlib import Path
from figpptx import constants
from figpptx import win32com_misc


def get_slide(arg=None):
    """Return ``Slide`` based on ``arg``.
    It attempts to return the most appropriate.
    """
    if _is_target_object(arg, "Slide"):
        return arg

    app = _get_application()

    # * If viewing mode is not normal, then change to normal mode.
    try:
        if app.ActiveWindow.ViewType != constants.ppViewNormal:
            app.ActiveWindow.ViewType = constants.ppViewNormal
    except com_error:
        pass

    try:
        if app.ActiveWindow.Selection.SlideRange:
            return app.ActiveWindow.Selection.SlideRange.Item(1)
    except com_error:
        pass

    if not app.Presentations.Count:
        pres = get_presentation()
    else:
        pres = app.Presentations.Item(1)
    if not pres.Slides.Count:
        slide = pres.Slides.Add(1, constants.ppLayoutBlank)
    else:
        slide = pres.Slides.Item(pres.Slides.Count)
    return slide


def get_presentation(filepath=None):
    """Return ``Presentation`` based on the given ``filepath``.
    It attempts to return the most appopriate one.
    """

    app = _get_application()

    # With ``filepath``.
    if filepath:
        filepath = Path(filepath).resolve()
        for pres in app.Presentations:
            if filepath == Path(pres.FullName):
                return pres
        if filepath.exists():
            return app.Presentations.Open(str(filepath))
        pres = app.presentations.add()
        pres.Saveas(str(filepath))
        return pres

    # If ``ActivePresent`` exists. then return it.
    try:
        return app.ActivePresentation.Slides.Parent
    except com_error:
        pass
    if app.Presentations.Count:
        return app.Presentations.Item(1)

    # Last resort; add and return.
    pres = app.Presentations.Add()
    return pres


def get_slide_size(arg):
    """Return the size of slide.
    Args:
        arg: ``Slide`` or ``Presentation``
    Return:
        (width, height) (``pt`` unit.)
    """
    if _to_object_type(arg) == "Slide":
        pres = arg.Parent
    elif _to_object_type(arg) == "Presentation":
        pres = arg
    else:
        raise ValueError()
    width = pres.PageSetup.SlideWidth
    height = pres.PageSetup.SlideHeight
    return (width, height)


def _get_application():
    try:
        app = win32com.client.GetObject(Class="Powerpoint.Application")
    except com_error:
        app = win32com.client.DispatchEx("Powerpoint.Application")
    app.Visible = True
    return app


def paste_image(slide, image, left=None, top=None):
    width, height = image.size
    if left is None:
        left = 0
    if top is None:
        top = 0
    with _temporary_file(".png") as path:
        image.save(path)
        shape = slide.Shapes.AddPicture(
            path,
            constants.msoFalse,
            constants.msoTrue,
            Left=left,
            Top=top,
            Width=width,
            Height=height,
        )
    return shape


def group(shapes):
    """Make a group shape.

    As a side-effect, the selection of  shapes is over-ridden.
    """
    if not shapes:
        raise ValueError("Empty.")
    if len(shapes) == 1:
        return shapes[0]

    select(shapes)
    app = shapes[0].Application

    if app.ActiveWindow.Selection.Type != constants.ppSelectionShapes:
        raise ValueError("Selection Type is not `ppSelectionShapes`.")
    shape = app.ActiveWindow.Selection.ShapeRange.Group()
    return shape


def select(shapes):
    """Select shapes:

    As side-effects,
        1. the selection of shapes is over-ridden.
        2. Active Slide changed.
    """
    slide_ids = {_shape_to_slide(shape).SlideID for shape in shapes}
    if 1 < len(slide_ids):
        raise ValueError("Shape's Slide must be Unique.")
    slide = _shape_to_slide(shapes[0])
    pres = slide.Parent

    # Search the target window and activate it.
    for window in pres.Windows:
        if window.ViewType == constants.ppViewNormal:
            window.Activate()
            break
    else:
        raise ValueError("Cannot activate Shape's Window.")

    slide.Application.ActiveWindow.View.GotoSlide(slide.SlideIndex)
    slide.Select()
    for index, shape in enumerate(shapes):
        if index == 0:
            shape.Select(True)
        shape.Select(False)


def _to_object_type(target):
    """Return the Capitalized object type."""
    assert not isinstance(target, CDispatch)
    return target.__class__.__name__.strip("_").capitalize()
    # return getattr(type(target), "__com_interface__").__name__.strip("_").capitalize()


def is_object(target):
    """Return whether ``target`` is regarded as Powerpoint Object.
    """
    return isinstance(target, DispatchBaseClass)


def _is_target_object(target, name):
    target_name = _to_object_type(target)
    return target_name == name.capitalize()


@contextmanager
def _temporary_file(suffix=".png"):
    import tempfile
    import uuid

    filepath = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)


def _shape_to_slide(shape):
    target = shape
    while _to_object_type(target) != "Slide":
        target = target.Parent
    return target


if __name__ == "__main__":
    slide = get_slide()
