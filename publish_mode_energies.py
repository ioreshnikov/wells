#!/usr/bin/env python3


import argparse
import os.path
import re
import scipy
import scipy.interpolate as interpolate
import wells.util as util
import wells.publisher as publisher

import matplotlib.pyplot as plot
import matplotlib.ticker as ticker


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    nargs="+")
parser.add_argument("-i", "--interactive",
                    help="Interactive mode",
                    action="store_true")
parser.add_argument("-e", "--ext",
                    help="output file extension",
                    type=str,
                    default="png")
parser.add_argument("-s", "--figsize",
                    help="Figure size",
                    type=str,
                    default=("2.8, 2.8"))
parser.add_argument("--nx", "--xn",
                    help="Number of x ticks",
                    type=int,
                    default=None)
parser.add_argument("--ny", "--yn",
                    help="Number of y ticks",
                    type=int,
                    default=None)
parser.add_argument("--dx",
                    help="Major x-axis tick step",
                    type=float,
                    default=None)
parser.add_argument("--dy",
                    help="Major y-axis tick step",
                    type=float,
                    default=None)
parser.add_argument("--mdx",
                    help="Minor x-axis tick step",
                    type=float,
                    default=None)
parser.add_argument("--mdy",
                    help="Minor y-axis tick step",
                    type=float,
                    default=None)
parser.add_argument("--minx", "--xmin",
                    help="Minimum x coordinate",
                    type=float)
parser.add_argument("--maxx", "--xmax",
                    help="Maximum x coordinate",
                    type=float)
parser.add_argument("--miny", "--ymin",
                    help="Minimum y coordinate",
                    type=float)
parser.add_argument("--maxy", "--ymax",
                    help="Maximum y coordinate",
                    type=float)
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


# Find minimum and maximum ranges in delta and energy.
minxs, maxxs = [], []
minys, maxys = [], []
for key, (deltas, energies, _) in curves.items():
    minxs.append(deltas.min())
    maxxs.append(deltas.max())
    minys.append(energies.min())
    maxys.append(energies.max())

minx = scipy.array(minxs).min()
maxx = scipy.array(maxxs).max()
miny = scipy.array(minys).min()
maxy = scipy.array(maxys).max()

minx = args.minx if args.minx is not None else minx
maxx = args.maxx if args.maxx is not None else maxx
miny = args.miny if args.miny is not None else miny
maxy = args.maxy if args.maxy is not None else maxy


# Third and final pass: plot the curves.
dx = 0.10 * (maxx - minx)
dy = 0.10 * (maxy - miny)
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    publisher.init({"figure.figsize": figsize})
plot.figure()
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
            linewidth=0.6,
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
            linewidth=0.5,
            zorder=2)
    # if idx == 1 and mode % 2 == 0:
    #     x = maxx - dx
    #     idx = abs(deltas - x).argmin()
    #     y = energies[idx]
    #     if y > maxy - dy or y < miny + dy:
    #         y = maxy - dy
    #         x = interpolate.interp1d(energies, deltas)(y)
    #         idx = abs(deltas - x).argmin()
    #         x = deltas[idx]
    #         if x > maxx - dx or x < minx + dx:
    #             continue
    #     plot.text(x, y, str(mode),
    #               ha="center", va="center",
    #               bbox=bbox, fontsize="x-small")
plot.xlabel("$\delta_{p}$")
plot.ylabel("$E(\delta_p)$")
plot.xlim(minx, maxx)
plot.ylim(miny, maxy)

if args.nx is not None:
    axs.xaxis.set_major_locator(
        ticker.MaxNLocator(args.nx))
if args.ny is not None:
    axs.yaxis.set_major_locator(
        ticker.MaxNLocator(args.ny))
if args.dx is not None:
    axs.xaxis.set_major_locator(
        ticker.MultipleLocator(args.dx))
if args.dy is not None:
    axs.yaxis.set_major_locator(
        ticker.MultipleLocator(args.dy))
if args.mdx is not None:
    axs.xaxis.set_minor_locator(
        ticker.MultipleLocator(args.mdx))
if args.mdy is not None:
    axs.yaxis.set_minor_locator(
        ticker.MultipleLocator(args.mdy))
axs.tick_params(which="both", direction="out")

if args.interactive:
    plot.show()
else:
    publisher.publish("energies", args.ext)
