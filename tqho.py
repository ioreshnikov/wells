#!/usr/bin/env python3


import argparse

import scipy
import scipy.optimize as optimize
import scipy.sparse as sparse

import wells.time_independent as time_independent
import wells.util as util


parser = argparse.ArgumentParser()
parser.add_argument("--delta",
                    help="Detuning between the pump and the resonance",
                    type=float,
                    default=0.0)
parser.add_argument("--input",
                    help="Read initial condition from a file",
                    type=str)
parser.add_argument("--n",
                    help="Mode number",
                    type=int,
                    default=0)
args = parser.parse_args()


# Coordinate grid parameters.
minx = -128
maxx = +128
nx = 2**11
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


# Nonlinear operator.
def l0(state):
    focusing = sparse.diags(abs(state)**2, 0, (nx, nx))
    operator = (
        -1/2 * laplacian +
        potential -
        focusing +
        delta)
    return operator.dot(state)


eigenvalue = eigenvalues[args.n]
eigenvector = eigenvectors[:, args.n]
if args.input is not None and util.energy(x, solution) > 0.1:
    initial = solution
else:
    initial = eigenvector


solution = optimize.newton_krylov(l0, initial)
if solution is None:
    exit()


filename = "mode=%d_delta=%.2f.npz" % (args.n, args.delta)
workspace = {}
workspace["x"] = x
workspace["potential"] = u
workspace["n"] = args.n
workspace["eigenvalue"] = eigenvalue
workspace["eigenvector"] = eigenvector
workspace["delta"] = args.delta
workspace["solution"] = solution


scipy.savez(filename, **workspace)
print(filename)
