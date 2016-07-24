#!/usr/bin/env python3


import argparse
import copy
import os.path
import re
import scipy


parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="solution file",
                    type=str)
args = parser.parse_args()


pattern = re.compile("mode=(\d+)_delta=(.*)_pump=(.*)_loss=(.*)_(.*).npz")
match = pattern.match(os.path.basename(args.input))
if not match:
    exit()

print(args.input)

mode, delta, pump, loss, label = match.groups()
pump, loss = map(float, (pump, loss))


workspace = scipy.load(args.input)
workspace_ = {}
for key in workspace.files:
    workspace_[key] = workspace[key]
workspace_["pump"] = pump
workspace_["loss"] = loss
scipy.savez(args.input, **workspace_)
