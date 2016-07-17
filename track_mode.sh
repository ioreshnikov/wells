#!/bin/bash


LANG=C;


n=11;

min=-11.5;
max=+10.0;
step=0.1;
deltas=`seq $min $step $max`;


for delta in $deltas; do
    command="./tqho.py --n $n --delta $delta";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
done
