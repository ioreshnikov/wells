import scipy
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg


def finite_difference_linear_problem(x, u, n, which="SM", boundary="box"):
    nx = len(x)
    dx = x[1] - x[0]

    if boundary == "box":
        # In case of infinite-box boundary conditions we need to null
        # the first and the last column. This will lead for the solver
        # to find two additional spurious eigenstates with eigenvalues
        # near zero. We need to throw them away later.
        n = n + 2
        nx = nx + 2

        x_ = scipy.zeros(nx)
        x_[1:-1] = x
        x = x_

        u_ = scipy.zeros(nx)
        u_[1:-1] = u
        u = u_

    laplacian = sparse.diags([1, -2, 1], [-1, 0, +1], (nx, nx))
    laplacian = 1/dx**2 * laplacian
    potential = sparse.diags(u, 0, (nx, nx))
    hamiltonian = -1/2 * laplacian + potential

    if boundary == "box":
        # The only modification to the Hamiltonian is to null the
        # first and the last column.
        hamiltonian[:, 0] = 0
        hamiltonian[:, nx-1] = 0

    if boundary == "periodic":
        # In case of periodic boundary conditions we need to modify
        # both rows and columns of the Hamiltonian.
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
        eigenvalues = eigenvalues[2:]
        eigenvectors = eigenvectors[1:-1, 2:]

    return eigenvalues, eigenvectors


fdlp = finite_difference_linear_problem
