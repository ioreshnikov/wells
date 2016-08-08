#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="raw propagation data",
                    type=str)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
states = workspace["states"]


publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()
axs = plot.subplot(1, 1, 1)

image = abs(states)
plot.pcolormesh(
    x, t, image, cmap="inferno", rasterized=True)
plot.xlim(-10, +10)
plot.ylim(0, 50)
plot.xlabel("$z$")
plot.ylabel("$t$")
plot.colorbar()
axs.tick_params(direction="out")

prefix = args.input.replace(".npz", "")
publisher.publish(prefix, args.ext)
