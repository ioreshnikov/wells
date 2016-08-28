! Integrates nonlinear Schrödinger equation to simulate pulse
! propagation in a regular single-mode optical fiber.

! Light-weight FFTW3 wrapper module
! ---------------------------------
module fftw
  implicit none
  include "fftw3.f"

  ! Multi-threading.
  integer, private   :: threading_init_successfull
  integer, parameter :: nthreads = 1

  ! Pointers to FFTW plan structures.
  integer*8, private :: forward_plan = 0
  integer*8, private :: inverse_plan = 0
contains
  subroutine init_forward(input, output)
    ! Initialize FFTW forward plan.
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    call dfftw_init_threads(threading_init_successfull)
    call dfftw_plan_with_nthreads(nthreads)
    call dfftw_plan_dft_1d(forward_plan, size(input), &
                           input, output,             &
                           FFTW_FORWARD, FFTW_ESTIMATE)
  end subroutine init_forward

  subroutine init_inverse(input, output)
    ! Initialize FFTW forward plan.
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    call dfftw_init_threads(threading_init_successfull)
    call dfftw_plan_with_nthreads(nthreads)
    call dfftw_plan_dft_1d(inverse_plan, size(input), &
                           input, output,             &
                           FFTW_BACKWARD, FFTW_ESTIMATE)
  end subroutine init_inverse

  subroutine fft(input, output)
    ! Perform forward fast Fourier transform.
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    if (forward_plan == 0) then
       call init_forward(input, output)
    end if
    call dfftw_execute_dft(forward_plan, input, output)
  end subroutine fft

  subroutine ifft(input, output)
    ! Perform inverse fast Fourier transform.
    double complex, dimension(:) :: input
    double complex, dimension(:) :: output
    if (inverse_plan == 0) then
       call init_inverse(input, output)
    end if
    call dfftw_execute_dft(inverse_plan, input, output)
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
    f = f / (step * n)
  end subroutine fftfreq

  subroutine fftshift(x)
    ! Performs swapping left and right parts of the vector in place.
    double precision, dimension(:) :: x
    double precision, allocatable, dimension(:) :: tmp
    integer :: n

    n = size(x)
    allocate(tmp(n/2))

    tmp = x(1:n/2)
    x(1:n/2) = x(n/2+1:n)
    x(n/2+1:n) = tmp

    deallocate(tmp)
  end subroutine fftshift

  subroutine zfftshift(x)
    ! Performs swapping left and right parts of the vector in place.
    ! The same as before, but over double complex arrays.
    double complex, dimension(:) :: x
    double complex, allocatable, dimension(:) :: tmp
    integer :: n

    n = size(x)
    allocate(tmp(n/2))

    tmp = x(1:n/2)
    x(1:n/2) = x(n/2+1:n)
    x(n/2+1:n) = tmp

    deallocate(tmp)
  end subroutine zfftshift
end module fftw


! Missing utilities
! -----------------
module util
  implicit none

  integer, parameter :: stderr = 0
  integer, parameter :: stdin = 5
  integer, parameter :: stdout = 6

  ! Allocated memory counter
  integer*8, private :: total_allocated
contains
  subroutine linspace(min, max, size, x)
    double precision :: min
    double precision :: max
    integer :: size
    double precision, dimension(:) :: x

    double precision :: dx
    integer :: i

    dx = (max - min) / (size - 1)
    do i = 1, size
       x(i) = min + (i - 1) * dx
    end do
  end subroutine linspace

  subroutine report_allocated(size, label)
    integer*8 :: size
    character(len=*) :: label

    total_allocated = total_allocated + size  ! Update global counter
    write (stderr, "(A15 I10 ' kB for ' A)"), &
          'Allocated:', size/1024, label
  end subroutine report_allocated

  subroutine report_total_allocated()
    write (stderr, "(A15 I10 ' kB')"), &
          'Total:', total_allocated / 1024
  end subroutine report_total_allocated

  function factorial(n)
    integer :: n
    integer :: factorial
    integer :: i

    factorial = 1
    do i = 1, n
       factorial = i * factorial
    end do
  end function factorial
end module util


