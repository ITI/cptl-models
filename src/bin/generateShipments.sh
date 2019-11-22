#!/bin/bash

scheduleFilePath=data/test-scenarios/onf1/flows/schedule.json
startTime=0
endTime=4320
outputDir=data/test-scenarios/onf1/flows

for shipper in 'All' 'Crowley' 'King\ Ocean' 'FIT' 'MSC'
do
  echo python3 src/bin/aggregateShipments.py $scheduleFilePath $shipper $startTime $endTime $outputDir/shipment.$shipper.$startTime-$endTime.shpt
done