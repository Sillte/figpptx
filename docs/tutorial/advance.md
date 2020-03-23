# Advance Usage

## Introduction
I'd like to explain how to extend function of ``figpptx`` and 
make it adopt to the user's preference. 

Intrinsically, conversion from ``matplotlib`` to ``PowerPoint Object`` is 
almost impossible to pursue perfect. 
In addition, even if it is possible, I think the cost of them
does not match the benefit. 

Instead, I believe that mechanism where users can modify the library 
to their tastes are more practical and useful.  
 
In Advance Usage,  I'd like to provide some examples as simple tutorials.  
I'm happy you are interested in the library and extend it to make it your tool.


### Overview of ``figpptx``.  

* When you want to modify **how** an Artists is converted to ``PowerPoint Object``,  you change ``converter function``.
* When you want to modify **what** Artist are converted as ``PowerPoint Object``, you change  ``Separator``.  

That is the basic strategy of modification. 

I hope the following tutorials help you to get the gist of strategies for modification.

* [Extension of transcribe ](./converter.md)
    - Explains how to extend ``converter functions``.
* [Tutorial for Separator]
    - Not yet,.

