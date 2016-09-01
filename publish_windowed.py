#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import scipy.fftpack as fft
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="raw propagation data",
                    type=str)
parser.add_argument("--win",
                    help="window size",
                    type=float,
                    default=50.0)
parser.add_argument("--one",
                    help="plot only first window",
                    action="store_true")
parser.add_argument("--timedomain",
                    help="plot time domain",
                    action="store_true")
parser.add_argument("--spectrum0",
                    help="plot frequency spectrum at fixed z",
                    action="store_true")
parser.add_argument("--z",
                    help="fixed z to plot the spectrum at",
                    type=float,
                    default=0.0)
parser.add_argument("--spectrum1",
                    help="plot frequency spectrum",
                    action="store_true")
parser.add_argument("--spectrum2",
                    help="plot frequency-wavenumber spectrum",
                    action="store_true")
parser.add_argument("--subsample",
                    help="use only every nth digit",
                    type=int,
                    default=1)
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
background = workspace["background"]


winsize = args.win / (t.max() - t.min()) * len(t)
winsize = int(winsize)
num_windows = len(t) / winsize
num_windows = int(num_windows)

f = fft.fftfreq(winsize, t[1] - t[0])
f = 2 * scipy.pi * fft.fftshift(f)


publisher.init({"figure.figsize": (2.8, 2.4)})
prefix = args.input.replace(".npz", "")

for n in range(num_windows):
    print("Window: %d/%d" % (n + 1, num_windows))
    prefix_ = prefix
    if not args.one:
        prefix_ = prefix_ + "_" + str(n)

    start = n * winsize
    stop = start + winsize
    window = slice(start, stop)

    t_ = t[window]
    states_ = states[window, :]
    spectra_ = fft.fft(states_, axis=0)

    t_ = t_[::args.subsample]
    f = f[::args.subsample]
    states_ = states_[::args.subsample, :]
    spectra_ = spectra_[::args.subsample, :]

    if args.timedomain:
        print("\tTime domain.")
        image = abs(states_)
        image = image / image.max()
        image = 20 * scipy.log10(image)

        figure = plot.figure()
        axs = plot.subplot(1, 1, 1)
        plot.pcolormesh(
            x, t_, image,
            cmap="magma",
            rasterized=True)
        plot.xlim(-20, +20)
        plot.xticks(scipy.arange(-20, +21, 10))
        plot.ylim(t_.min(), t_.max())
        plot.yticks(
            scipy.arange(
                round(t_.min()),
                round(t_.max()) + 1,
                10))
        plot.clim(-60, 0)
        plot.colorbar().set_ticks(scipy.arange(-60, 1, 20))
        plot.xlabel("$z$")
        plot.ylabel("$t$")
        axs.tick_params(direction="out")
        publisher.publish(
            prefix_ + "_timedomain",
            args.ext)
        plot.close()
        del image

    if args.spectrum0:
        print("\tFrequency spectrum at z=%.2f" % args.z)
        idx = abs(x - args.z).argmin()
        spectrum = spectra_[:, idx]

        image = fft.fftshift(spectrum)
        image = abs(image)
        image = image / image.max()

        plot.figure()
        axs = plot.subplot(1, 1, 1)
        plot.plot(f, image)
        plot.xlim(-60, 10)
        plot.xlabel(r"$\omega$")
        axs.tick_params(direction="out")
        publisher.publish(
            prefix_ + "_spectrum0",
            args.ext)
        plot.close()
        del image

    if args.spectrum1:
        print("\tFrequency spectrum.")
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
        plot.xticks(scipy.arange(-20, +30, 10))
        plot.ylim(-100, +50)
        plot.yticks(scipy.arange(-100, +51, 25))
        plot.clim(-80, 0)
        plot.colorbar().set_ticks(scipy.arange(-80, 1, 20))
        plot.xlabel("$z$")
        plot.ylabel("$\omega$")
        axs.tick_params(direction="out")
        publisher.publish(
            prefix_ + "_spectrum1",
            args.ext)
        plot.close()
        del image

    if args.spectrum2:
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
        plot.xticks(scipy.arange(-20, +30, 10))
        plot.ylim(-100, +50)
        plot.yticks(scipy.arange(-100, +51, 25))
        plot.clim(-80, 0)
        plot.colorbar().set_ticks(scipy.arange(-80, 1, 20))
        plot.xlabel("$k_z$")
        plot.ylabel("$\omega$")
        axs.tick_params(direction="out")
        publisher.publish(
            prefix_ + "_spectrum2",
            args.ext)
        plot.close()
        del image

    if args.one:
        exit()