! The solver itself
! -----------------
module pnlse
  use fftw
  use util
  implicit none

  ! Imaginary unit and pi, yes they are not in the language.
  double complex,   parameter, private :: im = (0.0, 1.0)
  double precision, parameter, private :: pi = 4 * atan(1.0)

  ! Solver parameters. Public ...
  double precision, parameter :: relative_tolerance = 1E-6
  double precision, parameter :: absolute_tolerance = 1E-8
  integer,          parameter :: maximum_steps = 5000
  ! ... and private.
  integer,          parameter, private :: scalar_tolerance = 1
  integer,          parameter, private :: adams_integrator = 10
  integer,          parameter, private :: extra_options = 1
  integer,          parameter, private :: without_jacobian = 0
  integer,          parameter, private :: not_sure_what_but_1 = 1
  double precision, parameter, private :: without_real_parameters = 0
  integer,          parameter, private :: without_integer_parameters = 0

  ! Internal rhs() parameters. I store them here because to hell with
  ! them parameter vectors packing/unpacking.
  double complex,   pointer, dimension(:), private :: input_
  double precision, pointer, dimension(:), private :: potential_
  double precision, pointer,               private :: pump_
  double precision, pointer,               private :: loss_
  double precision, pointer, dimension(:), private :: absorber_
  double precision, pointer,               private :: background_

  ! These are the often used intermediate variables (like current
  ! spectrum or nonlinearity operator) that I'd like to reuse rather
  ! than allocate memory each time I call rhs().
  double complex, allocatable, dimension(:), private :: state
  double complex, allocatable, dimension(:), private :: spectrum
  double complex, allocatable, dimension(:), private :: spectrum_
  double complex, allocatable, dimension(:), private :: dispersion
  double complex, allocatable, dimension(:), private :: nonlinearity
  double complex, allocatable, dimension(:), private :: exp_
