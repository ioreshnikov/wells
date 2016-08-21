#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
import scipy.signal
import scipy.special
import wells.time_independent as time_independent
import wells.publisher as publisher
import wells.util as util


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="raw propagation data",
                    type=str)
parser.add_argument("--energy",
                    help="plot true energy",
                    action="store_true")
parser.add_argument("--estimate",
                    help="plot estimated energy",
                    action="store_true")
parser.add_argument("--min",
                    help="minimum t coordinate",
                    type=float,
                    default=0.0)
parser.add_argument("--num",
                    help=("either number of modes (single argument) or "
                          "mode numbers (multiple arguments)"),
                    type=int,
                    default=10)
parser.add_argument("--label",
                    help="number of modes to label",
                    type=int,
                    default=0)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


workspace = scipy.load(args.input)
t = workspace["t"]
x = workspace["x"]
states = workspace["states"]


u = scipy.zeros(x.shape)
u = 1/2 * x**2
u[abs(x) >= 10] = 50

eigenvalues, eigenvectors = time_independent.fdlp(
    x, u, args.num + 1, boundary="box")
eigenvectors = eigenvectors.real

for n in range(args.num + 1):
    eigenvalue = eigenvalues[n]
    eigenvector = eigenvectors[:, n]
    eigenvector /= scipy.sqrt(util.energy(x, eigenvector))
    eigenvectors[:, n] = eigenvector


mode_numbers = scipy.arange(args.num)

coefficients = scipy.zeros((len(t), len(mode_numbers)))
for n in mode_numbers:
    eigenvector = eigenvectors[:, n]
    for idx, _ in enumerate(t):
        state = states[idx, :]
        coefficient = scipy.trapz(eigenvector * state, x)
        coefficients[idx, n] = abs(coefficient)
# coefficients[coefficients == 0] = None
# coefficients = scipy.log10(coefficients)


estimate = scipy.zeros(len(t))
for n in mode_numbers:
    estimate += coefficients[:, n]**2

energy = scipy.zeros(len(t))
for idx, _ in enumerate(t):
    energy[idx] = util.energy(x, states[idx, :])


# Sort the modes by maximum value at zero.
idx = scipy.argsort(coefficients[0])[::-1]
mode_numbers = mode_numbers[idx]


# Moving average smoothing.
# window = scipy.ones(64) / 64
# for n in mode_numbers:
#     coefficients[:, n] = scipy.signal.convolve(
#         coefficients[:, n], window, mode="same")


publisher.init({"figure.figsize": (2.8, 1.6)})
plot.figure()

tticks = scipy.arange(args.min, t.max() + 10, 10)
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

axs = plot.subplot(1, 1, 1)
for i, n in enumerate(mode_numbers):
    if n % 2 == 0:
        color = "black"
    else:
        color = "red"
    plot.semilogy(t, coefficients[:, n], color=color, label=str(n))
    if i < args.label:
        idx = int(len(t) * 0.05)
        x = t[idx] + args.min
        y = coefficients[idx, n]
        plot.text(x, y, str(n),
                  ha="center", va="center",
                  bbox=bbox, fontsize="x-small")
if args.energy:
    plot.plot(t, energy, color="black", linestyle="dashed")
if args.estimate:
    plot.plot(t, estimate, color="black", linestyle="dotted")
plot.xlim(args.min, t.max())
plot.xticks(tticks)
plot.xlabel(r"$t$")
plot.ylim(10**-6, 10)
plot.ylabel(r"$\left< A, \Psi_n \right>$")
# plot.legend()
axs.tick_params(direction="out")
plot.show()

prefix = args.input.replace(".npz", "")
publisher.publish(prefix + ".modes", args.ext)
