"""
Created on December 20, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from jsonschema import validate
from os import listdir
from os.path import isfile, join
import json
import math
import os
import sys
import uuid

def isIncludedVesselShipment(vesselShipmentDict):
    result = False
    berthMask = ("Berth 33" == vesselShipmentDict["source"]) or\
        ("Berth 32" == vesselShipmentDict["source"]) or\
        ("Berth 31" == vesselShipmentDict["source"]) or\
        ("Berth 30" == vesselShipmentDict["source"])
    result = berthMask
    return result

def normalizeShipLine(vesselShipmentDict):
    shipLine = vesselShipmentDict["shipper"]
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

    vesselShipmentDict["shipper"] = result
    return vesselShipmentDict

def roundTEU(vesselShipmentDict):
    nTEU = vesselShipmentDict["nTEU"]
    vesselShipmentDict["nTEU"] = math.ceil(nTEU)
    return vesselShipmentDict

def genUUID(vesselShipmentDict):
    uuidVal = uuid.uuid4()
    vesselShipmentDict["uuid"] = None #str(uuidVal)
    return vesselShipmentDict
    
def main(argv):
    scenarioBase = argv[0]

    shipmentSchemaFilePath = "/home/share/Code/cptl-models/data/schema/shipment.schema.v2.json"
    vesselShipmentSchema = None
    with open(shipmentSchemaFilePath) as shipmentSchemaFile:
        vesselShipmentSchema = json.load(shipmentSchemaFile)
    shipmentSchemaFile.close()

    # Loop through the months
    commodityShipmentsInputFileBase = "/".join([scenarioBase, "flows/shipments"])
    generateShipments(commodityShipmentsInputFileBase, shipper=None)

    #for shipper in []: #["Crowley", "MSC", "King Ocean", "FIT"]:
    #    commodityShipmentsInputFileBase = "/".join([scenarioBase, "flows/shipments"])
    #    generateShipments(commodityShipmentsInputFileBase, shipper)

def generateShipments(commodityShipmentsInputFileBase, shipper):        
    # Generate shipment file
    shipmentInputFilePaths = [f for f in listdir(commodityShipmentsInputFileBase) if isfile(join(commodityShipmentsInputFileBase, f))]
    for shipmentInputFileName in shipmentInputFilePaths:
        shipmentInputFilePath = "/".join([commodityShipmentsInputFileBase, shipmentInputFileName])
        #if not "filtered" in shipmentInputFileName:
        #    continue
        with open(shipmentInputFilePath) as shipmentInputFile:
            shipmentJSON = json.load(shipmentInputFile)
        shipmentInputFile.close()
            
        results = \
            list(filter(lambda x: isIncludedVesselShipment(x), shipmentJSON["commodities"]))
        results = \
            list(map(lambda x: normalizeShipLine(x), results))
        results = \
            list(map(lambda x: roundTEU(x), results))
        #results = \
        #    list(map(lambda x: genUUID(x), results))
        
        if None != shipper:
            results = \
                list(filter(lambda x: x["shipper"] == shipper, results))
            shipmentInputFilePath = shipmentInputFilePath.replace("shipments/", f"shipments-{shipper}/")

        if len(results) > 0:
            resultJSON = {"commodities": results}
            
            shipmentOutputFilePath = shipmentInputFilePath.replace(".json", ".filtered.json")
            shipmentOutputFilePath = shipmentOutputFilePath.replace(":", "_")
            with open(shipmentOutputFilePath, 'w') as shipmentOutputFile:
                resultStr = json.dumps(resultJSON, indent=4)
                shipmentOutputFile.write(resultStr)
            shipmentOutputFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    
