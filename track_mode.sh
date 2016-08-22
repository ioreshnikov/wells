#!/bin/bash


LANG=C;


modes=`seq 0 1 6`;
for mode in $modes; do
    min=-$mode.5;
    max=+5.0;
    step=0.1;
    deltas=`seq $min $step $max`;

    output=;
    for delta in $deltas; do
        echo $mode $delta;
        command="./tqho.py --n $mode --delta $delta";
        if [ -n "$output" ]; then
            command="$command --input $output";
        fi
        output=`$command`;
        if [ -z "$output" ]; then
            exit
        fi
    done
done
