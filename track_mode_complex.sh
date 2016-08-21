#!/bin/bash


set -x
LANG=C;


pump=0.500;
loss=0.001;


mode=0;
label="$mode";
scale=0.90;  # Was 0.95
phase=0.10;  # ... 0.10

start=1.00;
stop=5.00;
step=0.10;
deltas=`seq $start $step $stop`;


output="Conservative/mode=${mode}_delta=${start}.npz";
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
