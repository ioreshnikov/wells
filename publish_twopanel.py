#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy as s
import scipy.fftpack as fft
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


workspace = s.load(args.input)
t = workspace["t"]
x = workspace["x"]
k = workspace["k"]
states = workspace["states"]
spectra = workspace["spectra"]


ticks = s.arange(args.min, t.max() + 10, 10)


publisher.init({"figure.figsize": (3.1, 1.6)})

image = abs(states)
axs = plot.subplot(1, 2, 1)
plot.pcolormesh(
    x, t, image, cmap="inferno", rasterized=True)
plot.xlim(-5, +5)
plot.ylim(args.min, 50)
plot.xlabel("$z$")
plot.ylabel("$t$")
plot.yticks(ticks)
axs.tick_params(direction="out")


image = abs(spectra)
axs = plot.subplot(1, 2, 2)
plot.pcolormesh(
    k, t, image, cmap="rainbow", rasterized=True)
plot.xlim(-10, +10)
plot.ylim(args.min, 50)
plot.xlabel("$k_z$")
plot.ylabel("$t$")
plot.yticks(ticks)
axs.tick_params(direction="out")


prefix = args.input.replace(".npz", ".twopanel")
publisher.publish(prefix, args.ext)
