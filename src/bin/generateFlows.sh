#!/bin/bash
echo "INITIAL DATA PROCESSING"
echo "Data Intersection"
#python3 src/bin/dataIntersection.py `pwd`/data/test-scenarios/onf2 data/test-scenarios/onf2/data/PEV-FY2018/counts.txt
echo "Vessel Schedule"
#python3 src/bin/generateVesselSchedule.py `pwd`/data/test-scenarios/onf2
#python3 src/bin/filterSchedule.py `pwd`/data/test-scenarios/onf2 0 40320
echo "Shipments"
#python3 src/bin/generateVesselShipments.py `pwd`/data/test-scenarios/onf2
#python3 src/bin/filterShipments.py `pwd`/data/test-scenarios/onf2 

echo "CREATE EXPERIMENTS"
python3 ./src/bin/buildExperiments.py data/test-scenarios/onf2 nolhBaseline data/oct-baseline-exps 10 CLEAN
python3 ./src/bin/buildExperiments.py data/test-scenarios/onf2 nolhBaseline data/oct-baseline-exps 10 GENERATE

echo "RUN EXPERIMENTS"
for expId in {0..16}
do
  cp -rf data/test-scenarios/onf2/networks/altered-transportation.v2.json data/test-scenarios/onf2/networks/csv data/oct-baseline-exps/0/networks/
  mkdir ../cptl-models/data/oct-baseline-exps/$expId/results
  ../ciri-maritime-des/src/multiCommodityNetworkSim.py -o ../cptl-models/data/oct-baseline-exps/$expId/results/output.sql -s `pwd`/../cptl-models/data/oct-baseline-exps/$expId/flows/schedule.json -si 1000 --baselineOnly
  ../ciri-maritime-des/scripts/postProcessing/generateCostTable.py -i data/PEV_FY18_Import.sqlite -o ../cptl-models/data/oct-baseline-exps/$expId/results/output.sql
done


