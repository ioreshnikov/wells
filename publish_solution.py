#!/usr/bin/env python3


import argparse
import scipy
import wells.publisher as publisher

import matplotlib.pyplot as plot
import matplotlib.ticker as ticker


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="solution file",
                    type=str,
                    nargs="+")
parser.add_argument("-l", "--label",
                    help="Panel label",
                    type=str)
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


ns = []
solutions = []
for filename in args.input:
    workspace = scipy.load(filename)
    x = workspace["x"]
    n = workspace["n"]
    delta = workspace["delta"]
    solution = workspace["solution"]

    solution = solution / abs(solution).max()
    ns.append(n)
    solutions.append(solution)


minys, maxys = [], []
for solution in solutions:
    minys.append(abs(solution).min())
    maxys.append(abs(solution).max())
minx = x.min()
maxx = x.max()
miny = scipy.array(minys).min()
maxy = scipy.array(maxys).max()

minx = args.minx if args.minx is not None else minx
maxx = args.maxx if args.maxx is not None else maxx
miny = args.miny if args.miny is not None else miny
maxy = args.maxy if args.maxy is not None else maxy


dx = 0.10 * (maxx - minx)
dy = 0.10 * (maxy - miny)
bbox = dict(boxstyle="circle, pad=0.1", lw="0.0", fc="white")

if args.interactive:
    plot.figure()
else:
    figsize = [float(x) for x in args.figsize.split(",")]
    publisher.init({"figure.figsize": figsize})

axs = plot.subplot(1, 1, 1)
offset = 0
for n, solution in zip(ns, solutions):
    y = abs(solution) + offset
    zorder = len(solutions) - offset
    plot.plot(
        x, y,
        label=str(n),
        zorder=zorder)
    plot.fill_between(
        x, offset, y,
        linewidth=0,
        facecolor="white",
        zorder=zorder)
    offset = offset + 1
legend = plot.legend(loc=9, ncol=2, frameon=False)
legend.get_frame().set_lw(0.5)

if args.label is not None:
    plot.text(maxx - dx, dy, "(%s)" % args.label,
              ha="center", va="center",
              bbox=bbox)

plot.xlabel(r"$z$")
plot.ylabel(r"$\left|\psi\right|$")
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
axs.tick_params(which="both", axis="y",
                left="off", labelleft="off",
                right="off", labelright="off")

if args.interactive:
    plot.show()
else:
    output = "solution"
    publisher.publish(output, args.ext)
