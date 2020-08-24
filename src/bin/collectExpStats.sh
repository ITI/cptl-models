#!/bin/bash

EXPERIMENT_NAME=nolhDisruptedBig

for expId in 1;
do
    SCENARIO_REF=PEV-SouthPortImports.FY2018_10_8_nolhBaseline_0_nolhDisruptedBig$expId
    EXP_DIR=build/$EXPERIMENT_NAME/$SCENARIO_REF
    EXP_RESULTS_DIR=~/$EXPERIMENT_NAME-viz/exp$expId
