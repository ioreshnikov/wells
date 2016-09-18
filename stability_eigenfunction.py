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
x = workspace["x"]
u = workspace["potential"]
es = workspace["stability_eigenvalues"]
ys = workspace["stability_eigenvectors"]


n = es.imag.argmax()
y = ys[:, n]


n = len(y)
a = y[:n//2]
b = y[n//2:]
y = a + b.conjugate()


minx = args.minz if args.minz is not None else x.min()
maxx = args.maxz if args.maxz is not None else x.max()
miny = args.miny if args.miny is not None else abs(y).min()
maxy = args.maxy if args.maxy is not None else abs(y).max()

xticks = scipy.linspace(minx, maxx, args.nx)
yticks = scipy.linspace(miny, maxy, args.ny)


if not args.interactive:
    figsize = [float(x) for x in args.figsize.split(",")]
    filename = args.input.replace(".npz", "")
    filename = filename + "_stef"
    publisher.init({"figure.figsize": figsize})

plot.plot(x, y.imag, color="red", linestyle="solid")
plot.plot(x, y.real, color="black", linestyle="solid")
plot.xlim(minx, maxx)
plot.ylim(miny, maxy)
plot.xticks(xticks)
plot.yticks(yticks)
plot.xlabel("$z$")
plot.show()

if args.interactive:
    plot.show()
else:
    publisher.publish(filename, args.ext)
