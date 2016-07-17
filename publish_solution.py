#!/usr/bin/env python3


import argparse
import scipy
import matplotlib.pyplot as plot
import wells.publisher as publisher


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="Solution file",
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


publisher.init()
plot.figure()

axs = plot.subplot(1, 1, 1)
plot.plot(x, potential,
          color="gray",
          linestyle="solid",
          label="$U(z)$")
plot.plot(x, eigenvector + eigenvalue,
          color="blue",
          linestyle="solid",
          label="$\Psi_{%d}(z)$" % n)
plot.plot(x, solution + eigenvalue,
          color="red",
          label=("$A_{%d}(z; \delta_p = %.1f)$" %
                 (n, delta)))
plot.xlim(-8, +8)
plot.ylim(
    1.25 * min(min(eigenvector + eigenvalue),
               min(solution + eigenvalue),
               min(potential)),
    1.25 * max(max(eigenvector + eigenvalue),
               max(solution + eigenvalue)))
plot.xlabel("$z$")
legend = plot.legend()

legend.get_frame().set_lw(0.5)
axs.tick_params(direction="out")


output = args.input.replace(".npz", "")
publisher.publish(output, "png")
