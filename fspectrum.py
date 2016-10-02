#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import matplotlib.ticker as ticker
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
                    type=str,
                    default="2.8, 2.4")
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

f = 2*scipy.pi * fft.fftfreq(len(t), t[1] - t[0])
f = fft.fftshift(f)


if args.physical_units:
    delta0 = 1E11
    beta0 = 250
    xu = scipy.sqrt(beta0/delta0)
    x = xu * x

    c = 3E8
    l0 = 1.55 * 1E-6
    f0 = c/l0
    f = c/(f0 + delta0*f)


mm = 1.0
nm = 1.0
if args.physical_units:
    mm = 1E-3
    nm = 1E-9
x = x/mm
f = f/nm

minx = args.minz if args.minz is not None else x.min()
maxx = args.maxz if args.maxz is not None else x.max()
miny = args.minf if args.minf is not None else f.min()
maxy = args.maxf if args.maxf is not None else f.max()
maxc = 0
minc = args.dbmin


window = (x > minx) & (x < maxx)
x = x[window]
ys = ys[:, window]

if args.ssx:
    x = x[::args.ssx]
    ys = ys[:, ::args.ssx]

ys = fft.fft(ys, axis=0)
ys = fft.fftshift(ys, axes=[0])

window = (f > miny) & (f < maxy)
f = f[window]
ys = ys[window, :]

if args.ssy:
    f = f[::args.ssy]
    ys = ys[::args.ssy, :]

ys = abs(ys)
ys = ys / ys.max()
ys = 20 * scipy.log10(ys)


if args.physical_units:
    xlabel = "$z,~\mathrm{mm}$"
    ylabel = "$\lambda,~\mathrm{nm}$"
else:
    xlabel = "$z$"
    ylabel = "$\omega$"


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = args.input.replace(".npz", "")
    filename = filename + "_fspectrum"
    publisher.init({"figure.figsize": figsize})

plot.figure()
axs = plot.subplot(1, 1, 1)
plot.pcolormesh(x, f, ys, cmap="magma", rasterized=True)
plot.xlim(minx, maxx)
plot.ylim(miny, maxy)
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
