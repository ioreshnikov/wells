#!/bin/bash


LANG=C;
pump=0.500;
loss=0.001;
directory="Dissipative";

mode=2;
label="$mode+";
deltas=`seq 3.0 -0.5 -1.0`;


for delta in $deltas; do
    input="$directory/mode=${mode}_delta=$(printf '%.3f' $delta)_*_${label}.npz";
    input=`./ztqho.py --n $mode \
                      --label $label \
                      --pump $pump \
                      --loss $loss \
                      --delta $delta \
                      --interpolate \
                      --input $input`;
    ./propagate.sh $input;
done
