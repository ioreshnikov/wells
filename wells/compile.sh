#!/bin/bash


gfortran -g -c -fPIC vode.f zvode.f;
f2py -I/usr/include                  \
     -lfftw3_threads -llapack -lblas \
     --arch='-march=native'          \
     vode.o zvode.o                  \
     -c propagate.f90 -m propagate;
rm *.o;
