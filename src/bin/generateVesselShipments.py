"""
Created on December 16, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.dao.VesselArrivalDAO import VesselScheduleVesselArrivalEventDAO, VesselCommoditiesVesselArrivalEventDAO, VesselArrivalEventFusionDAO
from ciri.ports.dao.CommodityOriginsDAO import CSVCommodityOriginsDAO
from jsonschema import validate
import json
import numpy as np
import os
import shutil
import sys
import unittest

def initializeDir(dirPath):
    if os.path.isdir(dirPath):
        try:
            shutil.rmtree(dirPath)
        except OSError:
            print(f"Deletion of directory {dirPath} failed")
    os.mkdir(dirPath)

def getStartTime(month):
    result = None
    if month in range(10,13):
        result = f"2017-{month:02d}-01 00:00:00-0400"
    else:
        result = f"2018-{month:02d}-01 00:00:00-0400"
    return result 

def main(argv):
    scenarioBase = argv[0]
    month = int(argv[1])
    
    commodityCodeDictInputFilePath = "/".join([scenarioBase, "data/HS Codes.csv"])    
    shipmentSchemaFilePath = "/home/share/Code/cptl-models/data/schema/shipment.schema.v2.json"
    vesselShipmentSchema = None
    with open(shipmentSchemaFilePath) as shipmentSchemaFile:
        vesselShipmentSchema = json.load(shipmentSchemaFile)
    shipmentSchemaFile.close()

    # Loop through the months
    #for month in list(range(10,13)) + list(range(1,10)):
    #    print(month)

    # -- set up the vessel arrival event fusion DAO
    dayEpsilon = 0
    fusionMethod = "SHIP_DATE"
    scheduleInputFilePath = "/".join([scenarioBase, "data/VesselCalls.csv"])
    commoditiesInputFilePath = "/".join([scenarioBase, "data/ImportedCommods.csv"])
    scheduleOutputFilePath = "/".join([scenarioBase, "flows/schedule.json"])

    vesselDAO = VesselArrivalEventFusionDAO.create(scheduleInputFilePath, commoditiesInputFilePath)
    scheduleVesselArrivalEvents = vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
    commoditiesVesselArrivalEvents = vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents
    vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
    vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )
        
    vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents,\
                                      commoditiesVesselArrivalEvents,\
                                      dayEpsilon,\
                                      fusionMethod)

    # -- set up the commodity origins DAO
    commodityOriginsInputFilePath = "/".join([scenarioBase, "data/CommodityOrigins.csv"])
    commodityShipmentsOutputFileBase = "/".join([scenarioBase, "flows/shipments"])
    commodityOriginsOutputFileBase = "/".join([scenarioBase, "results/commodityOrigins"])

    initializeDir(commodityShipmentsOutputFileBase)
    initializeDir(commodityOriginsOutputFileBase)
        
    for shipper in ["Crowley", "MSC","King Ocean", "FIT"]:
        commodityShipmentsOutputFileBase2 = "/".join([scenarioBase, "flows", f"shipments-{shipper}"])
        initializeDir(commodityShipmentsOutputFileBase2)
            
        coDAO = CSVCommodityOriginsDAO()
        commodityOrigins = coDAO.readCommodityOrigins(commodityOriginsInputFilePath)
        odDf = coDAO.convertToPandasDataframe(commodityOrigins)
        coDAO.computeCommodityGroupIntervals(odDf)

        scheduleVesselArrivalEvents = vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
        commoditiesVesselArrivalEvents = vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents

        # -- set up the shipments output
        startTime = getStartTime(month)
        vesselShipmentsDict = vesselDAO.getVesselShipments("intersection", startTime, coDAO)
        for shipmentKey in vesselShipmentsDict:
            shipments = vesselShipmentsDict[shipmentKey]
            shipmentsDict = { "commodities": shipments }
            validate(shipmentsDict, vesselShipmentSchema)
            shipmentFileName = f"{shipmentKey}.json"
            outputFilePath = "/".join([commodityShipmentsOutputFileBase, shipmentFileName])
            with open(outputFilePath, 'w') as outFile:
                shipmentJSON = json.dumps(shipmentsDict, indent=4)
                outFile.write(shipmentJSON)
            outFile.close()
        
        # -- output commodity origin plots
        commodityCodes = coDAO.readCommodityCodes(commodityCodeDictInputFilePath)
        for commodityGroup in commodityCodes.keys():
            plotFileName = f"{commodityGroup}.png"
            outFilePath = "/".join([commodityOriginsOutputFileBase, plotFileName])
            coDAO.plotCommodityOrigins(commodityCodes, commodityGroup, outFilePath)
        
if __name__ == "__main__":
    main(sys.argv[1:])

