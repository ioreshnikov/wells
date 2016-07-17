#!/usr/bin/env python3


import argparse

import scipy
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
minx = -32
maxx = +32
nx = 2**10
dx = (minx - maxx) / (nx - 1)

# Coordinate grid.
x = scipy.linspace(minx, maxx, nx)


# Potential.
u = scipy.zeros(x.shape)
u = 1/2 * x**2
u[abs(x) >= 10] = 50


# Find the first n eigenstates to use as starting point.
eigenvalues, eigenvectors = time_independent.fdlp(x, u, args.n + 1, boundary="box")


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
laplacian = util.laplacian(nx, dx, dtype=complex)
potential = sparse.diags(u, 0, (nx, nx), dtype=complex)
delta = args.delta * sparse.eye(nx, nx, dtype=complex)


# Nonlinear operator.
def l0(state):
    focusing = sparse.diags(abs(state)**2, 0, (nx, nx))
    operator = (
        -1/2 * laplacian +
        potential -
        focusing +
        delta)
    return operator


# Linearization operator.
def l1(state):
    focusing = sparse.diags(3 * abs(state)**2, 0, (nx, nx))
    operator = (
        -1/2 * laplacian +
        potential -
        focusing +
        delta)
    return operator


# Preconditioning operator
precondition = 3 * sparse.eye(nx, nx, dtype=complex) - laplacian


eigenvalue = eigenvalues[args.n]
eigenvector = eigenvectors[:, args.n]
eigenvector = eigenvector
solution = time_independent.ncg(eigenvector, l0, l1, precondition)


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