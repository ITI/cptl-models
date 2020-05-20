#!/bin/bash
EXPERIMENT_NAME=$1

for expIdx in 0 1 2 3; do \
    rm config/makeParams
    ln config/makeParams.$EXPERIMENT_NAME$expIdx.txt config/makeParams
    make simulate init-calibration calibration
    make init.econ postprocess.econ calibration.econ
done
