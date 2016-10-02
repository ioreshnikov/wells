#!/usr/bin/env python3


import argparse
import os.path
import re
import scipy
import scipy.interpolate as interpolate
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
    re.compile("mode=(\d+)_delta=(.*?)_pump=(.*?)_loss=(.*?)_(.*?).npz"),
    re.compile("mode=(\d+)_delta=(.*?).npz")]

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


# Find minimum and maximum ranges in delta and energy.
minxs, maxxs = [], []
minys, maxys = [], []
for key, (deltas, rates) in curves.items():
    minxs.append(deltas.min())
    maxxs.append(deltas.max())
    minys.append(rates.min())
    maxys.append(rates.max())

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
for key, (deltas, rates) in curves.items():
    idx, mode, *_ = key
    plot.plot(deltas, rates)
    x = maxx - dx
    idx = abs(deltas - x).argmin()
    y = rates[idx]
    if y > maxy or y < miny:
        x = minx + dx
        idx = abs(deltas - x).argmin()
        y = rates[idx]
        if y > maxy or y < miny:
            continue
    plot.text(x, y, str(mode),
              ha="center", va="center",
              bbox=bbox, fontsize="x-small")
plot.xlabel("$\delta_{p}$")
plot.ylabel(r"$\max\left(\mathrm{Im}\,\lambda\right)$")
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
    publisher.publish("rates", args.ext)
