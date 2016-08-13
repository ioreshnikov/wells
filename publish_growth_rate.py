#!/usr/bin/env python3


import argparse
import os.path
import re
import scipy
import scipy.interpolate as interpolate
import wells.util as util
import wells.publisher as publisher

import matplotlib.pyplot as plot


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    nargs="+")
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


# Regular expressions for file names.
patterns = [
    re.compile("mode=(\d+)_delta=(.*)_pump=(.*)_loss=(.*)_(.*).npz"),
    re.compile("mode=(\d+)_delta=(.*).npz")]

# First pass: collect the curve points.
curves = {}
for filename in args.input:
    basename = os.path.basename(filename)
    for idx, pattern in enumerate(patterns):
        match = pattern.match(basename)
        if not match:
            continue
        groups = match.groups()
        if len(groups) == 2:
            mode, delta = groups
            pump = loss = 0
            label = None
        if len(groups) == 5:
            mode, delta, pump, loss, label = groups
        mode = int(mode)
        delta, pump, loss = map(float, (delta, pump, loss))

        workspace = scipy.load(filename)
        eigenvalues = workspace["stability_eigenvalues"]
        rate = eigenvalues.imag.max()

        key = (idx, mode, pump, loss, label)

        if key not in curves:
            curves[key] = [], []
        deltas, rates = curves[key]

        deltas.append(delta)
        rates.append(rate)

        break


# Second pass, sort the data points in each of the curves.
for key, curve in curves.items():
    deltas, rates = curve
    indexes = scipy.argsort(deltas)
    deltas = scipy.array(deltas)[indexes]
    rates = scipy.array(rates)[indexes]
    curves[key] = deltas, rates


# Third and final pass: plot the curves.
publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

xmin = -4.0
xmax = +4.0

ymin = -0.1
ymax = +0.7

dx = 1.0
dy = 0.1
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

axs = plot.subplot(1, 1, 1)
for key, curve in curves.items():
    idx, mode, *_ = key
    deltas, rates = curve
    # color = "black"
    # if mode == 2:
    #     color = "red"
    # if mode == 4:
    #     color = "green"
    # if mode == 6:
    #     color = "mediumpurple"
    plot.plot(deltas, rates)
    x = xmax - dx
    y = rates[deltas == x]
    plot.text(x, y, str(mode),
              ha="center", va="center",
              bbox=bbox, fontsize="x-small")
plot.xlim(xmin, xmax)
plot.ylim(ymin, ymax)
plot.xticks(scipy.arange(xmin, xmax + dx, dx))
plot.yticks(scipy.arange(0, ymax + dy, dy))
plot.xlabel(r"$\delta_{p}$")
plot.ylabel(r"$\max\left(\Im\,\lambda\right)$")
axs.tick_params(direction="out")

plot.show()
publisher.publish("rates", args.ext)
