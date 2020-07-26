"""
Created July 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from os import listdir
from os.path import isfile, join
from sqlite3 import Error
import json
import pandas as pd
import sqlite3
import sys

def usage():
    print("patchShipmentsWithBerthArrivalTimes.py <scenarioDir>")
    sys.exit(-1)

def main(argv):
    if len(argv) != 1:
        usage()

    scenarioDir = argv[0]
    simDBPath = "/".join([scenarioDir, "results/output.sqlite"])
    commodityShipmentsInputFileBase = "/".join([scenarioDir, "flows/shipments"])
    outputFileDir = "/".join([scenarioDir, "flows/shipments-opt"])

    patchShipments(commodityShipmentsInputFileBase, simDBPath, outputFileDir)

def patchShipments(commodityShipmentsInputFileBase, simDBPath, outputFileDir):
    # Generate shipment file
    shipmentInputFilePaths = [f for f in listdir(commodityShipmentsInputFileBase) if isfile(join(commodityShipmentsInputFileBase, f))]
    for shipmentInputFileName in shipmentInputFilePaths:
        shipmentInputFilePath = "/".join([commodityShipmentsInputFileBase, shipmentInputFileName])

        with open(shipmentInputFilePath) as shipmentInputFile:
            shipmentJSON = json.load(shipmentInputFile)
        shipmentInputFile.close()
        
        results = \
            list(filter(lambda x: patchEAT(simDBPath, x), shipmentJSON["commodities"]))

        if len(results) > 0:
            resultJSON = {"commodities": results}
            shipmentOutputFilePath = "/".join([outputFileDir, shipmentInputFileName])
            with open(shipmentOutputFilePath, 'w') as shipmentOutputFile:
                resultStr = json.dumps(resultJSON, indent=4)
                shipmentOutputFile.write(resultStr)
            shipmentOutputFile.close()

def patchEAT(simDBPath, vesselShipmentDict):
    name = vesselShipmentDict["name"]
    source = vesselShipmentDict["source"]
    nTEU = vesselShipmentDict["nTEU"]
    
    conn = None
    try:
        conn = sqlite3.connect(simDBPath)
    except Error as e:
        print(e)

    df = pd.read_sql_query(f"SELECT time FROM container WHERE container_name LIKE '{name}%' and source = 'Arrival'", conn)

    nTEUActual = df.shape[0]
    if nTEUActual != nTEU:
        raise Exception(f"Number expected for {name} not match actual ({nTEU} != {nTEUActual})")

    # Assuming all TEU in a bundle arrive at the same time
    teuIdx = 0
    time = df.iloc[ [teuIdx] ]["time"]

    vesselShipmentDict["EAT"] = float(time)
    return vesselShipmentDict
        
if __name__ == "__main__":
    main(sys.argv[1:])
