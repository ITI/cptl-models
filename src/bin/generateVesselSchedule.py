"""
Created on December 16, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.dao.VesselArrivalDAO import VesselScheduleVesselArrivalEventDAO, VesselCommoditiesVesselArrivalEventDAO, VesselArrivalEventFusionDAO
from jsonschema import validate
import json
import numpy as np
import sys

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
    
    scheduleSchemaFilePath = "/home/share/Code/cptl-models/data/schema/schedule.schema.v2.json"
    vesselScheduleSchema = None
    with open(scheduleSchemaFilePath) as scheduleSchemaFile:
        vesselScheduleSchema = json.load(scheduleSchemaFile)
    scheduleSchemaFile.close()

    dayEpsilon = 0
    fusionMethod = "SHIP_DATE"
    scheduleInputFilePath = "/".join([scenarioBase, "data/VesselCalls.csv"])
    commoditiesInputFilePath = "/".join([scenarioBase, "data/ImportedCommods.csv"])
    scheduleOutputFilePath = "/".join([scenarioBase, "flows/schedule.raw.json"])

    vesselDAO = VesselArrivalEventFusionDAO.create(scheduleInputFilePath, commoditiesInputFilePath)
    scheduleVesselArrivalEvents = vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
    commoditiesVesselArrivalEvents = vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents
    vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
    vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )

    vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents,\
                                      commoditiesVesselArrivalEvents,\
                                      dayEpsilon,\
                                      fusionMethod)

    unmatchedScheduleVesselArrivalEvents = vesselDAO.getUnmatchedVesselArrivalEvents("VesselSchedule")
    unmatchedCommoditiesVesselArrivalEvents = vesselDAO.getUnmatchedVesselArrivalEvents("Commodities")
        
    monthLabel = month
    scheduleInputFilePath = "/".join([scenarioBase, "data/VesselCalls.csv"])
    commoditiesInputFilePath = "/".join([scenarioBase, "data/ImportedCommods.csv"])

    setName = "intersection"
    shipmentOutfilePrefix = "shipments"
    disruptionsList = []
    transportationNetworkFilePath = "../networks/transportation.gnsi"
    startTime = getStartTime(month)
    workdayStart = "08:00"
    workdayEnd = "17:00"

    vesselScheduleDict = vesselDAO.getVesselSchedule(setName,\
                                                     shipmentOutfilePrefix,\
                                                     disruptionsList,\
                                                     transportationNetworkFilePath,\
                                                     startTime,\
                                                     workdayStart,\
                                                     workdayEnd)
    validate(vesselScheduleDict, vesselScheduleSchema)
    
    with open(scheduleOutputFilePath, 'w') as outFile:
        vesselScheduleJSON = json.dumps(vesselScheduleDict, indent=4)
        print(len(vesselScheduleDict["shipments"]))
        outFile.write(vesselScheduleJSON)
    outFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
