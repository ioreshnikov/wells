#!/usr/bin/env python3


import argparse
import scipy
import matplotlib.pyplot as plot
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
parser.add_argument("-m", "--mark",
                    help="Mark largest growth factor eigenvalue",
                    action="store_true")
parser.add_argument("--nx", "--xn",
                    help="Number of x ticks",
                    type=int,
                    default=5)
parser.add_argument("--ny", "--yn",
                    help="Number of y ticks",
                    type=int,
                    default=6)
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
parser.add_argument("input",
                    help="Input file",
                    type=str)
args = parser.parse_args()


workspace = scipy.load(args.input)
delta = workspace["delta"]
es = workspace["stability_eigenvalues"]
n = es.imag.argmax()
e = es[n]
es = scipy.delete(es, n)


minx = args.minz if args.minz is not None else es.real.min()
maxx = args.maxz if args.maxz is not None else es.real.max()
miny = args.miny if args.miny is not None else es.imag.min()
maxy = args.maxy if args.maxy is not None else es.imag.max()

xticks = scipy.linspace(minx, maxx, args.nx)
yticks = scipy.linspace(miny, maxy, args.ny)


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = args.input.replace(".npz", "")
    filename = filename + "_stev"
    publisher.init({"figure.figsize": figsize})

plot.title(r"$\delta_p=%.1f$" % delta, y=1.05)
plot.scatter(es.real, es.imag, s=1, color="black")
if args.mark:
    plot.scatter([e.real], [e.imag], s=6, color="red", marker="x")
else:
    plot.scatter([e.real], [e.imag], s=1, color="black")
plot.xlim(minx, maxx)
plot.ylim(miny, maxy)
plot.xticks(xticks)
plot.yticks(yticks)
plot.xlabel("$\mathrm{Re}\,\lambda$")
plot.ylabel("$\mathrm{Im}\,\lambda$")
plot.show()

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
