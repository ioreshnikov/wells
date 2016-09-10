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
parser.add_argument("--minx", "--xmin",
                    help="Minimum x coordinate",
                    type=float)
parser.add_argument("--maxx", "--xmax",
                    help="Maximum x coordinate",
                    type=float)
parser.add_argument("--minf", "--fmin",
                    help="Minimum f coordinate",
                    type=float)
parser.add_argument("--maxf", "--fmax",
                    help="Maximum f coordinate",
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
fticks = scipy.linspace(minf, maxf, 5)
cticks = scipy.linspace(minc, maxc, 5)


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
plot.yticks(fticks)
cb.set_ticks(cticks)
plot.xlabel("$x$")
plot.ylabel("$t$")
plot.axes().tick_params(direction="out")

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
