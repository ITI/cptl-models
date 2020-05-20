"""
Created April 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.util.CalibrationReporter import CoreCalibrationReporter
import json
import numpy as np
import sys
from matplotlib import pyplot

def usage():
    print("outputTEUPaths.py <scenarioDir> <month> <simDurationDays>")
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
    
    teuPathsInSimulation, teuPathsInOptimizer = None, None
    for outputDbUrn in dataSourceInventoryDict.keys():
        fileContents = []
        if "DESOutputDB" in outputDbUrn:
            teuInSimulation = cReporter.selectAllTEU(outputDbUrn)
            teuPathsInSimulation = teuInSimulation.groupby('Path Traveled').count()[['Commodity Name']]
            teuPathsInSimulation = teuPathsInSimulation.rename(columns={"Commodity Name":"Count"})
            teuPathsInSimulation = teuPathsInSimulation.sort_values(["Count"], ascending=False)
            
        elif "OptimizerOutputResults" in outputDbUrn:
            teuInOptimizer = cReporter.selectAllTEU(outputDbUrn)
            teuPathsInOptimizer = teuInOptimizer.groupby('Path Traveled').count()[['Commodity Name']]
            teuPathsInOptimizer = teuPathsInOptimizer.rename(columns={"Commodity Name":"Count"})
            teuPathsInOptimizer = teuPathsInOptimizer.sort_values(["Count"], ascending=False)

    for resultType in ["simulation", "optimizer"]:
        fileContents = []
        
        measurementFileName = ".".join(["TEUPaths", resultType, "csv"])
        outputFilePath = "/".join([outputFileDir, measurementFileName])

        if "simulation" == resultType:
            fileContents.append(teuPathsInSimulation.to_csv(index=True))
        elif "optimizer" == resultType:
            fileContents.append(teuPathsInOptimizer.to_csv(index=True))
            
        with open(outputFilePath, 'w') as outputFile:
            outputFile.write("\n".join(fileContents))
        outputFile.close()
        
if __name__ == "__main__":
    main(sys.argv[1:])
