import os

import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
import matplotlib

import bb84
import b92


def lineBestFit(ax, x, y, error, col, colError, protocol):
    """
    Plots a line of best fit and shades in the error for the line of best fit.
    Errors are only applied for the y-axis.

    Parameters
    ----------
    ax : matplotlib.axes
        Axes to plot on.
    x : List of integers or floats
        Holds x-coordinates of graph to find line of best fit.
    y : List of integers or floats
        Holds y-coordinates of graph to find line of best fit..
    error : List of integers or floats
        List of y-coordinate errors.
    col : String
        Matplotlib compatible colour for the line of best fit.
    colError : String
        Matplotlib compatible colour for the shaded error region.
    protocol : String
        Conatins which protocol is being used for changing the print message.
        Either "BB84" or "B92".

    Returns
    -------
    line : matplotlib.lines.Line2D
        The line of best fit.
    fill : matplotlib.collections.FillBetweenPolyCollection
        The shaded error region.
    """
    c, m = polyfit(x, y, 1)

    cUpper, mUpper = polyfit(x, np.array(y) + np.array(error), 1)
    cLower, mLower = polyfit(x, np.array(y) - np.array(error), 1)
    mError = (mUpper - mLower) / 2
    cError = (cUpper - cLower) / 2

    print(f"Gradient of {protocol} line of best fit is {m} \u00B1 {mError}.")
    print(f"Y-intercept of {protocol} line of best fit is {c} \u00B1 " +
          f"{cError}.")

    line, = ax.plot(x, c + m * x, '-', color = col, zorder = 5)
    fill = ax.fill_between(x, cLower + mLower * x, cUpper + mUpper * x,
                           color = colError)

    return line, fill


# Contains the number of bits which will be analysed at each interval.
intervals = np.arange(10, 400, 20)
BB84Key = []  # BB84 key lengths.
BB84Error = []  # Error in key lengths.
B92Key = []  # B92 key lengths.
B92Error = []

# Number of trials to do for each bit length to determine the mean.
trials = 10000
for bits in intervals:
    meanBB84 = []
    meanB92 = []

    for i in range(trials):
        message = np.random.randint(0, 2, bits)
        bobBasis = np.random.randint(0, 2, bits)

        meanBB84.append(len(bb84.keyBB84(message, bobBasis)))
        meanB92.append(len(b92.keyB92(message, bobBasis)))

    BB84Key.append(np.mean(meanBB84))
    BB84Error.append(np.std(meanBB84))
    B92Key.append(np.mean(meanB92))
    B92Error.append(np.std(meanB92))


matplotlib.rcParams.update({'font.size': 14})

graph = plt.figure()
graph, ax = plt.subplots(figsize=(10, 5))
BB84Data = ax.errorbar(intervals, BB84Key, BB84Error, marker = "x",
                       color = "#CDA5D4", capsize = 2)
B92Data = ax.errorbar(intervals, B92Key, B92Error, marker = "x",
                      color = "lightcoral", capsize = 2)

ax.set_title("Length of Keys in Relation to Increasing Number of " +
             "Initial Bits\nfor the BB84 and B92 Protocols" +
             f" for {trials} Trials per Key")
ax.set_ylabel('Key Length in Bits')
ax.set_xlabel('Number of Bits in Alice\'s Message')

# Adds lines of best fit and gradients to second plot.
BB84Line, BB84Fill = lineBestFit(ax, intervals, BB84Key, BB84Error,
                                 "purple", "#FEF2FF", "BB84")
B92Line, B92Fill = lineBestFit(ax, intervals, B92Key, B92Error,
                               "red", "mistyrose", "B92")

BB84Data.set_label("BB84 Data")
BB84Line.set_label("BB84")
BB84Fill.set_label("BB84 Error")
B92Data.set_label("B92 Data")
B92Line.set_label("B92")
B92Fill.set_label("B92 Error")

# Get handles and labels.
handles, labels = plt.gca().get_legend_handles_labels()
# Specify order of items in legend.
order = [0, 1, 4, 2, 3, 5]
ax.legend([handles[i] for i in order], [labels[i] for i in order])

# Determines a name for the output file automatically.
num = 1
while True:
    fileName = f"Graphs\\Key_{num}"
    if os.path.isfile(f"{fileName}.pdf"):
        num += 1
    else:
        break

plt.savefig(f"{fileName}.pdf")
plt.savefig(f"{fileName}.png")
plt.show()
