#!/usr/bin/env python3


import argparse

import scipy as s
import wells.time_dependent as time_dependent

import matplotlib.pyplot as plot


parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    help="Read initial condition from a file",
                    type=str)
parser.add_argument("--delta",
                    help="Detuning between the pump and the resonance",
                    type=float,
                    default=0.0)
parser.add_argument("--loss",
                    help="Linear losses",
                    type=float,
                    default=0.0)
parser.add_argument("--pump",
                    help="Pump",
                    type=float,
                    default=0.0)
args = parser.parse_args()


tmin = 0.0
tmax = 8.0
nt = 2**8
t = s.linspace(tmin, tmax, nt)

xmin = -128.00
xmax = +128.00
nx = 2**12
x = s.linspace(xmin, xmax, nx)

potential = s.zeros(x.shape)
potential = 1/2 * x**2
potential[abs(x) >= 10] = 50


input = s.zeros(x.shape, dtype=complex)
if args.input is not None:
    workspace = s.load(args.input)
    solution = workspace["solution"]
    input[nx/2 - 512:nx/2 + 512] = solution


t, x, k, states, spectra = time_dependent.integrate(
    t, x, input, potential, args.delta, args.loss, args.pump)

image = abs(states)
image = image / image.max()

plot.figure()
plot.pcolormesh(x, t, image, cmap="magma")
plot.colorbar()
plot.xlim(-32, +32)
plot.show()
