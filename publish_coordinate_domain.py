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

t = t[::4]
states = states[::4, :]


tticks = scipy.arange(0, t.max() + 10, 10)
xticks = scipy.arange(x.min(), x.max() + 5, 5)

image = abs(states)
image = image / image.max()
image = 20 * scipy.log10(image)


publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

axs = plot.subplot(1, 1, 1)
plot.pcolormesh(
    x, t, image, cmap="magma", rasterized=True)
plot.xlim(xticks.min(), xticks.max())
plot.ylim(tticks.min(), tticks.max())
plot.clim(-80, 0)
plot.xticks(xticks)
plot.yticks(tticks)
plot.xlabel("$z$")
plot.ylabel("$t$")
axs.tick_params(direction="out")

prefix = args.input.replace(".npz", "")
publisher.publish(prefix, args.ext)
