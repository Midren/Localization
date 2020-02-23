import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import math
import numpy

fig, ax = plt.subplots(1)
ax.set_xlim(0, 600)
ax.set_ylim(0, 400)
ax.xaxis.set_major_locator(tick.MultipleLocator(50))
ax.yaxis.set_major_locator(tick.MultipleLocator(50))
ax.xaxis.set_minor_locator(tick.MultipleLocator(10))
ax.yaxis.set_minor_locator(tick.MultipleLocator(10))
room = patches.Rectangle((50, 50), 500, 300, linewidth=1, edgecolor='r', facecolor='none')
ble1 = patches.Circle((100, 200), 5, edgecolor='b')
ble2 = patches.Circle((500, 200), 5, edgecolor='b')
for i in range(1,10):
    obj = patches.Circle((100+round(0.4*i,1)*100,200),5,edgecolor="g")
    ax.add_patch(obj)
ax.add_patch(room)
ax.add_patch(ble1)
ax.add_patch(ble2)

plt.show()
