#!/usr/bin/env python3


import argparse
import scipy as s
import matplotlib.pyplot as plot
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="input file",
                    type=str)
parser.add_argument("--ext",
                    help="output file extension",
                    type=str,
                    default="png")
a = parser.parse_args()


workspace = s.load(a.input)
eigenvalues = workspace["stability_eigenvalues"]
eigenvectors = workspace["stability_eigenvectors"]


publisher.init({"figure.figsize": (2.8, 2.8)})
plot.figure()

axs = plot.subplot(1, 1, 1)
plot.scatter(eigenvalues.real, eigenvalues.imag, s=1, c="black")
plot.xlabel(r"$\mbox{Re}\,\lambda$")
plot.ylabel(r"$\mbox{Im}\,\lambda$")
plot.xlim(-50, +50)
plot.ylim(-1, +1)
axs.tick_params(direction="out")

prefix = a.input.replace(".npz", "")
publisher.publish(prefix + ".eigenvalues", a.ext)
