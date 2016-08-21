#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import scipy.fftpack as fft
import scipy.integrate as integrate
import wells.time_independent as time_independent
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="raw propagation data",
                    type=str)
parser.add_argument("--win",
                    help="window size",
                    type=float,
                    default=50.0)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
k = workspace["k"]
states = workspace["states"]


winsize = args.win / t.max() * len(t)
winsize = int(winsize)
num_windows = len(t) / winsize
num_windows = int(num_windows)

f = fft.fftfreq(winsize, t[1] - t[0])
f = 2 * scipy.pi * fft.fftshift(f)

publisher.init({"figure.figsize": (2.8, 2.4)})
prefix = args.input.replace(".propagation.npz", "")

for n in range(num_windows):
    print("Window: %d/%d" % (n, num_windows))

    start = n * winsize
    stop = start + winsize
    window = slice(start, stop)

    print("\tTime domain.")
    t_ = t[window]
    states_ = states[window, :]
    image = abs(states_)
    image = image / image.max()
    image = 20 * scipy.log10(image)

    plot.figure()
    axs = plot.subplot(1, 1, 1)
    plot.pcolormesh(
        x, t_, image,
        cmap="magma",
        rasterized=True)
    plot.xlim(-20, +20)
    plot.clim(-60, 0)
    plot.xticks(scipy.arange(-20, +30, 10))
    plot.xlabel("$z$")
    plot.ylabel("$t$")
    plot.colorbar().set_ticks(scipy.arange(-60, 10, 10))
    axs.tick_params(direction="out")
    publisher.publish(prefix + "_" + str(n) + "_timedomain", args.ext)
    plot.close()

    print("\tFrequency spectrum.")
    spectra_ = fft.fft(states_, axis=0)
    image = fft.fftshift(spectra_, axes=(0,))
    image = abs(image)
    image = image / image.max()
    image = 20 * scipy.log10(image)

    plot.figure()
    axs = plot.subplot(1, 1, 1)
    plot.pcolormesh(
        x, f, image,
        cmap="magma",
        rasterized=True)
    plot.xlim(-20, +20)
    plot.ylim(-60, +60)
    plot.clim(-60, 0)
    plot.xticks(scipy.arange(-20, +30, 10))
    plot.yticks(scipy.arange(-60, +80, 20))
    plot.xlabel("$z$")
    plot.ylabel("$\omega$")
    plot.colorbar().set_ticks(scipy.arange(-60, 10, 10))
    axs.tick_params(direction="out")
    publisher.publish(prefix + "_" + str(n) + "_spectrum1", args.ext)
    plot.close()

    print("\tFrequency and wavenumber spectrum.")
    spectra_ = fft.ifft(spectra_, axis=1)
    image = fft.fftshift(spectra_)
    image = abs(image)
    image = image / image.max()
    image = 20 * scipy.log10(image)

    plot.figure()
    axs = plot.subplot(1, 1, 1)
    plot.pcolormesh(
        k, f, image,
        cmap="magma",
        rasterized=True)
    plot.xlim(-20, +20)
    plot.ylim(-60, +60)
    plot.clim(-60, 0)
    plot.xticks(scipy.arange(-20, +30, 10))
    plot.yticks(scipy.arange(-60, +80, 20))
    plot.xlabel("$k_z$")
    plot.ylabel("$\omega$")
    plot.colorbar().set_ticks(scipy.arange(-60, 10, 10))
    axs.tick_params(direction="out")
    publisher.publish(prefix + "_" + str(n) + "_spectrum2", args.ext)
    plot.close()
