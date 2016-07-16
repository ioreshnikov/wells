import scipy
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import wells.util

import sys


def finite_difference_linear_problem(x, u, n, which="SM", boundary="box"):
    nx = len(x)
    dx = x[1] - x[0]

    if boundary == "box":
        # In case of infinite-box boundary conditions we need to null
        # the first and the last column. This will lead for the solver
        # to find two additional spurious eigenstates with eigenvalues
        # near zero. Moreover, the first and the last digits of the
        # eigenvector won't contain any useful information, so we will
        # need to throw them away. To maintain the length of the
        # eigenvector we increase the number of elements in the
        # potential vector by 2 (dummy first and last values).
        n = n + 2    # spurious eigenstates
        nx = nx + 2  # extra ticks at beginning and end.

        u_ = scipy.zeros(nx)
        u_[1:-1] = u
        u = u_

    laplacian = wells.util.laplacian(nx, dx)
    potential = sparse.diags(u, 0, (nx, nx))
    hamiltonian = -1/2 * laplacian + potential

    if boundary == "box":
        # The only modification to the Hamiltonian is to null the
        # first and the last column.
        hamiltonian[:, 0] = 0
        hamiltonian[:, nx-1] = 0

    if boundary == "periodic":
        # In case of periodic boundary conditions we need to modify
        # both rows and columns of the Hamiltonian by inserting -1/dx
        # at all the zero boundary elements of the matrix.
        hamiltonian[0, 1:] = -1/dx
        hamiltonian[1:, 0] = -1/dx
        hamiltonian[-1, :-1] = -1/dx
        hamiltonian[:-1, -1] = -1/dx

    eigenvalues, eigenvectors = linalg.eigs(hamiltonian, n, which=which)

    # Sort the eigenstates based on absolute value of the eigenvalue.
    order = abs(eigenvalues).argsort()
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    if boundary == "box":
        # Throw the spurious states and buffer elements of the vectors.
        eigenvalues = eigenvalues[2:]
        eigenvectors = eigenvectors[1:-1, 2:]

    return eigenvalues, eigenvectors


fdlp = finite_difference_linear_problem


def newton_conjugate_gradient(
        x, u, l0, l1,
        precondconst=3,
        nerror=1E-10, cgerror=1E-2,
        maxniters=16, maxcgiters=256):
    nx = len(x)
    dx = x[1] - x[0]

    # Compute preconditioning operator M.
    laplacian = wells.util.laplacian(nx, dx)
    m = precondconst * sparse.eye(nx) - laplacian
    im = sparse.linalg.inv(m)

    niter = 0
    while True:
        # Newton iteration. Apply nonlinear operator and check whether
        # residue is smaller (everywhere) than desirable Newton method
        # error.
        if niter >= maxniters:
            return None

        r = -l0(u)
        nerror_ = max(abs(r))
        if nerror_ < nerror:
            return u

        # Otherwise, start CG search for an optimal correction.
        du = 0 * u
        d = im.dot(r)

        initial = r.conjugate().dot(d)
        cgiter = 0
        while True:
            # Conjugate-gradient iteration. I cannot explain anything
            # that happens here :)
            if cgiter >= maxcgiters:
                break

            l1d = l1(u, d)
            au = r.conjugate().dot(d)
            ad = d.conjugate().dot(l1d)
            a = au / ad
            du = du + a * d
            r = r - a * l1d
            d_ = im.dot(r)
            bu = r.conjugate().dot(d_)
            b = bu / au
            d = d_ + b * d

            cgerror_ = bu
            if cgerror_ < cgerror * initial:
                break
            sys.stderr.write(
                "%8d %e %12d %e %e\n" % (
                    niter,
                    nerror_,
                    cgiter,
                    cgerror_,
                    cgerror * initial))

            cgiter = cgiter + 1

        u = u + du
        niter = niter + 1


ncg = newton_conjugate_gradient
