import scipy as s
import scipy.fftpack as fft
import scipy.integrate
import sys


def integrate(t, x, input, potential, delta, loss, pump):
    nt = len(t)
    nx = len(x)

    dx = x[1] - x[0]

    k = 2*s.pi * fft.fftfreq(nx, dx)
    d = - delta - 1/2 * k**2

    spectrum = fft.fft(input)
    spectrum_ = spectrum

    def rhs(t, spectrum_):
        exp_ = s.exp(1j * d * t)
        spectrum = exp_ * spectrum_
        state = fft.ifft(spectrum)
        nonlinearity = abs(state)**2 * state
        nonlinearity += - potential * state
        nonlinearity += 1j * loss * state
        nonlinearity += pump
        return 1j * 1/exp_ * fft.fft(nonlinearity)

    solver = scipy.integrate.ode(rhs)
    solver.set_integrator("zvode",
                          rtol=1E-6,
                          atol=1E-10,
                          nsteps=2048)
    solver.set_initial_value(spectrum_, 0)

    spectra_ = s.zeros((nt, nx), dtype=complex)
    spectra_[0, :] = spectrum_
    for i in range(1, nt):
        sys.stderr.write("\rIntegrating: %-3.2f%%" % (100 * i/nt))
        spectra_[i, :] = solver.integrate(t[i])
    sys.stderr.write("\r")

    spectra = s.zeros((nt, nx), dtype=complex)
    states = s.zeros((nt, nx), dtype=complex)
    for i in range(0, nt):
        spectra[i, :] = s.exp(1j * d * t[i]) * spectra_[i, :]
        states[i, :] = fft.ifft(spectra[i, :])
        spectra[i, :] = 1/nt * fft.fftshift(spectra[i, :])
    k = fft.fftshift(k)

    return t, x, k, states, spectra
