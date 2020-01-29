#!/bin/bash
echo "INITIAL DATA PROCESSING"
echo "Data Intersection"
python3 src/bin/dataIntersection.py `pwd`/data/test-scenarios/onf2 data/test-scenarios/onf2/data/PEV-FY2018/counts.txt
echo "Vessel Schedule"
python3 src/bin/generateVesselSchedule.py `pwd`/data/test-scenarios/onf2
python3 src/bin/filterSchedule.py `pwd`/data/test-scenarios/onf2 0 40320
echo "Shipments"
python3 src/bin/generateVesselShipments.py `pwd`/data/test-scenarios/onf2
python3 src/bin/filterShipments.py `pwd`/data/test-scenarios/onf2 

echo "CREATE EXPERIMENTS"
python3 ./src/bin/buildExperiments.py data/test-scenarios/onf2 nolh1 data/may-exps 5 CLEAN
python3 ./src/bin/buildExperiments.py data/test-scenarios/onf2 nolh1 data/may-exps 5 GENERATE
