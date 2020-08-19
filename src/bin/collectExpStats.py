"""
Created July 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
import os
import pandas as pd
import re
import sys

def usage():
    print("collectExpStats.py <experimentDir> <maxExp> <outputFilePath>")
    sys.exit(-1)

def main(argv):
    if len(argv) != 3:
        usage()

    experimentDir = argv[0]
    experimentName = experimentDir.split("/")[-1]
    maxExp = int(argv[1])
    outputFilePath = argv[2]

    scenarioBase = f"PEV-SouthPortImports.FY2018_10_8_nolhBaseline_0_{experimentName}"
    df = pd.DataFrame(columns=["expId","penalty_sim","penalty_opt", "sim_opt_delta", "opt_execution_time", "num_nodes", "num_delay_nodes", "num_arcs", "num_storage_arcs", "num_bundles"])
    df = df.astype('int32')
    
    for expId in range(0,maxExp+1):
        expDirPath = f"{experimentDir}/{scenarioBase}{expId}"

        # Process the penalty file
        penaltyFilePath = f"{expDirPath}/results/measurements/TotalPenalties.csv"
        
        if not os.path.isfile(penaltyFilePath):
            continue
        
        pFile = open(penaltyFilePath, "r")
        lines = pFile.readlines()
        pFile.close()
        simPenalty = None
        optPenalty = None
        for line in lines:
            linePcs = line.split(",")
            method = linePcs[0]
            value = linePcs[1] #.replace("$","") + linePcs[2]
            if "sim" == method:
                simPenalty = int(value)
            elif "opt" == method:
                optPenalty = int(value)

        simOptDelta = None
        if simPenalty != None and optPenalty != None:
            simOptDelta = int(simPenalty - optPenalty)
            
        # Process the opt results file
        optResultsFilePath = f"{expDirPath}/results/ctsndp.results"
        optExecutionTime, numNodes, numDelayNodes, numArcs, numStorageArcs, numBundles = None, None, None, None, None, None
        if os.path.isfile(optResultsFilePath):
            rFile = open(optResultsFilePath, "r")
            lines = rFile.readlines()
            rFile.close()
            optExecutionTime = float(lines[0].split(":")[1].strip())
            numBundles = int(lines[3].split(":")[1].strip())
            nodesLine = lines[4].split(":")[1].strip()
            nodesMatches = re.search("(\d+) of which (\d+) are delay nodes", nodesLine)
            numNodes = int(nodesMatches[1])
            numDelayNodes = int(nodesMatches[2])
            numArcs = int(lines[5].split(":")[1].strip())
            numStorageArcs = int(lines[6].split(":")[1].strip())
                        
        df = df.append({'expId':expId, 'penalty_sim':simPenalty, 'penalty_opt':optPenalty, 'sim_opt_delta': simOptDelta,
                        'opt_execution_time': optExecutionTime, 'num_nodes': numNodes,
                        'num_delay_nodes': numDelayNodes, 'num_arcs': numArcs, 'num_storage_arcs': numStorageArcs,
                        'num_bundles': numBundles}, ignore_index=True)

    df = df.fillna(-1)
    df = df.astype({'expId': 'int32', 'penalty_sim': 'int32', 'penalty_opt': 'int32', 'sim_opt_delta': 'int32',
                    'opt_execution_time': 'float32', 'num_nodes': 'int32', 'num_delay_nodes': 'int32',
                    'num_arcs': 'int32', 'num_storage_arcs': 'int32', 'num_bundles': 'int32'})
    
    oFile = open(outputFilePath, "w")    
    oFile.write(df.to_csv(index=False, sep='\t'))

if __name__ == "__main__":
    main(sys.argv[1:])

        
    
    
