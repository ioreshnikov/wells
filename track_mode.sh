#!/bin/bash


LANG=C;


modes=`seq 10 1 20`;
for mode in $modes; do
    start=-$mode.50;
    stop=`expr -$mode + 5`;
    step=0.10;
    deltas=`seq $start $step $stop`;

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
