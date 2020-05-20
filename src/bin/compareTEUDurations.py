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
    print("compareTEUDurations.py <scenarioDir> <month> <simDurationDays>")
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
    
    teuDurationsInSimulation, teuDurationsInOptimizer = None, None
    for outputDbUrn in dataSourceInventoryDict.keys():
        fileContents = []
        if "DESOutputDB" in outputDbUrn:
            teuInSimulation = cReporter.selectAllTEU(outputDbUrn)
            teuDurationsInSimulation = teuInSimulation.apply(lambda x: cReporter.getDuration(x), axis=1)
            
        elif "OptimizerOutputResults" in outputDbUrn:
            teuInOptimizer = cReporter.selectAllTEU(outputDbUrn)
            teuDurationsInOptimizer = teuInOptimizer.apply(lambda x: cReporter.getDuration(x), axis=1)

    bins = np.linspace(0, 5000, 100)
    pyplot.hist(teuDurationsInSimulation, bins, alpha=0.5, label='Simulation')
    pyplot.hist(teuDurationsInOptimizer, bins, alpha=0.5, label='Optimizer')
    pyplot.legend(loc='upper right')
    pyplot.title(scenarioDir.split("/")[-1])
    
    outputFilePath = "/".join([outputFileDir, "teuDurations.png"])
    pyplot.savefig(outputFilePath)
            
if __name__ == "__main__":
    main(sys.argv[1:])
