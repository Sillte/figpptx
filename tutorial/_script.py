import matplotlib.pyplot as plt
import figpptx

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1], label="Line") 
ax.set_xlabel("X-Label", fontsize=14)
ax.set_ylabel("Y-Label", fontsize=14)
ax.set_title("Title Text", fontsize=18)
figpptx.send(fig)
