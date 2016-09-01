#!/bin/bash


input=$1;
mint=500;
maxt=550;


while [ $maxt -le 1000 ]; do
    input=`./propagate.py --mint $mint --maxt $maxt --input $input`;
    mint=`expr $mint + 50`;
    maxt=`expr $maxt + 50`;
done;
