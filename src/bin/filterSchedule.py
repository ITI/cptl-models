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

def updateVesselArrivalFile(vesselArrival):
    shipper = vesselArrival["shipper"]
    shipmentFile = vesselArrival["shipment_file"]
    shipmentFile = shipmentFile.replace("shipments/", f"shipments-{shipper}/")
    vesselArrival["shipment_file"] = shipmentFile
    return vesselArrival

def main(argv):
    scenarioBase = argv[0]
    minTime = int(argv[1])
    maxTime = int(argv[2])
    
    scheduleSchemaFilePath = "/home/share/Code/cptl-models/data/schema/schedule.schema.v2.json"
    vesselScheduleSchema = None
    with open(scheduleSchemaFilePath) as scheduleSchemaFile:
        vesselScheduleSchema = json.load(scheduleSchemaFile)
    scheduleSchemaFile.close()

    timeInterval = [minTime, maxTime]
    print(timeInterval)
    dayEpsilon = 0
    scheduleInputFilePath = "/".join([scenarioBase, "flows/schedule.raw.json"])
    scheduleOutputFilePath = "/".join([scenarioBase, "flows/schedule.json"])
        
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

    # Generate the vessel schedule for everyone
    validate(vesselScheduleDict, vesselScheduleSchema)
    with open(scheduleOutputFilePath, 'w') as scheduleOutputFile:
        resultStr = json.dumps(vesselScheduleDict, indent=4)
        scheduleOutputFile.write(resultStr)
    scheduleOutputFile.close()

    # Generate the vessel schedule for individual stakeholders
    for shipperName in ["Crowley", "MSC", "King Ocean", "FIT"]:
        shipperSchedule = filter(lambda x: x["shipper"] == shipperName, vesselScheduleDict["shipments"])
        shipperSchedule = map(lambda x: updateVesselArrivalFile(x), shipperSchedule)

        shipperScheduleDict = {}
        shipperScheduleDict["shipments"] = list(shipperSchedule)
        shipperScheduleDict["disruptions"] = vesselScheduleDict["disruptions"]
        shipperScheduleDict["network"] = vesselScheduleDict["network"]
        shipperScheduleDict["start_time"] = vesselScheduleDict["start_time"]
        shipperScheduleDict["workday_end"] = vesselScheduleDict["workday_end"]
        shipperScheduleDict["workday_start"] = vesselScheduleDict["workday_start"]

        validate(shipperScheduleDict, vesselScheduleSchema)
        scheduleOutputFileName2 = ".".join(["schedule", shipperName, "json"])
        scheduleOutputFilePath2 = scheduleOutputFilePath.replace("schedule.json", scheduleOutputFileName2)
        with open(scheduleOutputFilePath2, 'w') as scheduleOutputFile2:
            resultStr = json.dumps(shipperScheduleDict, indent=4)
            scheduleOutputFile2.write(resultStr)
        scheduleOutputFile2.close()

if __name__ == "__main__":
    main(sys.argv[1:])

    
                        
