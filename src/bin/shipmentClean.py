"""
Created on August 21, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign
All rights reserverd
"""
import json
import math
import sys

def main(argv):
    shipmentFilePath = argv[0]
    shipmentOutPath = argv[1]
    
    countsDict = {}
    shipmentDict = None
    with open(shipmentFilePath) as json_data:
        shipmentDict = json.load(json_data)
        json_data.close()

    total = 0
    for idx, commodity in enumerate(shipmentDict["commodities"]):
        name = "-".join([commodity["name"], str(idx)])
        total += math.ceil(float(commodity["nTEU"]))
        commodity["name"] = name
        commodity["destination"] = "McIntosh Intersection"
        if "Berth 33" in commodity["source"]:
            commodity["source"] = "Berth 33"
        
    countsDict[shipmentOutPath] = total
    with open(shipmentOutPath, 'w') as outfile:
        json.dump(shipmentDict, outfile, indent=4)
    outfile.close()

    with open("/tmp/teucounts.csv", 'a') as outfile:
        for key in countsDict:
            count = countsDict[key]
            outfile.write(f"{key}\t{count}\n")
    outfile.close()

    
    
if __name__ == "__main__":
    main(sys.argv[1:])



