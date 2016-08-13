#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="raw propagation data",
                    type=str)
parser.add_argument("--min",
                    help="minimum z coordinate",
                    type=float,
                    default=0.0)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
states = workspace["states"]


ticks = scipy.arange(args.min, t.max() + 10, 10)
image = abs(states)


publisher.init({"figure.figsize": (1.4, 2.4)})
plot.figure()

axs = plot.subplot(1, 1, 1)
plot.pcolormesh(
    x, t, image, cmap="inferno", rasterized=True)
plot.xlim(-5, +5)
plot.ylim(args.min, t.max())
plot.yticks(ticks)
plot.xlabel("$z$")
plot.ylabel("$t$")
axs.tick_params(direction="out")

prefix = args.input.replace(".npz", "")
publisher.publish(prefix, args.ext)
