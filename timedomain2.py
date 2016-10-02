#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import matplotlib.ticker as ticker
import re
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
                    type=str,
                    nargs="+")
args = parser.parse_args()


workspace = scipy.load(args.input[0])
t = workspace["t"]
x = workspace["x"]
bg = workspace["background"]
delta = workspace["delta"]
pump = workspace["pump"]
loss = workspace["loss"]


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

miny = args.miny if args.miny is not None else x.min()
maxy = args.maxy if args.maxy is not None else x.max()
minc = args.dbmin
maxc = 0


window = (x > miny) & (x < maxy)
x = x[window]
if args.ssy:
    x = x[::args.ssy]

pattern = re.compile(r"mint=(.*?)_")
def mint(filename):
    match = pattern.search(filename)
    if match:
        return float(match.group(1))

ts = []
yss = []
for n, filename in enumerate(sorted(args.input, key=mint)):
    print("%d/%d: %s" % (n+1, len(args.input), filename))
    workspace = scipy.load(filename)
    t = workspace["t"]
    ys = workspace["states"]
    ys = ys[:, window]
    if args.ssy:
        ys = ys[:, ::args.ssy]
    if args.ssx:
        t = t[::args.ssx]
        ys = ys[::args.ssx, :]
    ts.append(t)
    yss.append(ys)
    if t.max() >= args.maxx:
        break
t = scipy.hstack(ts)
ys = scipy.vstack(yss)
print("Resulting image shape:", ys.shape)


minx = args.minx if args.minx is not None else t.min()
maxx = args.maxx if args.maxx is not None else t.max()


ys = abs(ys)
ys = ys / ys.max()
ys = 20 * scipy.log10(ys)


if args.physical_units:
    xlabel = "$t,~\mathrm{ns}$"
    ylabel = "$z,~\mathrm{mm}$"
else:
    xlabel = "$t$"
    ylabel = "$z$"


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = ("delta=%.2f_"
                "pump=%.2E_"
                "loss=%.2E_"
                "mint=%.2f_"
                "maxt=%.2f_timedomain2"
                % (delta, pump, loss, minx, maxx))
    publisher.init({"figure.figsize": figsize})

plot.figure()
axs = plot.subplot(1, 1, 1)
plot.pcolormesh(t, x, ys.T, cmap="magma", rasterized=True)
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
