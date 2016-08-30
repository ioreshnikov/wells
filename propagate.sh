#!/bin/bash


input=$1;
mint=0;
maxt=50;


while [ $maxt -le 600 ]; do
    input=`./propagate.py --mint $mint --maxt $maxt --input $input`;
    mint=`expr $mint + 50`;
    maxt=`expr $maxt + 50`;
done;
