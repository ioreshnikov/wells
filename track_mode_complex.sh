#!/bin/bash


LANG=C;


p=0.01;
kappa=0.001;


mode=0;
start=0.00;
stop=+2.00;
step=+0.05;
deltas=`seq $start $step $stop`;


label="$mode";
if (( $(echo "$step > 0" | bc -l) )); then
    label="$label+";
else
    label="$label-";
fi


output="raw/mode=${mode}_delta=${start}.npz";
for delta in $deltas; do
    command="./ztqho.py --delta $delta --p $p --kappa $kappa --label $label";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
done
