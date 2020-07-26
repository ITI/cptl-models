"""
Created July 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
import os
import pandas as pd
import sys

def usage():
    print("collectExpStats.py <experimentDir> <maxExp> <outputFilePath>")
    sys.exit(-1)

def main(argv):
    if len(argv) != 3:
        usage()

    experimentDir = argv[0]
    maxExp = int(argv[1])
    outputFilePath = argv[2]

    scenarioBase = "PEV-SouthPortImports.FY2018_10_8_nolhBaseline_0_nolhDisruptedBig"
    df = pd.DataFrame(columns=["expId","penalty_sim","penalty_opt"])

    for expId in range(0,maxExp+1):
        expDirPath = f"{experimentDir}/{scenarioBase}{expId}"
        penaltyFilePath = f"{expDirPath}/results/measurements/TotalPenalties.csv"

        if not os.path.isfile(penaltyFilePath):
            continue
        
        pFile = open(penaltyFilePath, "r")
        lines = pFile.readlines()
        pFile.close()
        simPenalty = "NA"
        optPenalty = "NA"
        for line in lines:
            linePcs = line.split(",")
            method = linePcs[0]
            value = linePcs[1].replace("$","")
            if "sim" == method:
                simPenalty = int(value)
            elif "opt" == method:
                optPenalty = int(value)

        df = df.append({'expId':expId, 'penalty_sim':simPenalty, 'penalty_opt':optPenalty}, ignore_index=True)

    df = df.fillna(-1)
    oFile = open(outputFilePath, "w")    
    oFile.write(df.to_csv(index=False))

if __name__ == "__main__":
    main(sys.argv[1:])

        
    
    
