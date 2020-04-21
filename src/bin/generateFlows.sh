#!/bin/bash
#SCENARIO_REPO_HOME=/home/share/Code/cptl-models/data/test-scenarios
SCENARIO_REPO_HOME=/home/share/Code/cptl-models/build/nolhBaseline
DES_HOME=/home/share/des

echo "Enter Scenario Reference"
SCENARIO_REF=$1
echo "Enter Month"
MONTH=$2
echo "Enter Simulation Duration (days)"
SIM_DURATION_DAYS=$3

SCENARIO_DIR=$SCENARIO_REPO_HOME/$SCENARIO_REF
SIM_DURATION="$(($SIM_DURATION_DAYS * 1440))"
SIM_RUN_TIME="$(($SIM_DURATION + 5000))"

source cptl-models.venv/bin/activate
export PATH=$PATH:$DES_HOME/src:$DES_HOME/scripts/postProcessing
export PYTHONPATH=$DES_HOME/src:`pwd`/src

## TASK 0:  Clean
#rm -rf $SCENARIO_DIR/flows $SCENARIO_DIR/results 
#mkdir $SCENARIO_DIR/flows $SCENARIO_DIR/results

## TASK 2 (OK):  Initial Data Processing
#echo "Data Intersection"
#python3 src/bin/dataIntersection.py $SCENARIO_DIR 

## TASK 3 (OK):  Vessel Schedule
#python3 src/bin/generateVesselSchedule.py $SCENARIO_DIR $MONTH
#python3 src/bin/filterSchedule.py $SCENARIO_DIR 0 $SIM_DURATION

## TASK 4 (OK):  Create Shipments
#python3 src/bin/generateVesselShipments.py $SCENARIO_DIR $MONTH
#python3 src/bin/filterShipments.py $SCENARIO_DIR

## TASK 5 (OK):  Run the Scenario, Get Calibration Report
multiCommodityNetworkSim.py -o $SCENARIO_DIR/results/output.sqlite -t $SIM_RUN_TIME -si 100 -s $SCENARIO_DIR/flows/schedule.json
python ./src/bin/calibrationReporter.py $SCENARIO_DIR $MONTH $SIM_DURATION_DAYS

exit

### PDT EXTENSION:  ADVANCED ECONOMIC MODULE
##  TASK 1:  Generate the Cost Table for Simulation Output
#python $DES_HOME/scripts/postProcessing/generateCostTable.py -i $SCENARIO_DIR/data/PEV_FY18_Import.sqlite -o $SCENARIO_DIR/results/output.sqlite
##  TASK 2:  Get the Calibration Report
#python ./src/bin/calibrationReporterEcon.py $SCENARIO_DIR $MONTH $SIM_DURATION_DAYS

### PDT EXTENSION:  LATIN HYPERCUBE SCENARIO GENERATION
## TASK 1 (OK):  Create Experiments from Template
EXPERIMENT_NAME=nolhBaseline
TEMPLATE_REPO_HOME=$SCENARIO_REPO_HOME
EXPERIMENT_REPO_HOME=/home/share/Code/cptl-models/build/$EXPERIMENT_NAME
rm -rf $EXPERIMENT_REPO_HOME
mkdir $EXPERIMENT_REPO_HOME
python3 ./src/bin/buildExperiments.py $TEMPLATE_REPO_HOME $SCENARIO_REF $EXPERIMENT_NAME $EXPERIMENT_REPO_HOME $MONTH CLEAN
python3 ./src/bin/buildExperiments.py $TEMPLATE_REPO_HOME $SCENARIO_REF $EXPERIMENT_NAME $EXPERIMENT_REPO_HOME $MONTH GENERATE



