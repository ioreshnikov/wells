#!/usr/bin/env python3


import argparse
import scipy as s
import wells.time_dependent as time_dependent


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


tmin = 000.0
tmax = 500.0
nt = 2**10
t = s.linspace(0, tmax - tmin, nt)

xmin = -128.00
xmax = +128.00
nx = 2**11
x = s.linspace(xmin, xmax, nx)

potential = s.zeros(x.shape)
potential = 1/2 * x**2
potential[abs(x) >= 10] = 50

delta = args.delta
pump = args.pump
loss = args.loss
input = s.zeros(x.shape, dtype=complex)
if args.input is not None:
    workspace = s.load(args.input)
    if "solution" in workspace.files:
        # Using stationary solution as an initial condition.
        # half = int(nx/2) - 1
        # input[half - 512:half + 512] = workspace["solution"]
        input = workspace["solution"][::2]
    if "states" in workspace.files:
        # Using own data file to extract the input state.
        input = workspace["states"][-1, :]
    delta = workspace["delta"]
    pump = workspace["pump"]
    loss = workspace["loss"]


absamp = 500
absorber = absamp * (1/s.cosh((x - x.min()) / 4.0) +
                     1/s.cosh((x - x.max()) / 4.0))
absorber[abs(x) < 32] = 0

# import matplotlib.pyplot as plot
# plot.semilogy(x, abs(absorber))
# plot.show()
# exit()


t, x, k, states, spectra = time_dependent.integrate(
    t, x, input, potential,
    delta, loss, pump,
    absorber)


if args.input is not None:
    filename = args.input.replace(".npz", "")
    filename = (filename +
                "_absorber=%.2f_tmin=%.2f_tmax=%.2f.npz"
                % (absamp, tmin, tmax))
else:
    filename = ("delta=%.2f_pump=%.2E_loss=%.2E.npz" %
                (args.delta, args.pump, args.loss))


workspace = {}
workspace["t"] = t
workspace["x"] = x
workspace["k"] = k
workspace["states"] = states
workspace["spectra"] = spectra
workspace["input"] = input
workspace["delta"] = args.delta
workspace["loss"] = args.loss
workspace["pump"] = args.pump
workspace["absorber"] = absorber


s.savez(filename, **workspace)
print(filename)
