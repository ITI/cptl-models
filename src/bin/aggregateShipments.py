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
    print("aggregateShipments.py <scheduleFilePath> <shipper> <outputFilePath>")
    sys.exit(-1)
    
def main(argv):
    scheduleFilePath = argv[0]
    shipperName = argv[1]
    outputFilePath = argv[2]

    scheduleFileDir = os.path.dirname(scheduleFilePath)
    berthList = ["Berth 30", "Berth 31", "Berth 32", "Berth 33"]
    aggregatedDict = { "commodities": [] }
    
    with open(scheduleFilePath) as jsonScheduleFile:
        scheduleDict = json.load(jsonScheduleFile)
        shipmentsDict = scheduleDict["shipments"]

        for shipment in shipmentsDict:
            shipper = shipment["shipper"]
            if shipper != shipperName:
                continue
            time = shipment["time"]
            shipmentFile = shipment["shipment_file"]
            with open(scheduleFileDir + "/" + shipmentFile) as vesselShipmentsFile:
                vesselShipmentsDict = json.load(vesselShipmentsFile)
                vesselShipments = vesselShipmentsDict["commodities"]
                shipments = list(filter(lambda x: x["source"] in berthList, vesselShipments))
                for shipment in shipments:
                    shipment["shipper"] = shipper
                aggregatedDict["commodities"].extend(shipments)

    with open(outputFilePath, 'w') as outFile:
        outputStr = json.dumps(aggregatedDict, indent=4)
        outFile.write(outputStr)
    outFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    
