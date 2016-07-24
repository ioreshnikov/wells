#!/bin/bash


LANG=C;


p=0.05;
kappa=0.001;


mode=2;
label="$mode+";
scale=0.95;
phase=0.10;

start=-4.00;
stop=2.00;
step=0.05;
deltas=`seq $start $step $stop`;


# output="Conservative/mode=${mode}_delta=${start}.npz";
for delta in $deltas; do
    command="./ztqho.py --p $p --kappa $kappa --n $mode --delta $delta --scale $scale --phase $phase --label $label";
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
