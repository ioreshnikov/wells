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

xticks = scipy.linspace(minx, maxx, 5)
yticks = scipy.linspace(mint, maxt, 6)
cticks = scipy.linspace(minc, maxc, 5)


def texify(ticks, digits=0):
    labels = []
    template = "$%d$"
    if digits:
        template = "$%%.%df$" % digits
    for t in ticks:
        labels.append(template % t)
    return labels

xlabel = "$z$"
ylabel = "$t$"
xlabels = texify(xticks)
ylabels = texify(yticks)
clabels = texify(cticks)

if args.physical_units:
    # This is very ad-hoc.
    delta0 = 1E11  # Hardcoded, but what?
    beta0 = 250    # ... and this too.
    unit = scipy.sqrt(beta0/delta0)

    xlabel = r"$z,~\mathrm{mm}$"
    ylabel = r"$t,~\mathrm{ns}$"

    xlabels = texify(unit*xticks/1E-3, digits=1)
    ylabels = texify(2*scipy.pi*yticks/delta0/1E-9, digits=2)


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
plot.xticks(xticks, xlabels)
plot.yticks(yticks, ylabels)
cb.set_ticks(cticks)
cb.set_ticklabels(clabels)
plot.xlabel(xlabel)
plot.ylabel(ylabel)
plot.axes().tick_params(direction="out")

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
