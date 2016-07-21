#!/bin/bash


LANG=C;

p=0.001;
kappa=0.001;

n=0;

start=-0.45;
stop=2.0;
step=+0.05;
deltas=`seq $start $step $stop`;


for delta in $deltas; do
    command="./ztqho.py --n $n --delta $delta --p $p --kappa $kappa";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
done
