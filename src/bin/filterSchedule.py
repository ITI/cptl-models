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

def isInTimeInterval(vesselArrivalDict, timeInterval):
    result = False
    time = vesselArrivalDict["time"]
    if time in range( timeInterval[0], timeInterval[1] ):
        result = True
    return result

def main(argv):
    scenarioBase = argv[0]
    minTime = int(argv[1])
    maxTime = int(argv[2])
    
    scheduleSchemaFilePath = "/Users/polutropos/Documents/Repositories/CIRI/cptl-models/data/schema/schedule.schema.v2.json"
    vesselScheduleSchema = None
    with open(scheduleSchemaFilePath) as scheduleSchemaFile:
        vesselScheduleSchema = json.load(scheduleSchemaFile)
    scheduleSchemaFile.close()

    for month in list(range(10,13)) + list(range(1,10)):
        print(month)
        timeInterval = [minTime, maxTime]
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
            list(filter(lambda x: isInTimeInterval(x, timeInterval), results))
        results = \
            list(map(lambda x: updateShipmentFilePath(x), results))
        results = \
            list(map(lambda x: normalizeShipLine(x), results))
        
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
    
                        
