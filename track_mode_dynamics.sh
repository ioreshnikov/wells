#!/bin/bash


set -x
LANG=C


prefix="DissipativeP=0.50";

pump=0.5;
loss=0.001;

start=-5.00;
stop=5.0;
step=0.10;
deltas=`seq $start $step $stop`;

mode=4;
label="$mode+";


for delta in $deltas; do
    input=`printf "mode=%d_delta=%.2f_pump=%.2E_loss=%.2E_%s.npz" \
                  $mode $delta $pump $loss $label;`;
    input="$prefix/$input";
    output=`./propagate.py --pump $pump   \
                           --loss $loss   \
                           --delta $delta \
                           --input $input`;
    ./publish_coordinate_domain.py $output;
done;
