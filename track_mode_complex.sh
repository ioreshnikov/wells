#!/bin/bash


set -x
LANG=C;


pa=1.000;
pm=0.790;
pw=0.200;
loss=0.100;

max_energy=30;


modes=`seq 6 2 20`;
for mode in $modes; do
    label="$mode+";
    scale=1.00;
    output='';

    start=$((-1 * ($mode + 1))).00;
    stop=$((-1 * ($mode - 10))).00;
    step=0.10;
    deltas=`seq $start $step $stop`;

    for delta in $deltas; do
        command="./ztqho.py --pa $pa --pm $pm --pw $pw --loss $loss --n $mode --delta $delta --scale $scale --label $label";
        if [ -n "$output" ]; then
            command="$command --input $output";
        fi
        output=`$command`;
        if [ -z "$output" ]; then
            exit;
        fi
        scale=1.0;

        energy=`./energy.py $output`;
        need_exit=`echo "$energy > $max_energy" | bc`;
        if [ $need_exit -eq 1 ]; then
            break;
        fi
    done
done


# modes=`seq 6 2 20`;
# for mode in $modes; do
#     label="$mode-";
#     scale=0.95;

#     start=$((-$mode + 1)).00;
#     start=-$mode.20;
#     stop=$((-$mode + 10)).00;
#     step=0.10;
#     deltas=`seq $start $step $stop`;


#     # Trial run to determine the energy.
#     output="Conservative/mode=${mode}_delta=${start}.npz";
#     conservative_energy=`./energy.py $output`;

#     command="./ztqho.py --pa $pa --pm $pm --pw $pw --loss $loss --n $mode --delta $start --scale $scale --label $label --input $output";
#     trial=`$command`
#     energy=`./energy.py $trial`;

#     # Above the curve.
#     if [ `echo "$energy > $conservative_energy" | bc -l` -eq 1 ]; then
#         scale=`echo "-1 * $scale" | bc -l`;
#     fi

#     for delta in $deltas; do
#         command="./ztqho.py --pa $pa --pm $pm --pw $pw --loss $loss --n $mode --delta $delta --scale $scale --label $label";
#         if [ -n "$output" ]; then
#             command="$command --input $output";
#         fi
#         output=`$command`;
#         if [ -z "$output" ]; then
#             exit
#         fi
#         scale=1.0

#         energy=`./energy.py $output`;
#         need_exit=`echo "$energy > $max_energy" | bc`;
#         if [ $need_exit -eq 1 ]; then
#             break;
#         fi
#     done
# done


# mode=2
# label="$mode+";

# # start=$((-1 * ($mode + 1))).00;
# # start=$((-$mode + 1)).00;
# start=-2.50;
# stop=10.00;
# step=0.01;
# deltas=`seq $start $step $stop`;

# # output="Dissipative/mode=${mode}_delta=$(printf '%.3f' $start)_*_${label}.npz";
# output="mode=${mode}_delta=$(printf '%.3f' $start)_*_${label}.npz";
# # output="Conservative/mode=${mode}_delta=${start}.npz";
# # scale=0.9;
# for delta in $deltas; do
#     command="./ztqho.py --pa $pa --pm $pm --pw $pw --loss $loss --n $mode --delta $delta --label $label";
#     if [ -n "$output" ]; then
#         command="$command --input $output";
#     fi
#     if [ -n "$scale" ]; then
#         command="$command --scale $scale";
#     fi
#     output=`$command`;
#     if [ -z "$output" ]; then
#         exit
#     fi
#     scale=1.0;

#     energy=`./energy.py $output`;
#     need_exit=`echo "$energy > $max_energy" | bc`;
#     if [ $need_exit -eq 1 ]; then
#         break;
#     fi
# done
