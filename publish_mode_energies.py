#!/usr/bin/env python3


import argparse
import re
import scipy
import wells.util as util
import wells.publisher as publisher

import matplotlib.pyplot as plot


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    nargs="+")
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


# Extract the data.
pattern = re.compile("mode=(.*)_delta=(.*).npz")
modes = set([])
deltas = set([])
points = []
for filename in args.input:
    match = pattern.match(filename)
    if not match:
        continue
    mode, delta = match.groups()
    mode, delta = int(mode), float(delta)

    workspace = scipy.load(filename)
    x = workspace["x"]
    u = workspace["solution"]
    energy = util.energy(x, u)

    modes.add(mode)
    deltas.add(delta)
    points.append((mode, delta, energy))


deltas = scipy.array(sorted(deltas))
energies = scipy.zeros((len(deltas), max(modes) + 1))
for point in points:
    mode, delta, energy = point
    energies[deltas == delta, mode] = energy


ymax = energies[deltas == 0, :].max()
energies[energies == 0] = None

xmin = -5.5
xmax = 5.5
dx = 1.5
bbox = dict(boxstyle="circle, pad=0.2", lw="0.25", fc="white")


publisher.init({"figure.figsize": (3.1, 3.1)})
plot.figure()

for n in range(max(modes) + 1):
    plot.plot(deltas, energies[:, n], color="black")
    x = xmax - dx
    y = energies[deltas == x, n]
    if y > ymax or scipy.isnan(y):
        x = xmin + dx
        y = energies[deltas == x, n]
    print(x, y)
    plot.text(x, y, str(n),
              ha="center", va="center",
              bbox=bbox, fontsize="x-small")
plot.xlim(xmin, xmax)
plot.ylim(0, ymax)
plot.xlabel("$\delta_{p}$")
plot.ylabel("$E_{n}$")

publisher.publish("energies", args.ext)
