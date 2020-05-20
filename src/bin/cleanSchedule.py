"""
Created on May 4, 2020

@author Gabriel A. Weaver

Copyright (c) 2019-2020 University of Illinois at Urbana Champaign
All Rights Reserved
"""
import json
import os
import sys

def main(argv):
    scheduleFilePath = argv[0]
    outputFilePath = argv[1]

    with open(scheduleFilePath) as jsonSchedule:
        scheduleDict = json.load(jsonSchedule)
        shipments = scheduleDict["shipments"]

        for idx, shipment in enumerate(shipments):
            shipment["shipment_file"] = shipment["shipment_file"].replace(":", "_")

    with open(outputFilePath, 'w') as outFile:
        outputStr = json.dumps(scheduleDict, indent=4)
        outFile.write(outputStr)
    outFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])

