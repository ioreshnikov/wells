#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import scipy.fftpack as fft

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
parser.add_argument("--minf", "--fmin", "--miny", "--ymin",
                    help="Minimum y coordinate",
                    type=float)
parser.add_argument("--maxf", "--fmax", "--maxy", "--ymax",
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


minx = args.minz if args.minz is not None else x.min()
maxx = args.maxz if args.maxz is not None else x.max()
minc = args.dbmin
maxc = 0


window = (x > minx) & (x < maxx)
x = x[window]
ys = ys[:, window]

if args.ssx:
    x = x[::args.ssx]
    ys = ys[:, ::args.ssx]


f = 2*scipy.pi * fft.fftfreq(len(t), t[1] - t[0])
f = fft.fftshift(f)
minf = args.minf if args.minf is not None else f.min()
maxf = args.maxf if args.maxf is not None else f.max()

ys = fft.fft(ys, axis=0)
ys = fft.fftshift(ys, axes=[0])
ys = abs(ys)
ys = ys / ys.max()
ys = 20 * scipy.log10(ys)


if args.ssy:
    f = f[::args.ssy]
    ys = ys[::args.ssy, :]

xticks = scipy.linspace(minx, maxx, 5)
yticks = scipy.linspace(minf, maxf, 5)
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
    print(yticks * delta0)
    exit()


if not args.interactive:
    figsize = [float(x) for x in args.figsize]
    filename = args.input.replace(".npz", "")
    filename = filename + "_fspectrum"
    publisher.init({"figure.figsize": figsize})

plot.figure()
plot.pcolormesh(x, f, ys, cmap="magma", rasterized=True)
cb = plot.colorbar()
plot.xlim(minx, maxx)
plot.ylim(minf, maxf)
plot.clim(minc, maxc)
plot.xticks(xticks)
plot.yticks(yticks)
cb.set_ticks(cticks)
plot.xlabel("$x$")
plot.ylabel("$t$")
plot.axes().tick_params(direction="out")

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
