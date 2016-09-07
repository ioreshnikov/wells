#!/bin/bash


input=$1;
mint=950;
maxt=1000;


while [ $maxt -le 1000 ]; do
    input=`./propagate.py --mint $mint --maxt $maxt --input $input --nt $((2**14))`;
    mint=`expr $mint + 50`;
    maxt=`expr $maxt + 50`;
done;
