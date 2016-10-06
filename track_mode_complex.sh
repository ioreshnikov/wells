#!/bin/bash


set -x
LANG=C;


pump=0.500;
loss=0.001;


# modes=`seq 12 2 20`;
# for mode in $modes; do
#     label="$mode+";
#     scale=1.00;
#     output='';

#     start=-$(($mode + 1)).00;
#     stop=-$(($mode - 5)).00;
#     step=0.10;
#     deltas=`seq $start $step $stop`;

#     for delta in $deltas; do
#         command="./ztqho.py --pump $pump --loss $loss --n $mode --delta $delta --scale $scale --label $label";
#         if [ -n "$output" ]; then
#             command="$command --input $output";
#         fi
#         output=`$command`;
#         if [ -z "$output" ]; then
#             exit
#         fi
#         scale=1.0
#     done
# done


mode=16;
label="$mode+";
# scale=-0.90;
scale=1.00;

start=-17.97;
stop=-20.00;
step=-0.001;
deltas=`seq $start $step $stop`;

# output="Lower Conservative/mode=${mode}_delta=${start}.npz";
# output="Dissipative/mode=${mode}_delta=$(printf '%.3f' $start)_*_${label}.npz";
output="mode=${mode}_delta=$(printf '%.3f' $start)_*_${label}.npz";
for delta in $deltas; do
    command="./ztqho.py --pump $pump --loss $loss --n $mode --delta $delta --scale $scale --label $label";
    if [ -n "$output" ]; then
        command="$command --input $output";
    fi
    output=`$command`;
    if [ -z "$output" ]; then
        exit
    fi
    scale=1.0
done