contains
  subroutine integrate(z, t, input,                  &
                       potential, delta, pump, loss, &
                       absorber, background,         &
                       f, states, spectra)
    ! Input variables.
    double precision, dimension(:), intent(in) :: z
    double precision, dimension(:), intent(in) :: t
    double complex,   dimension(:), target, intent(in) :: input
    double precision, dimension(:), target, intent(in) :: potential
    double precision, target, intent(in) :: delta
    double precision, target, intent(in) :: pump
    double precision, target, intent(in) :: loss
    double precision, dimension(:), target, intent(in) :: absorber
    double precision, target, intent(in) :: background
    ! double precision, dimension(:), intent(in) :: betas

    ! Output variables.
    double precision, dimension(size(t)),          intent(out) :: f
    double complex,   dimension(size(z), size(t)), intent(out) :: states
    double complex,   dimension(size(z), size(t)), intent(out) :: spectra

    ! Intermediate variables.
    integer :: nz          ! Grid parameters
    integer :: nt
    double precision :: dt
    double precision :: z_ ! Running distance
    integer :: i
    integer :: n
    integer :: status = 1  ! Integration status
    real :: time_start
    real :: time_stop

    integer :: worker_complex_size
    integer :: worker_real_size
    integer :: worker_integer_size
    double complex,   allocatable, dimension(:) :: worker_complex
    double precision, allocatable, dimension(:) :: worker_real
    integer,          allocatable, dimension(:) :: worker_integer

    ! Save medium parameters as module-level globals.
    input_      => input
    potential_  => potential
    pump_       => pump
    loss_       => loss
    absorber_   => absorber
    background_ => background

    ! Extract grid parameters from the vectors.
    nz = size(z)
    nt = size(t)
    dt = t(2) - t(1)
    z_ = z(1)

    ! Construct frequency scale.
    call fftfreq(nt, dt, f)
    f = 2*pi * f

    ! Construct dispersion operator.
    allocate(dispersion(nt))
    dispersion = - delta - 0.5 * f**2
    ! dispersion = 0.0
    ! do i = 1, size(betas)
    !    n = i + 1
    !    dispersion = dispersion + 1.0/factorial(n) * betas(i) * f**n
    ! end do

    ! We will not use frequency scale anymore and can fftshift it.
    call fftshift(f)

    ! Initialize intermediate state, spectrum and slowly changing
    ! spectrum_, as well as intermediate variables in rhs() function.
    allocate(state(nt))
    allocate(spectrum(nt))
    allocate(spectrum_(nt))
    allocate(exp_(nt))
    allocate(nonlinearity(nt))

    state = input
    call fft(input, spectrum)
    spectrum_ = spectrum

    ! Prepare worker arrays.
    worker_complex_size = 15 * nt
    worker_real_size = 20 * nt
    worker_integer_size = 30

    allocate(worker_complex(worker_complex_size))
    allocate(worker_real(worker_real_size))
    allocate(worker_integer(worker_integer_size))

    ! We're going to redefine maximum internal steps. To do so we need
    ! to set flag IOPT to 1, which will cause solver to look inside
    ! worker_real and worker_integer arrays, which are usually
    ! initalized with garbage, unless we specify 0 initial state
    ! explicitly.
    worker_real = 0
    worker_integer = 0
    ! Pass maximum steps.
    worker_integer(6) = maximum_steps

    ! Initialize running distance variable, and copy initial
    ! conditions into output matrices.
    call zfftshift(spectrum)
    z_ = z(1)
    states(1, :)  = state
    spectra(1, :) = spectrum

    ! Report allocated space (including input variables)
    write (stderr, "(A)"), repeat("-", 64)
    call report_allocated(sizeof(z),              "distance grid")
    call report_allocated(sizeof(t),              "time grid")
    call report_allocated(sizeof(f),              "frequency grid")
    call report_allocated(sizeof(states),         "state matrix")
    call report_allocated(sizeof(spectra),        "spectrum matrix")
    call report_allocated(sizeof(state),          "current state")
    call report_allocated(sizeof(spectrum),       "current spectrum")
    call report_allocated(sizeof(spectrum_),      "slowly changing spectrum")
    call report_allocated(sizeof(dispersion),     "dispersion operator")
    call report_allocated(sizeof(exp_),           "auxiliary variable exp_")
    call report_allocated(sizeof(nonlinearity),   "auxiliary variable nonlinearity")
    call report_allocated(sizeof(worker_complex), "zvode worker complex matrix")
    call report_allocated(sizeof(worker_real),    "zvode worker real matrix")
    call report_allocated(sizeof(worker_integer), "zvode worker integer matrix")
    write (stderr, "(A)"), repeat("=", 64)
    call report_total_allocated()

    ! Finally, integrate the equation step-by-step with ZVODE solver.
    write (stderr, *)
    write (stderr, "(A)"), repeat("-", 64)

    call cpu_time(time_start)
    do i = 2, nz
       write (stderr, "(A15 F10.2 '%')"), "Integrating:", 100.0 * (real(i)/nz)
       call zvode(                     &
            rhs, nt, spectrum_,        &
            z_, z(i),                  &
            scalar_tolerance,          & ! ITOL
            relative_tolerance,        & ! RTOL
            absolute_tolerance,        & ! ATOL
            not_sure_what_but_1,       & ! ITASK
            status,                    & ! ISTATE
            extra_options,             & ! IOPT
            worker_complex,            & ! ZWORK
            worker_complex_size,       & ! LZW
            worker_real,               & ! RWORK
            worker_real_size,          & ! LRW
            worker_integer,            & ! IWORK
            worker_integer_size,       & ! LIW
            without_jacobian,          & ! JAC
            adams_integrator,          & ! MF = 10 => Adams
            without_real_parameters,   & ! RPAR
            without_integer_parameters & ! IPAR
            )

       if (status < 0) then
          write(stderr, "('Integration failed')")
          call exit()
       end if

       ! Convert to real fast changing spectrum and state and write
       ! them into return matrices.
       exp_ = exp(im * dispersion * z_)
       spectrum = spectrum_ * exp_
       call ifft(spectrum, state)
       call zfftshift(spectrum)

       states(i, :) = state
       spectra(i, :) = spectrum
    end do
    call cpu_time(time_stop)

    write (stderr, "(A)"), repeat("=", 64)
    write (stderr, "(A15 F8.2 ' seconds')") "Elapsed:", (time_stop - time_start)
    write (stderr, *)
  end subroutine integrate

  subroutine rhs(nt, z, spectrum_, result)
    ! Right hand's side of the equation. The interface if fixed by
    ! ZVODE solver.
    integer :: nt
    double precision :: z
    double complex, dimension(1:nt) :: spectrum_
    double complex, dimension(1:nt) :: result

    ! Transform to time domain.
    exp_ = exp(im * dispersion * z)
    spectrum = spectrum_ * exp_
    call ifft(spectrum, state)

    ! Calculate nonlinear operator.
    nonlinearity = abs(state)**2
    nonlinearity = nonlinearity - potential_
    nonlinearity = nonlinearity + im * loss_
    if (size(absorber_) == nt) then
       nonlinearity =     &
           nonlinearity + &
           im * absorber_ * (abs(state) - background_)
    end if
    nonlinearity = nonlinearity * state
    nonlinearity = nonlinearity + pump_

    ! Transform back to slow spectrum.
    call fft(nonlinearity, result)
    result = im * 1/exp_ * result
  end subroutine rhs
end module pnlse
