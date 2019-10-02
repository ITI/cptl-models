#!/bin/bash

flowsDir=$1
outDir=$2

rm /tmp/teucounts.csv
rm $outDir/*

for filePath in $flowsDir/*;
do
    outFileName=$(basename "${filePath%.*}")
    outPath=${outDir}/${outFileName}.json
    echo "python src/bin/shipmentClean.py '$filePath' '$outPath'"
    python src/bin/shipmentClean.py "${filePath}" "${outPath}"
done
