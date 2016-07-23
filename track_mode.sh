#!/bin/bash


LANG=C;


n=4;

min=-4.5;
max=+2.0;
step=0.1;
deltas=`seq $min $step $max`;


for delta in $deltas; do
    command="./tqho.py --n $n --delta $delta";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
done
