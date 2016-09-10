#!/bin/bash

set -e;

f2py --fcompiler=gnu95         \
     -I/usr/include            \
     -lfftw3                   \
     --arch='-march=native'    \
     -c _solver.f90 -m _solver;
