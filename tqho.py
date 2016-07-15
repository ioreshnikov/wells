#!/usr/bin/env python3


import scipy
import matplotlib.pyplot as plot
import wells.time_independent as time_independent


x = scipy.linspace(-32, +32, 2**11)
u = scipy.zeros(x.shape)
u = 1/2 * x**2
u[abs(x) >= 10] = 50

n = 127
eigenvalues, eigenvectors = time_independent.fdlp(x, u, n, boundary="box")


plot.figure()
plot.scatter(eigenvalues.real, eigenvalues.imag)
plot.show()


plot.figure()
plot.plot(x, u)
for i in range(n):
    e = eigenvalues[i]
    f = eigenvectors[:, i]
    f = f / 2 / abs(f).max()
    plot.plot(x, f + e)
plot.show()
