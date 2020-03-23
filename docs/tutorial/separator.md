# Setting of Separator.  

## Introduction 
 
``send`` function converts some ``Artists``  with `transcribe`
while the others with ``rasterize``.  

To specify classify ``Artists`` to these two categories, 
``separator`` is  used. 
By defining a ``separator``, you can customize this classification.   


The example of ``separator`` is as follows.  
```python
@SeparatorManager.register("register_key")
def sample_separator(artist):
    # when you use the string ``register_key`` as ar parameter of ``separator``, you can use this function.      
    # As a parameter, the target ``Artist`` is given, which is the same as the parameter of ``send``.
    # If the function returns 2-length tuple,
    #    the first is used for ``transcribe``, the second is used for ``rasterize``.
    # If only 1 Sequence of ``Artists`` is returned, then it is regarded as ``shape_artists`` , 
    # and ``image_artists`` is assumed to be the complement set.

    return shape_artists
    # or
    #return (shape_artists, image_artists)
```


## Tutorial

Here, consider the following snippet.

```python
import numpy as np
import matplotlib.pyplot as plt 
import figpptx
fig, ax = plt.subplots()
x = np.arange(-5, +5, step=0.01)
y = 1 / 2 * x ** 2
ax.plot(x, y)
annotation = ax.annotate("Minimum", xy = (0, 0), xycoords='data', xytext=(0, 5), arrowprops=dict(arrowstyle="->"))
figpptx.send(fig, separator="rasterize")
```

This code converts a figure to an image.  
Here, we would like to pass ``annotation`` to ``transcibe``. 
As you can imagine, it is all correct to implement a simple `separator`.   

```python
import figpptx
import numpy as np
import matplotlib.pyplot as plt 
fig, ax = plt.subplots()
x = np.arange(-5, +5, step=0.01)
y = 1 / 2 * x ** 2
ax.plot(x, y)
annotation = ax.annotate("Minimum", xy = (0, 0), xycoords='data', xytext=(0, 5), arrowprops=dict(arrowstyle="->"))

def separator(artist):
    return [annotation]
figpptx.send(fig, separator=separator)
```

If we want a more sophisticated one, then the following is one example.   
```
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.text import Annotation
import figpptx
from figpptx.separator import SeparatorManager, get_leaf_artists

fig, ax = plt.subplots()
x = np.arange(-5, +5, step=0.01)
y = 1 / 2 * x ** 2
ax.plot(x, y)
annotation = ax.annotate("Minimum", xy = (0, 0), xycoords='data', xytext=(0, 5), arrowprops=dict(arrowstyle="->"))

@SeparatorManager.register("my-separator")
def separator(artist):
    matchfunc = lambda artist: isinstance(artist, Annotation)
    return get_leaf_artists(artist, matchfunc)

figpptx.send(fig, separator="my-separator")
```

