#!/bin/bash


set -x
LANG=C;


pump=0.500;
loss=0.001;


mode=2;
label="$mode-";
scale=-0.90;
phase=0.00;

start=-1.40;
stop=-1.50;
step=-0.01;
deltas=`seq $start $step $stop`;

output="Conservative128/mode=${mode}_delta=${start}.npz";
for delta in $deltas; do
    command="./ztqho.py --pump $pump --loss $loss --n $mode --delta $delta --scale $scale --phase $phase --label $label";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
    phase=0.0
    scale=1.0
done
