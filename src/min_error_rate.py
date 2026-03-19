import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from numpy.polynomial.polynomial import polyfit

import bb84


def fitExponetial(ax, x, y, error, col, colError):
    """
    Fits an exponetial curve to a set of data.

    Parameters
    ----------
    ax : matplotlib.axes
        Axes to plot on.
    x : List of integers or floats
        Holds x-coordinates of graph to fit curve to.
    y : List of integers or floats
        Holds y-coordinates of graph to fit curve to.
    error : List of integers or floats
        List of y-coordinate errors.
    col : String
        Matplotlib compatible colour for the curve.
    colError : String
        Matplotlib compatible colour for the shaded error region.

    Returns
    -------
    line : matplotlib.lines.Line2D
        Fitted curve.
    fill : matplotlib.collections.FillBetweenPolyCollection
        The shaded error region.
    """
    y = np.array(y)
    y = y[y > 0]

    x0 = np.array(x)
    x0 = x0[:len(y)]

    error = np.array(error)
    error = error[:len(y)]

    yLower = y - error
    yLower = yLower[yLower > 0]
    xLower = np.array(x)
    xLower = x[:len(yLower)]

    c, m = polyfit(x0, np.log(y), 1, w = np.sqrt(y))

    cUpper, mUpper = polyfit(x0, np.log(y + error), 1, w = np.sqrt(y + error))
    cLower, mLower = polyfit(xLower, np.log(yLower), 1,
                             w = np.sqrt(yLower))
    mError = (mUpper - mLower) / 2
    cError = (cUpper - cLower) / 2

    print(f"Graph of form y = Aexp(bx), where A = {np.exp(c)} \u00B1 " +
          f"{np.exp(cError)} and b = {m} \u00B1 {mError}.")

    x1 = np.arange(x[0] - 1, x[-1] + 1)
    line, = ax.plot(x1, np.exp(c) * np.exp(m * x1), '-', color = col,
                    zorder = 5)
    fill = ax.fill_between(x1, np.exp(cLower) * np.exp(mLower * x1),
                           np.exp(cUpper) * np.exp(mUpper * x1),
                           color = colError)

    return line, fill


matplotlib.rcParams.update({'font.size': 14})

graph = plt.figure()
graph, ax = plt.subplots(figsize=(10, 5))

distance = 100  # Distance in km over which signal is sent.
realError = 0.01 + 7.5e-5 * 10 ** ((0.16 * distance + 7.5) / 10)

minErrorRate = realError + 0.5 * realError
# Minimum error rate to guarantee detection of an eavesdropper, or another
# source of error such that the result must be discarded(for greater than 25%).

# Contains the number of bits which will be analysed at each interval.
intervals = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
# Contains the mean of the percentage of failed trials for each bit interval.
failedTrials = []
# Contains the standard errors corresponding to each bit interval.
trialErrors = []
for i in range(len(intervals)):
    trials = 100000  # The number of trials to do for each bit interval.
    repeats = 10  # The number of times to repeat the number of trials in the
    # trials variable for each bit interval - so that a mean and standard error
    # can be calculated.

    failList = []  # Contains the result of each set of trials, will be used to
    # find the mean and standard error.
    for n in range(repeats):
        fails = 0  # Counts how many trials have had an error rate less than
        # that of the minErrorRate.

        for m in range(trials):
            binaryNums = []
            for j in range(4):
                binaryNums.append(np.random.randint(0, 2, [intervals[i]]))

            try:
                error = bb84.bb84Protocol(binaryNums, intervals[i])
            # Some trials with low bit numbers may have zero matching bases.
            except ZeroDivisionError:
                trials += 1

            if error + realError < minErrorRate:
                fails += 1

        failList.append(fails / trials * 100)

    trialErrors.append(np.std(failList))
    failedTrials.append(np.mean(failList))
    print(f"Percentage of {trials} trials which fail to detect an Eavesdropper"
          + f" for {intervals[i]} bits: " +
          f"{failedTrials[i]} \u00B1 {trialErrors[i]}%")

ax.errorbar(intervals, failedTrials, trialErrors, marker = 'x', ls = 'none',
            color = "#CDA5D4", capsize = 2)
fitExponetial(ax, intervals, failedTrials, trialErrors, "purple", "#F0D4FF")

ax.set_title(f"Percentage of {trials} " +
             "Trials which Failed to Detect an Eavesdropper")
ax.set_ylabel('Failed Trials (%)')
ax.set_xlabel('Number of Bits in Alice\'s Message')

# Determines a name for the output file automatically.
num = 1
while True:
    fileName = f"Graphs\\Detect_{num}"
    if os.path.isfile(f"{fileName}.pdf"):
        num += 1
    else:
        break

plt.tight_layout()
plt.savefig(f"{fileName}.pdf")
plt.savefig(f"{fileName}.png")
plt.show()
