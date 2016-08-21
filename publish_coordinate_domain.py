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


tticks = scipy.arange(args.min, t.max() + 50, 50)
xticks = scipy.arange(-15, +20, 5)

image = abs(states)
# image = image / image.max()
# image = 20 * scipy.log10(image)


publisher.init({"figure.figsize": (2.8, 1.6)})
plot.figure()

axs = plot.subplot(1, 1, 1)
plot.pcolormesh(
    t, x, image, cmap="hot", rasterized=True)
plot.xlim(tticks.min(), tticks.max())
plot.ylim(xticks.min(), xticks.max())
plot.clim(-30, 0)
plot.xticks(tticks)
plot.yticks(xticks)
plot.ylabel("$z$")
plot.xlabel("$t$")
axs.tick_params(direction="out")

prefix = args.input.replace(".npz", "")
publisher.publish(prefix, args.ext)