import scipy
import scipy.fftpack as fft
import scipy.sparse as sparse


def laplacian(n, d=1.0, dtype=None):
    laplacian = sparse.diags(
        [1, -2, 1],
        [-1, 0, +1],
        (n, n),
        dtype=dtype)
    laplacian = 1/d**2 * laplacian
    return laplacian


def energy(x, u):
    return scipy.trapz(abs(u)**2, x)
