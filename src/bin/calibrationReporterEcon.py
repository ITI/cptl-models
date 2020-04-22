"""
Created April 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.util.CalibrationReporter import EconomicCalibrationReporter
import json
import sys

def usage():
    print("calibrationReporterEcon.py <scenarioDir> <month> <simDurationDays>")
    sys.exit(-1)
    
def main(argv):
    if len(argv) != 3:
        usage()
        
    scenarioDir = argv[0]
    month = int(argv[1])
    simDurationDays = int(argv[2])

    configDirPath = "/".join([scenarioDir, "config"])
    dataSourceInventoryPath = "/".join([configDirPath, "inventory.json"])
    outputFilePath = "/".join([scenarioDir, "results/calibration_econ.log"])
    
    dataSourceInventoryDict = None
    with open(dataSourceInventoryPath) as dataSourceInventoryFile:
        dataSourceInventoryDict = json.load(dataSourceInventoryFile)

    #for dUrn in dataSourceInventoryDict:
    #    dataSourceInventoryDict[dUrn] = \
    #        "/".join([scenarioDir, dataSourceInventoryDict[dUrn]])
        
    ecReporter = EconomicCalibrationReporter.create(scenarioDir,\
                                                    configDirPath,\
                                                    dataSourceInventoryDict,\
                                                    month,\
                                                    simDurationDays)
    ecReporter.loadDataSources()

    fileContents = []
    for mUrn in ecReporter.measurementUrns:
        result = ecReporter.getMeasurement(mUrn)
        print(mUrn)
        fileContents.append(mUrn)                    
        if type(result) is dict:
            results = result
            for dsUrn in results.keys():
                result = results[dsUrn]
                fileContents.append(dsUrn)
                fileContents.append(result.to_csv(index=True))
        else:
            if "Ref" in result:
                result.drop("Ref", axis=1, inplace=True)
            fileContents.append(result.to_csv(index=True))

        
    with open(outputFilePath, 'w') as outputFile:
        outputFile.write("\n".join(fileContents))
    
if __name__ == "__main__":
    main(sys.argv[1:])
