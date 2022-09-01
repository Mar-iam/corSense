import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from csdriver import corsense
import numpy as np

# Initialize communication with CorSense
cs = corsense()
cs.initialize()

# Initialise figure
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

# Initialise variable
xs = []
ys = []
idxs = []
temp = []


def animate(i, xs, ys, mrr, idxs):
    rr = cs.rr()[0]

    if rr > 0:
        temp.append(rr)

        if len(temp) > 10:
            medRR = np.median(temp[-9:])
            mrr = np.abs(np.diff(temp - medRR))
            idxs = np.where(mrr > 250)[0]

            # remove if consecutive
            idxs = np.delete(idxs, np.where(np.diff(idxs) == 1)[0] + 1)

            idxs = list(idxs)

            xs.append(dt.datetime.now().strftime('%S.%f'))
            ys.append(rr)

            ax.clear()
            ax.plot(xs, ys, markevery=idxs, marker='o', color='steelblue', markerfacecolor="firebrick",
                    markeredgecolor="firebrick")

        plt.xticks([])
        plt.title('RR Intervals over Time')
        plt.ylabel('RR (ms)')


anim = animation.FuncAnimation(fig, animate, fargs=(xs, ys, temp, idxs), interval=1000)

plt.show()