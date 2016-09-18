#!/usr/bin/env python3


import argparse
import matplotlib
import matplotlib.pyplot as plot
import scipy

import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interactive",
                    help="Interactive mode",
                    action="store_true")
parser.add_argument("-e", "--ext",
                    help="Output image extension",
                    type=str,
                    default="png")
parser.add_argument("-v", "--vertical",
                    help="Plot vertical colorbar",
                    action="store_true")
parser.add_argument("-s", "--figsize",
                    help="Figure size",
                    type=str,
                    default=("2.8, 0.1"))
parser.add_argument("-l", "--label",
                    help="Colorbar label",
                    type=str,
                    default="dB")
parser.add_argument("-n",
                    help="Number of ticks to plot",
                    type=int,
                    default=5)
parser.add_argument("--min",
                    help="Minimum decibels level to display",
                    type=float,
                    default=-60)
parser.add_argument("--max",
                    help="Minimum decibels level to display",
                    type=float,
                    default=0)
args = parser.parse_args()



if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    publisher.init({"figure.figsize": figsize})


def texify(ticks, digits=0):
    labels = []
    template = "$%d$"
    if digits:
        template = "$%%.%df$" % digits
    for t in ticks:
        labels.append(template % t)
    return labels


ticks = scipy.linspace(args.min, args.max, args.n)
labels = texify(ticks, digits=0)


fig = plot.figure()
axes = fig.add_axes([0.30, 0.40, 0.50, 0.10])
cmap = matplotlib.cm.magma
norm = matplotlib.colors.Normalize(vmin=args.min, vmax=args.max)
cb = matplotlib.colorbar.ColorbarBase(
    axes,
    cmap=cmap,
    norm=norm,
    orientation="vertical" if args.vertical else "horizontal")
cb.set_ticks(ticks)
cb.set_ticklabels(labels)
cb.set_label(args.label, labelpad=-28)

if args.interactive:
    plot.show()
else:
    publisher.publish("colorbar", args.ext, tight=False)
