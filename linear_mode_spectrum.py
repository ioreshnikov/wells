#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy

import wells.time_independent as time_independent
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
parser.add_argument("--minz", "--zmin", "--minx", "--xmin",
                    help="Minimum x coordinate",
                    type=float)
parser.add_argument("--maxz", "--zmax", "--maxx", "--xmax",
                    help="Maximum x coordinate",
                    type=float)
parser.add_argument("--miny", "--ymin",
                    help="Minimum y coordinate",
                    type=float)
parser.add_argument("--maxy", "--ymax",
                    help="Maximum y coordinate",
                    type=float)
parser.add_argument("-p", "--physical-units",
                    help="Use physical units for plot labels",
                    action="store_true")
parser.add_argument("--delta",
                    help="Frequency shift",
                    type=float,
                    default=0.0)
args = parser.parse_args()


x = scipy.linspace(-32, +32, 2**10)
f = scipy.linspace(-64, +64, 2**11)
ys = scipy.zeros((len(f), len(x)))

u = 1/2 * x**2
u[abs(x) >= 10] = 50


n = 60
eigvals, eigvecs = time_independent.fdlp(x, u, n, boundary="box")
for n in range(eigvecs.shape[1]):
    y = eigvecs[:, n]
    f0 = eigvals[n] + args.delta
    idx = abs(f - f0).argmin()
    ys[idx, :] = abs(y) / abs(y).max()


if args.physical_units:
    delta0 = 1E11
    beta0 = 250
    xu = scipy.sqrt(beta0/delta0)
    x = xu * x

    c = 3E8
    l0 = 1.55 * 1E-6
    f0 = c/l0
    f = c/(f0 - delta0*f)


mm = 1.0
nm = 1.0
if args.physical_units:
    mm = 1E-3
    nm = 1E-9

minx = args.minz*mm if args.minz is not None else x.min()
maxx = args.maxz*mm if args.maxz is not None else x.max()
miny = args.miny*nm if args.miny is not None else f.min()
maxy = args.maxy*nm if args.maxy is not None else f.max()
maxc = 0.0
minc = 1.0


xticks = scipy.linspace(minx, maxx, args.nx)
yticks = scipy.linspace(miny, maxy, args.ny)
cticks = scipy.linspace(minc, maxc, args.nc)


def texify(ticks, digits=0):
    labels = []
    template = "$%d$"
    if digits:
        template = "$%%.%df$" % digits
    for t in ticks:
        labels.append(template % round(t, digits))
    return labels


if args.physical_units:
    xlabel = "$z,~\mathrm{mm}$"
    ylabel = "$\lambda,~\mathrm{nm}$"
    xlabels = texify(xticks/mm, digits=1)
    ylabels = texify(yticks/nm)
else:
    xlabel = "$z$"
    ylabel = "$\omega$"
    xlabels = texify(xticks)
    ylabels = texify(yticks)
clabels = texify(cticks, digits=1)


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = "linear_modes"
    publisher.init({"figure.figsize": figsize})

plot.figure()
plot.pcolormesh(x, f, ys, cmap="magma", rasterized=True)
plot.xlim(minx, maxx)
plot.ylim(miny, maxy)
plot.xticks(xticks, xlabels)
plot.yticks(yticks, ylabels)
plot.xlabel(xlabel)
plot.ylabel(ylabel)
plot.axes().tick_params(direction="out")
if args.colorbar:
    cb = plot.colorbar()
    cb.set_ticks(cticks)
    cb.set_ticklabels(clabels)


if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
