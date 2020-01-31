import matplotlib.pyplot as plt
import figpptx

fig, ax = plt.subplots()
ax.plot([0, 1], [1, 0], label="Line") 
figpptx.rasterize(fig)
