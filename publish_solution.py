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
n = workspace["n"]
delta = workspace["delta"]
solution = workspace["solution"]

complex_ = False
if max(abs(solution.imag)) > 1E-3:
    complex_ = True


publisher.init()
plot.figure()

axs = plot.subplot(1, 1, 1)
if complex_:
    plot.plot(x, solution.real,
              color="black",
              linestyle="solid",
              label=("$\Re A_{%d}(z; \delta_p = %.1f)$" %
                     (n, delta)))
    plot.plot(x, solution.imag,
              color="black",
              linestyle="dotted",
              label=("$\Im A_{%d}(z; \delta_p = %.1f)$" %
                     (n, delta)))
else:
    plot.plot(x, solution,
              color="black",
              label=("$A_{%d}(z; \delta_p = %.1f)$" %
                     (n, delta)))
plot.xlim(-16, +16)
plot.xlabel("$z$")
legend = plot.legend()

legend.get_frame().set_lw(0.5)
axs.tick_params(direction="out")


output = args.input.replace(".npz", "")
publisher.publish(output, "png")
