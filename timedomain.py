#!/usr/bin/env python3


import argparse
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
parser.add_argument("-s", "--figsize",
                    help="Figure size",
                    type=tuple,
                    default=("2.8", "2.4"))
parser.add_argument("--minx", "--xmin",
                    help="Minimum x coordinate",
                    type=float)
parser.add_argument("--maxx", "--xmax",
                    help="Maximum x coordinate",
                    type=float)
parser.add_argument("--mint", "--tmin",
                    help="Minimum t coordinate",
                    type=float)
parser.add_argument("--maxt", "--tmax",
                    help="Maximum t coordinate",
                    type=float)
parser.add_argument("--dbmin", "--mindb",
                    help="Minimum decibels level to display",
                    type=float,
                    default=-60)
parser.add_argument("--ssx",
                    help="Subsample in x",
                    type=int)
parser.add_argument("--ssy",
                    help="Subsample in y",
                    type=int)
parser.add_argument("input",
                    help="Input file",
                    type=str)
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
ys = workspace["states"]
bg = workspace["background"]


minx = args.minx if args.minx is not None else x.min()
maxx = args.maxx if args.maxx is not None else x.max()
mint = args.mint if args.mint is not None else t.min()
maxt = args.maxt if args.maxt is not None else t.max()
minc = args.dbmin
maxc = 0


window = (x > minx) & (x < maxx)
x = x[window]
ys = ys[:, window]

if args.ssx:
    x = x[::args.ssx]
    ys = ys[:, ::args.ssx]
if args.ssy:
    t = t[::args.ssy]
    ys = ys[::args.ssy, :]


ys = abs(abs(ys) - bg)
ys = ys / ys.max()
ys = 20 * scipy.log10(ys)

xticks = scipy.linspace(minx, maxx, 5)
tticks = scipy.arange(mint, maxt + 1, 10)
cticks = scipy.arange(minc, maxc + 1, 20)


if not args.interactive:
    figsize = [float(x) for x in args.figsize]
    filename = args.input.replace(".npz", "")
    filename = filename + "_timedomain"
    publisher.init({"figure.figsize": figsize})

plot.figure()
plot.pcolormesh(x, t, ys, cmap="magma", rasterized=True)
cb = plot.colorbar()
plot.xlim(minx, maxx)
plot.ylim(mint, maxt)
plot.clim(minc, maxc)
plot.xticks(xticks)
plot.yticks(tticks)
cb.set_ticks(cticks)
plot.xlabel("$x$")
plot.ylabel("$t$")
plot.axes().tick_params(direction="out")

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
