#!/usr/bin/env python3


import argparse
import scipy as s
import scipy.fftpack as fft
import matplotlib.pyplot as plot
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("--t",
                    type=float,
                    help="Time at which diagram should be plotted")
parser.add_argument("--width",
                    type=float,
                    default=1.0,
                    help="Window width")
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
parser.add_argument("input",
                    type=str,
                    help="Path to the input file")
args = parser.parse_args()


workspace = s.load(args.input)
t = workspace["t"]
x = workspace["x"]
k = workspace["k"]
states = workspace["states"]
background = workspace["background"]


idx = abs(t - args.t).argmin()
t = t[idx]
state = states[idx, :]


def xfrog(x0, state, delay, width):
    window = lambda x: s.exp(-(x/width)**2)
    diagram = s.zeros((len(x), len(delay)), dtype=complex)
    for idx in range(len(delay)):
        diagram[:, idx] = window(x - delay[idx]) * state
    diagram = fft.fft(diagram, axis=0)
    diagram = fft.fftshift(diagram, axes=[0])
    return diagram


delay = s.linspace(-64, +64, 2**11)
image = xfrog(t, state, delay, args.width)
image = abs(image)
image = image / image.max()
image = 20 * s.log10(image)

publisher.init({"figure.figsize": (2.8, 2.4)})
prefix = args.input.replace(".npz", "")
filename = prefix + "_xfrog=%.2f" % args.t

plot.figure()
axs = plot.subplot(1, 1, 1)
plot.title(r"$t=%.2f$" % args.t, y=1.05)
plot.pcolormesh(
    delay, k, image,
    cmap="magma",
    rasterized=True)
plot.xlim(-20, +20)
plot.xticks(s.arange(-40, +41, 20))
plot.ylim(-40, +40)
plot.yticks(s.arange(-40, +41, 20))
plot.clim(-80, 0)
plot.colorbar().set_ticks(s.arange(-80, 1, 20))
plot.xlabel(r"$z$")
plot.ylabel(r"$k_z$")
axs.tick_params(direction="out")

publisher.publish(filename, args.ext)
plot.close()

print(filename + "." + args.ext)
