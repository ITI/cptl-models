"""
Created April 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.util.CalibrationReporter import CoreCalibrationReporter
import json
import sys

def usage():
    print("calibrationReporter.py <scenarioDir> <month> <simDurationDays>")
    sys.exit(-1)
    
def main(argv):
    if len(argv) != 3:
        usage()
        
    scenarioDir = argv[0]
    month = int(argv[1])
    simDurationDays = int(argv[2])

    configDirPath = "/".join([scenarioDir, "config"])
    dataSourceInventoryPath = "/".join([configDirPath, "inventory.json"])
    outputFileDir = "/".join([scenarioDir, "results/measurements"])
    
    dataSourceInventoryDict = None
    with open(dataSourceInventoryPath) as dataSourceInventoryFile:
        dataSourceInventoryDict = json.load(dataSourceInventoryFile)

    #for dUrn in dataSourceInventoryDict:
    #    dataSourceInventoryDict[dUrn] = \
    #        "/".join([scenarioDir, dataSourceInventoryDict[dUrn]])
        
    cReporter = CoreCalibrationReporter.create(scenarioDir,\
                                               configDirPath,\
                                               dataSourceInventoryDict,\
                                               month,\
                                               simDurationDays)
    cReporter.loadDataSources()


    for mUrn in cReporter.measurementUrns:
        fileContents = []

        result = cReporter.getMeasurement(mUrn)
        result.drop("Ref", axis=1, inplace=True)
        fileContents.append(mUrn)
        fileContents.append(result.to_csv(index=False))

        measurementName = mUrn.split(":")[-1]
        measurementFileName = measurementName + ".csv"
        outputFilePath = "/".join([outputFileDir, measurementFileName])
        with open(outputFilePath, 'w') as outputFile:
            outputFile.write("\n".join(fileContents))
        outputFile.close()
        
if __name__ == "__main__":
    main(sys.argv[1:])
