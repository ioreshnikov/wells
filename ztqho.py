#!/usr/bin/env python3


import argparse

import scipy
import scipy.sparse as sparse
import scipy.optimize as optimize

import wells.time_independent as time_independent
import wells.util as util


parser = argparse.ArgumentParser()
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
parser.add_argument("--input",
                    help="Read initial condition from a file",
                    type=str)
parser.add_argument("--n",
                    help="Mode number",
                    type=int,
                    default=0)
parser.add_argument("--scale",
                    help="Initial guess scaling",
                    type=float,
                    default=0.0)
parser.add_argument("--phase",
                    help="Initial guess phase rotation",
                    type=float,
                    default=0.0)
parser.add_argument("--label",
                    help="Auxiliary label",
                    type=str,
                    default="0")
args = parser.parse_args()


# Coordinate grid parameters.
minx = -128
maxx = +128
nx = 2**12
dx = (minx - maxx) / (nx - 1)

# Coordinate grid.
x = scipy.linspace(minx, maxx, nx)


# Potential.
u = scipy.zeros(x.shape)
u = 1/2 * x**2
u[abs(x) >= 10] = 50


# Load input file to use for initial guess.
if args.input is not None:
    workspace = scipy.load(args.input)
    solution = workspace["solution"]


# Find the first n eigenstates to use as starting point.
eigenvalues, eigenvectors = time_independent.fdlp(
    x, u, args.n + 1, boundary="box")
eigenvectors = eigenvectors.real


# Normalize the modes.
for n in range(args.n + 1):
    eigenvalue = eigenvalues[n]
    eigenvector = eigenvectors[:, n]
    eigenvector = (
        scipy.sqrt(
            abs(eigenvalue) /
            util.energy(x, eigenvector)) *
        eigenvector)
    eigenvectors[:, n] = eigenvector


# Define operators for the Newton-CG method.
laplacian = util.laplacian(nx, dx)
potential = sparse.diags(u, 0, (nx, nx))
delta = args.delta * sparse.eye(nx, nx)
loss = args.loss * sparse.eye(nx, nx)
pump = args.pump * scipy.ones(2*nx)
pump[nx:] = 0

laplacian = sparse.bmat([[laplacian, None], [None, laplacian]])
potential = sparse.bmat([[potential, None], [None, potential]])
delta = sparse.bmat([[delta, None], [None, delta]])
loss = sparse.bmat([[None, loss], [-loss, None]])


# Nonlinear operator.
def l0(state):
    real = state[:nx]
    imag = state[nx:]
    power = (real**2 + imag**2)
    focusing = sparse.diags(power, 0, (nx, nx))
    focusing = sparse.bmat([[focusing, None], [None, focusing]])
    operator = (
        -1/2 * laplacian +
        potential -
        focusing +
        delta +
        loss)
    return operator.dot(state) - pump


# Preconditioning operator
eigenvalue = eigenvalues[args.n]
eigenvector = eigenvectors[:, args.n]
initial = scipy.zeros(2*nx)
if args.input is not None:
    solution = scipy.exp(1j * args.phase) * args.scale * solution
    # real = scipy.zeros(nx)
    # imag = scipy.zeros(nx)
    # real[int(nx/2-nx/4):int(nx/2+nx/4)] = solution.real
    # imag[int(nx/2-nx/4):int(nx/2+nx/4)] = solution.imag
    # initial[:nx] = real
    # initial[nx:] = imag
    initial[:nx] = solution.real
    initial[nx:] = solution.imag
else:
    initial[:] = 0


# Solve using Newton-Krylov method.
solution = optimize.newton_krylov(l0, initial)


filename = ("mode=%d_delta=%.2f_pump=%.2E_loss=%.2E_%s.npz" %
            (args.n, args.delta, args.pump, args.loss, args.label))
workspace = {}
workspace["x"] = x
workspace["potential"] = u
workspace["n"] = args.n
workspace["eigenvalue"] = eigenvalue
workspace["eigenvector"] = eigenvector
workspace["delta"] = args.delta
workspace["solution"] = solution[:nx] + 1j * solution[nx:]
workspace["pump"] = args.pump
workspace["loss"] = args.loss


scipy.savez(filename, **workspace)
print(filename)
