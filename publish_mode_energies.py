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
    re.compile("mode=(\d+)_delta=(.*)_pump=(.*)_loss=(.*).npz"),
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
        key = (idx, mode, pump, loss, label)

        if key not in curves:
            curves[key] = [], []
        deltas, energies = curves[key]

        # Load the file to calculate the energy.
        workspace = scipy.load(filename)
        energy = util.energy(workspace["x"], workspace["solution"])
        deltas.append(delta)
        energies.append(energy)
        break


# Second pass, sort the data points in each of the curves.
for key, curve in curves.items():
    deltas, energies = curve
    indexes = scipy.argsort(deltas)
    deltas = scipy.array(deltas)[indexes]
    energies = scipy.array(energies)[indexes]
    curves[key] = deltas, energies


# Third and final pass: plot the curves.
publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

xmin = -4.0
xmax = +2.0

ymin = 00.0
ymax = 10.0

dx = 1.0
dy = 10/6 * dx
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

axs = plot.subplot(1, 1, 1)
for key, curve in curves.items():
    idx, mode, *_ = key
    deltas, energies = curve
    linestyle = "solid"
    if idx == 2:
        linestyle = "dotted"
    plot.plot(deltas, energies, color="black", linestyle=linestyle)
    if idx == 2:
        x = xmax - dx
        y = energies[deltas == x]
        if y > ymax or scipy.isnan(y):
            f = interpolate.interp1d(energies, deltas)
            y = ymax - dy
            x = f(y)
            if x < xmin + dx or x > xmax - dx:
                continue
        plot.text(x, y, str(mode),
                  ha="center", va="center",
                  bbox=bbox, fontsize="x-small")
plot.xlim(xmin, xmax)
plot.ylim(ymin, ymax)
plot.xticks(scipy.arange(xmin, xmax + 1, 1))
plot.yticks(scipy.arange(0, ymax + 2, 2))
plot.xlabel("$\delta_{p}$")
plot.ylabel("$E_{n}(\delta_p)$")
axs.tick_params(direction="out")
plot.show()
publisher.publish("energies", args.ext)
