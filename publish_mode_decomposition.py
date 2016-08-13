#!/usr/bin/env python3


import argparse
import matplotlib.pyplot as plot
import scipy
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

estimate = scipy.zeros(len(t))
for n in mode_numbers:
    estimate += coefficients[:, n]**2

energy = scipy.zeros(len(t))
for idx, _ in enumerate(t):
    energy[idx] = util.energy(x, states[idx, :])


# Sort the modes by maximum value at zero.
idx = scipy.argsort(coefficients[0])[::-1]
mode_numbers = mode_numbers[idx]


publisher.init({"figure.figsize": (1.4, 2.4)})
plot.figure()

tticks = scipy.arange(args.min, t.max() + 10, 10)
cticks = scipy.arange(0.0, coefficients.max() + 1.0, 1.0)
bbox = dict(boxstyle="circle, pad=0.2", lw="0.5", fc="white")

axs = plot.subplot(1, 1, 1)
for i, n in enumerate(mode_numbers):
    if n % 2 == 0:
        linestyle = "solid"
    else:
        linestyle = "dashed"
    plot.plot(coefficients[:, n], t, label=str(n))
    if i < args.label:
        idx = int(len(t) * 0.1)
        x = coefficients[idx, n]
        y = t[idx] + args.min
        plot.text(x, y, str(n),
                  ha="center", va="center",
                  bbox=bbox, fontsize="x-small")
if args.energy:
    plot.plot(energy, t, color="black", linestyle="dashed")
if args.estimate:
    plot.plot(estimate, t, color="black", linestyle="dotted")
plot.xticks(cticks)
plot.ylim(args.min, t.max())
plot.yticks(tticks)
plot.xlabel(r"$\left< A, \Psi_n \right>$")
plot.ylabel(r"$t$")
# plot.legend()
axs.tick_params(direction="out")

prefix = args.input.replace(".npz", "")
publisher.publish(prefix + ".modes", args.ext)
