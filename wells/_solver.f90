module fftw
  implicit none
  include "fftw3.f"

  integer*8, private :: fft_plan = 0
  integer*8, private :: ifft_plan = 0
contains
  subroutine fftinit(input, output)
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    call dfftw_plan_dft_1d(     &
         fft_plan, size(input), &
         input, output,         &
         FFTW_FORWARD, FFTW_ESTIMATE)
  end subroutine fftinit

  subroutine ifftinit(input, output)
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    call dfftw_plan_dft_1d(      &
         ifft_plan, size(input), &
         input, output,          &
         FFTW_BACKWARD, FFTW_ESTIMATE)
  end subroutine ifftinit

  subroutine fft(input, output)
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    if (fft_plan == 0) then
       call fftinit(input, output)
    end if
    call dfftw_execute_dft(fft_plan, input, output)
  end subroutine fft

  subroutine ifft(input, output)
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    if (ifft_plan == 0) then
       call ifftinit(input, output)
    end if
    call dfftw_execute_dft(ifft_plan, input, output)
    output = output / size(output)
  end subroutine ifft

  subroutine fftfreq(n, step, f)
    integer :: n
    double precision :: step
    double precision, dimension(1:n) :: f

    integer :: i
    do i = 1, n
       if (i <= n/2) then
          f(i) = i - 1
       else
          f(i) = i - 1 - n
       end if
    end do
    f = f / (n * step)
  end subroutine fftfreq
end module fftw


module util
  implicit none

  integer, parameter :: stderr = 0
  integer, parameter :: stdin = 5
  integer, parameter :: stdout = 6

  double complex,   parameter :: im = (0.0, 1.0)
  double precision, parameter :: pi = 4 * atan(1.0)

  integer*8, private :: total_allocated
contains
  subroutine report_allocated(size, label)
    integer*8 :: size
    character(len=*) :: label

    total_allocated = total_allocated + size
    write (stderr, "(A15 I10 ' kB for ' A)") &
          'Allocated:', size/1024, label
  end subroutine report_allocated

  subroutine report_total_allocated()
    write (stderr, "(A15 I10 ' kB')") &
          'Total:', total_allocated / 1024
  end subroutine report_total_allocated

  function fac(n)
    integer :: n, i, fac
    fac = 1
    do i = 1, n
       fac = i * fac
    end do
  end function fac
end module util


module ccgnlse
  use fftw
  use util
  implicit none
contains
  subroutine integrate( &
       t, x, y0, dt,    & ! Grids, initial condition and step
       betas,           & ! Diffraction (dispersion) operator
       gamma,           & ! Nonlinearity coefficient
       u,               & ! External potential
       pump, loss,      & ! Pump and loss
       absrb, bg,       & ! Absorbing boundary layer
       ys)                ! Output matrix
    double precision, dimension(:), intent(in) :: t, x
    double complex, dimension(:), intent(in) :: y0
    double precision, intent(in) :: dt

    double precision, dimension(:), intent(in) :: betas, u, absrb
    double precision, intent(in) :: gamma, pump, loss, bg

    double complex, dimension(size(t), size(x)), intent(out) :: ys

    integer :: nt, nx, i, n
    double precision :: dx, t_
    double precision, dimension(:), allocatable :: f, d
    double complex, dimension(:), allocatable :: y, s, e, nl
    logical :: use_absrb = .FALSE., use_u = .FALSE.
    real :: start, stop

    nt = size(t)
    nx = size(x)
    dx = x(2) - x(1)
    t_ = t(1)

    allocate(f(nx))
    call fftfreq(nx, dx, f)
    f = 2*pi * f

    allocate(d(nx))
    allocate(e(nx))
    d = 0.0
    do i = 1, size(betas)
       n = i - 1
       d = d + 1.0/fac(n) * betas(i) * f**n
    end do
    e = exp(im * d * dt/2)

    if ((size(u)) == nx .and. maxval(abs(u)) > 0) then
       use_u = .TRUE.
    end if

    if (size(absrb) == nx .and. maxval(abs(absrb)) > 0) then
       use_absrb = .TRUE.
    end if

    allocate(y(nx))
    allocate(s(nx))
    allocate(nl(nx))
    y = y0
    ys(1, :) = y0

    write (stderr, "(A)") repeat("-", 64)
    call report_allocated(sizeof(t),  "time grid")
    call report_allocated(sizeof(x),  "coordinate grid")
    call report_allocated(sizeof(f),  "frequency grid")
    call report_allocated(sizeof(ys), "output states matrix")
    call report_allocated(sizeof(y),  "current state")
    call report_allocated(sizeof(s),  "current spectrum")
    call report_allocated(sizeof(d),  "diffraction operator")
    call report_allocated(sizeof(e),  "auxiliary exponential")
    call report_allocated(sizeof(nl), "nonlinear term")
    write (stderr, "(A)") repeat("=", 64)
    call report_total_allocated()

    call cpu_time(start)
    write (stderr, *)
    write (stderr, "(A)") repeat("-", 64)
    do i = 1, nt-1
       do while (t_ < t(i+1))
          ! Dispersive half-step.
          call fft(y, s)
          s = e * s
          call ifft(s, y)

          ! Nonlinearity and absorption.
          nl = gamma * abs(y)**2
          if (use_u) then
             nl = nl - u
          end if
          if (use_absrb) then
             nl = nl + im * absrb * (abs(y) - bg)
          end if
          y = exp(im * nl * dt) * y
          y = exp(-loss * dt) * y + im * pump * dt

          ! Dispersive half-step.
          call fft(y, s)
          s = e * s
          call ifft(s, y)
          t_ = t_ + dt
       end do
       ys(i+1, :) = y
       write (stderr, "(A15 F10.2 '%')") "Integrating:", 100.0 * (real(i)/nt)
    end do
    call cpu_time(stop)
    write (stderr, "(A)") repeat("=", 64)
    write (stderr, "(A15 F8.2 ' seconds')") "Elapsed:", (stop - start)
    write (stderr, *)

    deallocate(f)
    deallocate(d)
    deallocate(e)
    deallocate(y)
    deallocate(s)
    deallocate(nl)
  end subroutine integrate
end module ccgnlse
