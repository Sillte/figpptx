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


if __name__ == "__main__":
    pass
