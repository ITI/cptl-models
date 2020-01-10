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

def main(argv):
    scenarioBase = argv[0]

    shipmentSchemaFilePath = "/Users/polutropos/Documents/Repositories/CIRI/cptl-models/data/schema/shipment.schema.v2.json"
    vesselShipmentSchema = None
    with open(shipmentSchemaFilePath) as shipmentSchemaFile:
        vesselShipmentSchema = json.load(shipmentSchemaFile)
    shipmentSchemaFile.close()

    # Loop through the months
    for month in list(range(10,13)) + list(range(1,10)):
        print(month)
        commodityShipmentsInputFileBase = "/".join([scenarioBase, "flows/PEV-FY2018", f"{month}/shipments"])
        
        shipmentInputFilePaths = [f for f in listdir(commodityShipmentsInputFileBase) if isfile(join(commodityShipmentsInputFileBase, f))]
        for shipmentInputFileName in shipmentInputFilePaths:
            shipmentInputFilePath = "/".join([commodityShipmentsInputFileBase, shipmentInputFileName])
            with open(shipmentInputFilePath) as shipmentInputFile:
                shipmentJSON = json.load(shipmentInputFile)
            shipmentInputFile.close()
            
            results = \
                list(filter(lambda x: isIncludedVesselShipment(x), shipmentJSON["commodities"]))
            results = \
                list(map(lambda x: normalizeShipLine(x), results))
            results = \
                list(map(lambda x: roundTEU(x), results))

            resultJSON = {"commodities": results}
            
            shipmentOutputFilePath = shipmentInputFilePath.replace(".json", ".filtered.json")
            with open(shipmentOutputFilePath, 'w') as shipmentOutputFile:
                resultStr = json.dumps(resultJSON, indent=4)
                shipmentOutputFile.write(resultStr)
            shipmentOutputFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])
    
