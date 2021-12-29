# figpptx

### Introduction

**figpptx** performs conversion of artists of [matplotlib](https://matplotlib.org/) to [Shape Object (Powerpoint)](https://docs.microsoft.com/en-us/office/vba/api/powerpoint.shape). 

Suppose the situation you write a python code in order to make a presentation with PowerPoint.   
I bet many use [matplotlib](https://matplotlib.org/) (or the derivatives) for visualization.         
We have to transfer objects of matplotlib such as Figure to Slide of Powerpoint.    
It is desirable to perform this process swiftly, since we'd like to improve details of visualization based on the feel of Slide.  

I considered how to perform this chore efficiently.     
**figpptx** is written to integrate my experiments as a (somewhat) makeshift library.      


### Requirements

* Python 3.6+ (My environment is  3.8.2.)  
* Microsoft PowerPoint (My environment is Microsoft PowerPoint 2016)  
* See ``requirements.txt``.

### Install

Please clone or download this repository, and please execute below.  

```bat
python setup.py install 
```

### CAUTION!
This library uses [COM Object](https://docs.microsoft.com/en-us/windows/win32/com/the-component-object-model) for automatic operation of Powerpoint.    
Therefore, automatic operations are performed at your computer. Don't be panick!   

### Usage

In short, **rasterize** convert artists to an image while **transcribe** convert them to Objects of Powerpoint.


#### Paste the image to slide  

```python
import matplotlib.pyplot as plt
import figpptx

fig, ax = plt.subplots()
ax.plot([0, 1], [1, 0], color="C2")
figpptx.rasterize(fig)
```

#### Attempt to convert Artist to Object of Powerpoint.     

```python
import matplotlib.pyplot as plt
import figpptx

fig, ax = plt.subplots()
ax.plot([0, 1], [1, 0], color="C3")
figpptx.transcribe(fig)
```

#### Some artists are rasterized and the others are converted to Objects of PowerPoint.

```python
import matplotlib.pyplot as plt
import figpptx

fig, ax = plt.subplots()
ax.plot([0, 1], [1, 0], color="C3")
ax.set_title("Title. This is a TextBox.", fontsize=16)
figpptx.send(fig)
```

For details, please see [documents](https://sillte.github.io/figpptx/). 

### Gallery

If you would like to know difference between ``rasterize`` and ``transcribe``, please execute below. 
You can see some examples.

```bat
python gallery.py
```

### Test

#### Unit Test
```bat
python setup.py test
```

#### Regreesion Test 
```bat
pytest
```

* Tests include automatic operation of PowerPoint.    
* You must close the files of PowerPoint beforehand.   


### Comment and Policy

* This library is mainly for my personal practice.  
* It is yet highly possible to change specifications. 
* ``transcribe`` is far from perfection.
* I'd like not to pursue perfection for ``transcrbe``. 
    - I feel it takes much cost but the benefit is not so large. 
