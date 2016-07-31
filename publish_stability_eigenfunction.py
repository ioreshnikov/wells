#!/usr/bin/env python3


import argparse
import scipy
import matplotlib.pyplot as plot
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="solution file",
                    type=str)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
args = parser.parse_args()


workspace = scipy.load(args.input)
x = workspace["x"]
potential = workspace["potential"]
n = workspace["n"]
eigenvalue = workspace["eigenvalue"]
eigenvector = workspace["eigenvector"]
delta = workspace["delta"]
solution = workspace["solution"]
stability_eigenvalues = workspace["stability_eigenvalues"]
stability_eigenvectors = workspace["stability_eigenvectors"]


idx = stability_eigenvalues.imag.argmax()
eigenvalue = stability_eigenvalues[idx]
eigenvector = stability_eigenvectors[:, idx]

nx = len(x)
a = eigenvector[:nx]
b = eigenvector[nx:]
eigenvector = a + b.conjugate()


publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

plot.plot(x, eigenvector.real,
          color="black", linestyle="solid")
plot.plot(x, eigenvector.imag,
          color="orangered", linestyle="solid")
plot.xlim(-10, +10)
plot.xlabel("$z$")
plot.ylabel("$a(z) + b^{*}(z)$")
plot.show()

prefix = args.input.replace(".npz", "")
publisher.publish(prefix + ".stev", args.ext)
