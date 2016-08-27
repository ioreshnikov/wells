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

        stable = None
        try:
            stable = bool(workspace["stable"])
        except:
            pass

        key = (idx, mode, pump, loss, label)

        if key not in curves:
            curves[key] = [], [], []
        deltas, energies, stability = curves[key]

        energy = util.energy(workspace["x"], workspace["solution"])
        deltas.append(delta)
        energies.append(energy)
        stability.append(stable)

        break

# Second pass, sort the data points in each of the curves.
for key, curve in curves.items():
    deltas, energies, stability = curve
    indexes = scipy.argsort(deltas)
    deltas = scipy.array(deltas)[indexes]
    energies = scipy.array(energies)[indexes]
    stability = scipy.array(stability)[indexes]
    curves[key] = deltas, energies, stability


# Third and final pass: plot the curves.
publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

xmin = -3.0
xmax = +3.0

ymin = 00.0
ymax = 20.0

dx = 1.0
dy = 3.4
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

axs = plot.subplot(1, 1, 1)
for key, curve in curves.items():
    idx, mode, *_ = key
    deltas, energies, stability = curve
    if idx == 1:
        plot.plot(
            deltas,
            energies,
            color="#7f7f7f",
            linestyle="dotted",
            zorder=1)
    else:
        # Stable branch.
        deltas_ = deltas.copy()
        energies_ = energies.copy()
        for idx, _ in enumerate(deltas):
            if not stability[idx] and not stability[idx-1]:
                energies_[idx] = None
        plot.plot(
            deltas_,
            energies_,
            color="black",
            linestyle="solid",
            zorder=3)
        # Unstable branch.
        deltas_ = deltas.copy()
        energies_ = energies.copy()
        for idx, _ in enumerate(deltas):
            if stability[idx] and stability[idx-1]:
                energies_[idx] = None
        plot.plot(
            deltas_,
            energies_,
            color="red",
            linestyle="solid",
            zorder=2)
    if idx == 1 and mode % 2 == 0:
        x = xmax - dx
        y = energies[deltas == x]
        if y > ymax - 2*dx or scipy.isnan(y):
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
plot.yticks(scipy.arange(0, ymax + 5, 5))
plot.xlabel("$\delta_{p}$")
plot.ylabel("$E_{n}(\delta_p)$")
axs.tick_params(direction="out")
plot.show()
publisher.publish("energies", args.ext)
