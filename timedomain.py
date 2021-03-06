#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import matplotlib.ticker as ticker
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
                    type=str,
                    default=("2.8, 2.8"))
parser.add_argument("-c", "--colorbar",
                    help="Show colorbar",
                    action="store_true")
parser.add_argument("--nx", "--xn",
                    help="Number of x ticks",
                    type=int,
                    default=5)
parser.add_argument("--ny", "--yn",
                    help="Number of y ticks",
                    type=int,
                    default=6)
parser.add_argument("--nc", "--cn",
                    help="Number of colorbar ticks",
                    type=int,
                    default=4)
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
parser.add_argument("--minz", "--zmin", "--minx", "--xmin",
                    help="Minimum x coordinate",
                    type=float)
parser.add_argument("--maxz", "--zmax", "--maxx", "--xmax",
                    help="Maximum x coordinate",
                    type=float)
parser.add_argument("--mint", "--tmin", "--miny", "--ymin",
                    help="Minimum y coordinate",
                    type=float)
parser.add_argument("--maxt", "--tmax", "--maxy", "--ymax",
                    help="Maximum y coordinate",
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
parser.add_argument("-p", "--physical-units",
                    help="Use physical units for plot labels",
                    action="store_true")
parser.add_argument("input",
                    help="Input file",
                    type=str)
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
ys = workspace["states"]
bg = workspace["background"]
delta = workspace["delta"]


if args.physical_units:
    # This is very ad-hoc.
    delta0 = 1E11  # Hardcoded, but what?
    beta0 = 250    # ... and this too.
    xu = scipy.sqrt(beta0/delta0)
    x = xu * x
    t = 2*scipy.pi/delta0 * t


mm = 1.0
ns = 1.0
if args.physical_units:
    mm = 1E-3
    ns = 1E-9
x = x/mm
t = t/ns

minx = args.minz if args.minz is not None else x.min()
maxx = args.maxz if args.maxz is not None else x.max()
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

ys = abs(ys)
ys = ys / ys.max()
ys = 20 * scipy.log10(ys)


if args.physical_units:
    xlabel = "$z,~\mathrm{mm}$"
    ylabel = "$t,~\mathrm{ns}$"
else:
    xlabel = "$z$"
    ylabel = "$t$"


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = args.input.replace(".npz", "")
    filename = filename + "_timedomain"
    publisher.init({"figure.figsize": figsize})

plot.figure()
axs = plot.subplot(1, 1, 1)
plot.pcolormesh(x, t, ys, cmap="magma", rasterized=True)
plot.xlim(minx, maxx)
plot.ylim(mint, maxt)
plot.clim(minc, maxc)
plot.xlabel(xlabel)
plot.ylabel(ylabel)

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
if args.colorbar:
    cb = plot.colorbar()
    cb.set_label("dB")

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
