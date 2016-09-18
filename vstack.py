#!/usr/bin/env python3


import argparse
import scipy


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    type=str,
                    nargs="+")
args = parser.parse_args()


final = {}
for filename in args.input:
    partial = scipy.load(filename)
    for key in partial.files:
        if key not in final:
            final[key] = partial[key]
        else:
            if key == "t":
                final[key] = scipy.hstack(
                    [final[key], partial[key]])
            if key == "states":
                final[key] = scipy.vstack(
                    [final[key], partial[key]])

t = final["t"]
filename = (
    "delta=%.2f_pump=%.2E_loss=%.2E_mint=%.2f_maxt_%.2f_nt=%d.npz" %
    (final["delta"], final["pump"], final["loss"],
     t.min(), t.max(), len(t)))
scipy.savez(filename, **final)
