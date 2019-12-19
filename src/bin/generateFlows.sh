#!/bin/bash
echo "Data Intersection"
python3 src/bin/dataIntersection.py `pwd`/data/test-scenarios/onf2 data/test-scenarios/onf2/data/PEV-FY2018/counts.txt
echo "Vessel Schedule"
python3 src/bin/generateVesselSchedule.py `pwd`/data/test-scenarios/onf2
echo "Shipments"
python3 src/bin/generateVesselShipments.py `pwd`/data/test-scenarios/onf2
