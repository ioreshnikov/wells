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

complex_ = False
if max(abs(solution.imag)) > 1E-3:
    complex_ = True


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
if complex_:
    plot.plot(x, solution.real + eigenvalue,
              color="red",
              linestyle="solid",
              label=("$\Re A_{%d}(z; \delta_p = %.1f)$" %
                     (n, delta)))
    plot.plot(x, solution.imag + eigenvalue,
              color="red",
              linestyle="dotted",
              label=("$\Im A_{%d}(z; \delta_p = %.1f)$" %
                     (n, delta)))
else:
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
