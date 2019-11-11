"""
Created on March 15, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
import json
import os
import sys

def usage():
    print("aggregateShipments.py <shipmentsDir> <outputFilePath>")
    sys.exit(-1)
    
def main(argv):
    shipmentsDir = argv[0]
    outputFilePath = argv[1]

    berthList = ["Berth 30", "Berth 31", "Berth 32", "Berth 33"]
    aggregatedDict = { "commodities": [] }
    for filename in os.listdir(shipmentsDir):
        if not ".json" in filename:
            continue
        with open(shipmentsDir + "/" + filename) as jsonFile:
            shipmentsDict = json.load(jsonFile)
            shipments = shipmentsDict["commodities"]
            shipments = list(filter(lambda x: x["source"] in berthList, shipments))
            aggregatedDict["commodities"].extend(shipments)

    with open(outputFilePath, 'w') as outFile:
        outputStr = json.dumps(aggregatedDict, indent=4)
        outFile.write(outputStr)
    outFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    
