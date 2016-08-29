#!/usr/bin/env python3


import argparse
import scipy as s
import wells.propagate as propagate


parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    help="Read initial condition from a file",
                    type=str)
parser.add_argument("--delta",
                    help="Detuning between the pump and the resonance",
                    type=float,
                    default=0.0)
parser.add_argument("--pump",
                    help="Pump",
                    type=float,
                    default=0.0)
parser.add_argument("--loss",
                    help="Linear losses",
                    type=float,
                    default=0.0)
parser.add_argument("--mint",
                    help="Start time",
                    type=float,
                    default=0.0)
parser.add_argument("--maxt",
                    help="End time",
                    type=float,
                    default=50.0)
parser.add_argument("--nt",
                    help="Number of time steps in the output",
                    type=float,
                    default=2**12)
args = parser.parse_args()


xmin = -128.00
xmax = +128.00
nx = 2**12
x = s.linspace(xmin, xmax, nx)


potential = s.zeros(x.shape)
potential = 1/2 * x**2
potential[abs(x) >= 10] = 50


delta = args.delta
pump = args.pump
loss = args.loss

input = s.zeros(x.shape, dtype=complex)
background = 0
filename = ""


if args.input is not None:
    workspace = s.load(args.input)
    if "solution" in workspace.files:
        # Using stationary solution as an initial condition.
        input = workspace["solution"]
        background = input[(x > 0.5 * xmax) & (x < 0.75 * xmax)]
        background = s.mean(abs(background))
    if "states" in workspace.files:
        # Using own data file to extract the input state.
        input = workspace["states"][-1, :]
        background = workspace["background"]
    delta = workspace["delta"]
    pump = workspace["pump"]
    loss = workspace["loss"]


filename = (
    filename +
    "delta=%.2f_pump=%.2E_loss=%.2E_mint=%.2f_maxt_%.2f_nt=%d.npz" %
    (delta, pump, loss, args.mint, args.maxt, args.nt))


absorber = (1000 *
            (1/s.cosh((x - x.min()) / 8.0) +
             1/s.cosh((x - x.max()) / 8.0)))
absorber[abs(x) < 64] = 0


t = s.linspace(args.mint, args.maxt, args.nt)
k, states, spectra = propagate.pnlse.integrate(
    t - t.min(), x, input, potential,
    delta, pump, loss,
    absorber, background)


workspace = {}
workspace["t"] = t
workspace["x"] = x
workspace["k"] = k
workspace["states"] = states
workspace["spectra"] = spectra
workspace["input"] = input
workspace["background"] = background
workspace["delta"] = delta
workspace["pump"] = pump
workspace["loss"] = loss
workspace["absorber"] = absorber


s.savez(filename, **workspace)
print(filename)
