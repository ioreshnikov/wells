#!/bin/bash


LANG=C;


n=0;

min=-0.5;
max=+5.0;
step=0.1;
deltas=`seq $min $step $max`;


for delta in $deltas; do
    echo $delta;
    command="./tqho.py --n $n --delta $delta";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
done
