"""
Created on December 20, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from jsonschema import validate
import json
import sys

def isIncludedVesselArrival(vesselArrivalDict):
    result = False
    berthMask = ("Berth 33" == vesselArrivalDict["destination_node"]) or\
        ("Berth 32" == vesselArrivalDict["destination_node"]) or\
        ("Berth 31" == vesselArrivalDict["destination_node"]) or\
        ("Berth 30" == vesselArrivalDict["destination_node"])
    result = berthMask
    return result

def updateShipmentFilePath(vesselArrivalDict):
    shipmentFilePath = vesselArrivalDict["shipment_file"]
    vesselArrivalDict["shipment_file"] = shipmentFilePath.replace(".json", ".filtered.json")
    return vesselArrivalDict

def normalizeShipLine(vesselArrivalDict):
    shipLine = vesselArrivalDict["shipper"]
    result = None
    if "Crowley" in shipLine:
        result = "Crowley"
    elif "King Ocean" in shipLine:
        result = "King Ocean"
    elif "MSC" in shipLine:
        result = "MSC"
    else:
        # Ugly hack assumption
        result = "FIT"

    vesselArrivalDict["shipper"] = result
    return vesselArrivalDict


def main(argv):
    scenarioBase = argv[0]
    
    scheduleSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/schedule.schema.v2.json"
    vesselScheduleSchema = None
    with open(scheduleSchemaFilePath) as scheduleSchemaFile:
        vesselScheduleSchema = json.load(scheduleSchemaFile)
    scheduleSchemaFile.close()

    for month in list(range(10,13)) + list(range(1,10)):
        print(month)
        dayEpsilon = 0
        scheduleInputFilePath = "/".join([scenarioBase, "flows/PEV-FY2018", f"{month}/schedule.json"])
        scheduleOutputFilePath = "/".join([scenarioBase, "flows/PEV-FY2018", f"{month}/schedule.filtered.json"])
        
        vesselArrivals = None
        with open(scheduleInputFilePath) as scheduleInputFile:
            vesselArrivals = json.load(scheduleInputFile)
        scheduleInputFile.close()

        results = \
            list(filter(lambda x: isIncludedVesselArrival(x), vesselArrivals["shipments"]))
        results = \
            list(map(lambda x: updateShipmentFilePath(x), vesselArrivals["shipments"]))
        results = \
            list(map(lambda x: normalizeShipLine(x), vesselArrivals["shipments"]))

        vesselScheduleDict = { "shipments": results,\
                                   "disruptions": vesselArrivals["disruptions"],\
                                   "start_time": vesselArrivals["start_time"],\
                                   "workday_start": vesselArrivals["workday_start"],\
                                   "workday_end": vesselArrivals["workday_end"],\
                                   "network": vesselArrivals["network"] }

        validate(vesselScheduleDict, vesselScheduleSchema)
        with open(scheduleOutputFilePath, 'w') as scheduleOutputFile:
            resultStr = json.dumps(vesselScheduleDict, indent=4)
            scheduleOutputFile.write(resultStr)
        scheduleOutputFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
    
                        
