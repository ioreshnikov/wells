import scipy.sparse as sparse


def laplacian(n, d=1.0):
    laplacian = sparse.diags([1, -2, 1], [-1, 0, +1], (n, n))
    laplacian = 1/d**2 * laplacian
    return laplacian
