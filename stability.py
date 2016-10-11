#!/usr/bin/env python3


import argparse
import scipy
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import wells.util as util


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="solution file",
                    type=str)
parser.add_argument("--trust",
                    help="skip the file if the spectrum is already present",
                    action='store_true')
args = parser.parse_args()


workspace = scipy.load(args.input)
x = workspace["x"]
potential = workspace["potential"]
delta = workspace["delta"]
solution = workspace["solution"]
try:
    loss = workspace["loss"]
except:
    loss = 0


x = x[::2]
potential = potential[::2]
solution = solution[::2]


if args.trust:
    files = workspace.files
    if ("stability_eigenvalues" in files and
        "stability_eigenvectors" in files):
        eigenvalues = workspace["stability_eigenvalues"]
        stable = all(eigenvalues.imag < 0)
        workspace_ = {}
        for name in files:
            workspace_[name] = workspace[name]
        workspace_["stable"] = stable
        scipy.savez(args.input, **workspace)
        exit()


nx = len(x)
dx = x[1] - x[0]


laplacian = util.laplacian(nx, dx)
potential = sparse.diags(potential, 0, (nx, nx))
power = sparse.diags(abs(solution)**2, 0)
square = sparse.diags(solution**2, 0)
delta = delta * sparse.eye(nx, nx)
loss = loss * sparse.eye(nx, nx)

l = -1/2 * laplacian + potential - 2*power + delta
operator = sparse.bmat(
    [[l - 1j * loss, -square],
     [square.conjugate(), -l - 1j * loss]])

k = 64
eigenvalues, eigenvectors = linalg.eigs(operator, k=k, which="SM")
stable = all(eigenvalues.imag < 0)


workspace_ = {}
for name in workspace.files:
    workspace_[name] = workspace[name]
workspace_["stability_eigenvalues"] = eigenvalues
workspace_["stability_eigenvectors"] = eigenvectors
workspace_["stable"] = stable


scipy.savez(args.input, **workspace_)
