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
                    help="plot true and estimated energy",
                    action="store_true")
parser.add_argument("--num",
                    help=("either number of modes (single argument) or "
                          "mode numbers (multiple arguments)"),
                    type=int,
                    default=10)
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


mode_numbers = range(args.num)
mode_numbers = [n for n in mode_numbers if n % 2 == 0]


coefficients = scipy.zeros((len(t), len(mode_numbers)))
for nidx, n in enumerate(mode_numbers):
    eigenvector = eigenvectors[:, n]
    for tidx, _ in enumerate(t):
        state = states[tidx, :]
        coefficient = scipy.trapz(eigenvector * state, x)
        coefficients[tidx, nidx] = abs(coefficient)

total = scipy.zeros(len(t))
for nidx, n in enumerate(mode_numbers):
    total += coefficients[:, nidx]**2

energy = scipy.zeros(len(t))
for tidx, _ in enumerate(t):
    energy[tidx] = util.energy(x, states[tidx, :])


plot.figure()
for nidx, n in enumerate(mode_numbers):
    plot.plot(t, coefficients[:, nidx], label=n)
if args.energy:
    plot.plot(t, total, color="black", linestyle="dotted", label="total")
    plot.plot(t, energy, color="black", linestyle="solid", label="energy")
plot.xlabel("$t$")
plot.show()
