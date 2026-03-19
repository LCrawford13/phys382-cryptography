import bb84
import os.path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import b92


protocol = "B92"  # Change to "BB84" or "B92".

matplotlib.rcParams.update({'font.size': 16})

graph = plt.figure()
graph, ax = plt.subplots(figsize=(7, 6))
ax.set_title(f"Error Rate Caused by an Eavesdropper\nfor the {protocol} " +
             "Protocol")
ax.set_ylabel('Error Rate (%)')
ax.set_xlabel("Number of Bits in Alice's Message")
ax.set_xscale('log')
ax.set_ylim([0, 100])

# Contains the number of bits which will be analysed at each interval.
intervals = [10, 30, 100, 1000, 10000, 100000, 1000000]
runs = 5
for n in range(runs):
    binaryNums = []
    for i in range(4):
        binaryNums.append(np.random.randint(0, 2, [intervals[-1]]))

    errors = []
    for m in range(len(intervals)):
        if protocol == "BB84":
            error = bb84.bb84Protocol(binaryNums, intervals[m])
        elif protocol == "B92":
            error = b92.b92Protocol(binaryNums, intervals[m])

        errors.append(error)

    line, = ax.plot(intervals, errors, '-x')
    line.set_label(f"Run {n + 1}")

# Limits needed so that the 25% horizontal line will end on the y-axis.
xmin, xmax = ax.get_xlim()
limits = [xmin, xmax]
ax.set_xlim(limits)

trend = 25
# This is a horizontal line at y = 25, for illustrations purposes.
line, = ax.plot(limits, np.full(2, trend), zorder = 0,
                linestyle = 'dashed', color = 'black')
line.set_label(f"{trend}%")

ax.legend()

# Determines a name for the output file automatically.
num = 1
while True:
    fileName = f"Graphs\\{protocol}_{num}"
    if os.path.isfile(f"{fileName}.pdf"):
        num += 1
    else:
        break

plt.tight_layout()
plt.savefig(f"{fileName}.pdf")
plt.savefig(f"{fileName}.png")
plt.show()
