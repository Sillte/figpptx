# Tutorial

## Introduction 
In tutorial pages, I'd like to introduce usage 
of ``figpptx`` and how to extend functionality
of this library.  

I feel it is sufficient for most users 
to only know ``send`` and ``rasterize`` functions.
To know basic usage, please read to the following page.  

* [Basic Usage](./basic.md)

I hope simple calls of these functions become helpful to you.
Nevertheless, it may not satisfy your requirements.
Especially, default settings of ``send`` function reflects 
tastes of the author strongly, so it may contradict against 
your desires. 

If you feel improvements or modification are required for each case, 
please modify them to your advantages.  
First of all, [Overview of Design](../concept/index.md) is helpful for customization.

In short, 

* When you want to modify **how** an Artists is converted to ``PowerPoint Object``,  you change ``Converters``.
* When you want to modify **what** Artist are converted as ``PowerPoint Object``, you change  ``Separator``.  

I'd like to leave some sample codes for extension.  

* [Separator Example](separator.md)
* [Converter Example](converter.md)


### Afterword   

Intrinsically, conversion from ``matplotlib`` to ``PowerPoint Object`` is 
almost impossible to pursue perfection. 
Even if it is possible, I think the cost of them does not match the benefit. 
Instead, I believe that mechanism where users can modify the library to their tastes are more practical and useful,  
so I wrote this kind of document.  

