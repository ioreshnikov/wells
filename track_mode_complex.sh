#!/bin/bash


LANG=C;

p=0.001;
kappa=0.001;

n=0;

start=2.0;
stop=-0.5;
step=-0.05;
deltas=`seq $start $step $stop`;


for delta in $deltas; do
    command="./ztqho.py --n $n --delta $delta --p $p --kappa $kappa --zero";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
done
