#!/bin/bash


LANG=C;
max_energy=30;
modes=`seq 0 1 20`;


for mode in $modes; do
    start=-$mode.50;
    stop=`expr -$mode + 10`;
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

        energy=`./energy.py $output`;
        need_exit=`echo "$energy > $max_energy" | bc -l`;
        if [ $need_exit -eq 1 ]; then
            break;
        fi
    done
done
