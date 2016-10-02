#!/usr/bin/env python3


import scipy
import sys


z0 = float(sys.argv[1])
input = sys.argv[2]


ws = scipy.load(input)
t = ws["t"]
x = ws["x"]
y = ws["states"]


idx = abs(x - z0).argmin()
y = y[:, idx]


output = scipy.zeros((len(t), 3))
output[:, 0] = t
output[:, 1] = y.real
output[:, 2] = y.imag


filename = "slice.txt"
header = """Complex field at z=%.2f, the first row is dimensionless time `t`,
the second and the third ones are real and complex parts of A(z, t),
respectively."""
header = header % x[idx]
scipy.savetxt("slice.txt", output, header=header)
