# Extension of `transcribe`

## Introduction

`transcribe` converts `Artist` to `PowerPoint Object`.   
`ConverterManager` enables you to customize how to perform this.  

This sections explains how to extend `transcribe` function.

## Explanation

Shortly speaking, it is necessary to register a function 
to ``ConvertManager`` before you invoke ``transcribe``.

The interface is such as follows.
```python
@ConverterManager.register(matplotlib.lines.Line2D)
def line2d_converter(slide_editor, artist):
    # `artist` is an instance of `matplotlib.lines.Line2D`.
    # you have to generate ``shapes``, corresponding to ``artist``.
    return [shapes]
```

### SlideEditor
``figpptx.slide_editor.SlideEditor`` have a role to
create ``Shape Object`` of PowerPoint.
Specifically, 

1. [generation of objects] ``slide`` attributes enables accessing to ``Slide.Shapes``, which invokes ``AddShapes``. 
2. [conversion of coordination]
    - ``transform`` method converts coordination system between ``Figure`` and ``Slide``
    - Via ``get_box`` method, get ``Artist``'s position in the coordination of ``Slide``.
 

## Tutorial
Here, consider the following code snippet.
```python  
import figpptx
import matplotlib.pyplot as plt
import matplotlib
from figpptx import ConverterManager, NonHandlingException

# To reset the pre-determined function.
@ConverterManager.register(matplotlib.text.Text)
def func(slide_editor, artist):
    print(artist)
    raise NonHandlingException  # Delegate to ``CrudeRenderer``.

fig, ax = plt.subplots()
ax.axis("off")
style = "circle"
fig.text(0.5, 0.5, style, ha="center",
         size=14,
         transform=fig.transFigure,
         bbox=dict(boxstyle=style, fc="w", ec="red"))
figpptx.transcribe(fig)
```

The code above draws a text with a circle.
It is a bit inconvenient that the ``AutoShapeType`` of red circle is not ``msoShapeOval``.
Here, we see how to revise this behavior.

### Implementation

To implement this feature, we have to know the properties of ``matplotlib.text.Text`` and ``Shape``'s property. 
Firstly, look up ``matplotlib.text.Text`` and related documents and codes.   

* [https://matplotlib.org/3.1.1/_modules/matplotlib/text.html#Text](https://matplotlib.org/3.1.1/_modules/matplotlib/text.html#Text)  
* [https://matplotlib.org/3.1.1/api/text_api.html?highlight=text#matplotlib.text.Text](https://matplotlib.org/3.1.1/api/text_api.html?highlight=text#matplotlib.text.Text)  
* [https://matplotlib.org/3.1.3/api/_as_gen/matplotlib.patches.FancyBboxPatch.html](https://matplotlib.org/3.1.3/api/_as_gen/matplotlib.patches.FancyBboxPatch.html)  
* [https://matplotlib.org/3.1.3/_modules/matplotlib/patches.html#BoxStyle](https://matplotlib.org/3.1.3/_modules/matplotlib/patches.html#BoxStyle)  

Next, check VBA Reference.

* [https://docs.microsoft.com/en-us/office/vba/api/powerpoint.shapes.addshape](https://docs.microsoft.com/en-us/office/vba/api/powerpoint.shapes.addshape).   
* [https://docs.microsoft.com/en-us/office/vba/api/office.msoautoshapetype](https://docs.microsoft.com/en-us/office/vba/api/office.msoautoshapetype).   

From these surveys, we can see to get ``FancyBboxPatch``'s information via, ``get_bbox_patch``.  

What we do is as follows. 

1. Acquire the properties of ``Artist``.
2. Generate ``Shape``. 
3. Set the properties of ``Artist`` to ``Shape``.  

Though, the codes are a little bit long, 
it is possible to make a circle.  


```python  
import figpptx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import BoxStyle

from figpptx import ConverterManager, NonHandlingException
from figpptx import constants  # Definition of constants.
from figpptx import conversion_misc


@ConverterManager.register(matplotlib.text.Text)
def func(slide_editor, artist):
    patch = artist.get_bbox_patch()
    if patch is None:
        raise NonHandlingException  # Delegate to ``CrudeRenderer``.

    boxstyle = patch.get_boxstyle()
    if isinstance(boxstyle, BoxStyle.Circle):
        box = slide_editor.get_box(patch)
        # ``box`` is a dict which constains ``Left``, ``Top``, ``Width`` and ``Height``.
        shape = slide_editor.slide.Shapes.AddShape(Type=constants.msoShapeOval, **box)
        # Conversion of color format of ``Line``.
        edgecolor = patch.get_edgecolor()
        linewidth = patch.get_linewidth()
        color, transparency = conversion_misc.to_color_infos(edgecolor)
        shape.Line.ForeColor.RGB = color
        shape.Line.Transparency = transparency
        shape.Line.ForeColor.Weight = linewidth

        # Conversion of color format of ``Fill``.
        fillcolor = patch.get_facecolor()
        color, transparency = conversion_misc.to_color_infos(fillcolor)
        shape.Fill.ForeColor.RGB = color
        shape.Fill.Transparency = transparency

        # Setting Text Properties.
        shape.TextFrame.TextRange.Text = artist.get_text()
        shape.TextFrame.TextRange.Font.Size = artist.get_fontsize()
        color, _ = conversion_misc.to_color_infos(artist.get_color())
        shape.TextFrame.TextRange.Font.Color.RGB = color
        shape.TextFrame.WordWrap = constants.msoFalse
        return shape
    else:
        raise NonHandlingException  # Delegate to ``CrudeRenderer``.

fig, ax = plt.subplots(dpi=72)
ax.axis("off")
style = "circle"
fig.text(
    0.1,
    0.5,
    "circle",
    horizontalalignment="left",
    size=14,
    transform=fig.transFigure,
    bbox=dict(boxstyle=style, fc="w", ec="red"),
)

figpptx.transcribe(fig)
```

Notice that the code above is insufficient. 
For other properties, or other inputs, the format became broke. 
In addition, the setting of type of fonts is omitted.

Remind that mechanism of ``transcribe`` is uncertain and far from perfect.  
When you want steady behavior, you should use mechanism of ``rasterize``, 
or you should write ``converters`` for your situations.

  
### Comment

#### Specification of the registered Artist Class.
When ``Figure`` or ``Axes`` are given as Parameter, then the target Artist must be the children of them.
This means only if the registered Artist class is an instance  of ``Figure.get_children()`` or  ``Axes.get_children()``, 
then registered function is  invoked. 
For example, even if you register a function for ``FancyBboxPatch`` , it is not invoked in the tutorial case. 
This is because  ``FancyBboxPatch`` is not included in ``Figure.get_children`` or ``Axes.get_children()``.

