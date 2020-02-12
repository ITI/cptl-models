"""
Created on February 25, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.VesselArrivalDAO import VesselScheduleVesselArrivalEventDAO, VesselCommoditiesVesselArrivalEventDAO, VesselArrivalEventFusionDAO

from ciri.ports.dao.CommodityOriginsDAO import CSVCommodityOriginsDAO
from jsonschema import validate
import json
import numpy as np
import unittest
import uuid

class TestVesselScheduleVesselArrivalEventDAO(unittest.TestCase):

    def setUp(self):
        self.scenarioBase = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/test-scenarios/onf2"
        self.scheduleInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "Vessel Calls GRID_May FY 2018.csv"])
        self.vesselDAO = VesselScheduleVesselArrivalEventDAO.create(self.scheduleInputFilePath)

    def testReadVesselSchedule(self):
        self.assertEqual( len(self.vesselDAO.vesselArrivalEvents), 327 )


    def testConvertToPandasDataframe(self):
        df = self.vesselDAO.convertToPandasDataframe()
        df = df[ df["cargoType"] == "CONTAINER" ]
        self.assertEqual( df.shape[0], 173 )


class TestVesselCommoditiesArrivalEventDAO(unittest.TestCase):

    def setUp(self):
        self.scenarioBase = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/test-scenarios/onf2/"
        self.commoditiesInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "PEV Imported Commods by Vessel May FY2018.csv"])
        self.vesselDAO = VesselCommoditiesVesselArrivalEventDAO.create(self.commoditiesInputFilePath)

    def testReadVesselSchedule(self):
        self.assertEqual( len(self.vesselDAO.vesselArrivalEvents), 203 )

    def testConvertToPandasDataframe(self):
        df = self.vesselDAO.convertToPandasDataframe()
        print(df.head())
        print(df.dtypes)

class TestVesselArrivalEventFusionDAO(unittest.TestCase):
    def setUp(self):
        scheduleSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/schedule.schema.v2.json"
        shipmentSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/shipment.schema.v2.json"

        self.scenarioBase = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/test-scenarios/onf2/"
        self.scheduleInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "Vessel Calls GRID_May FY 2018.csv"])
        self.commoditiesInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "PEV Imported Commods by Vessel May FY2018.csv"])
        self.commodityOriginsInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "PEV Trading Partners May FY2018.csv"])
        self.commodityCodeDictInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "HS Codes.csv"])

        self.vesselDAO = \
            VesselArrivalEventFusionDAO.create(self.scheduleInputFilePath,\
                                                   self.commoditiesInputFilePath)

        with open(scheduleSchemaFilePath) as scheduleSchemaFile:
            self.vesselScheduleSchema = json.load(scheduleSchemaFile)
        
        with open(shipmentSchemaFilePath) as shipmentSchemaFile:
            self.vesselShipmentSchema = json.load(shipmentSchemaFile)

        self.coDAO = \
            CSVCommodityOriginsDAO()
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        odDf = self.coDAO.convertToPandasDataframe(commodityOrigins)
        self.coDAO.computeCommodityGroupIntervals(odDf)

    def testFuseVesselArrivalEvents(self):
        scheduleVesselArrivalEvents = self.vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
        commoditiesVesselArrivalEvents = self.vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents

        dayEpsilon = 0
        print("# First pass:  Same shipName and overlapping dates")
        fusionMethod = "SHIP_DATE"
        self.vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
        self.vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )
        self.vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents, \
                                                   commoditiesVesselArrivalEvents,\
                                                   dayEpsilon,\
                                                   fusionMethod)


        unmatchedScheduleVesselArrivalEvents = self.vesselDAO.getUnmatchedVesselArrivalEvents("VesselSchedule")
        unmatchedCommoditiesVesselArrivalEvents = self.vesselDAO.getUnmatchedVesselArrivalEvents("Commodities")

        setName = "intersection"
        df = self.vesselDAO.convertToPandasDataframe(setName)
        print(df.shape)
        #print(df.head())

        setName =  "unmatched_schedule"
        df = self.vesselDAO.convertToPandasDataframe(setName)
        df = df[ df["cargoType"] == "CONTAINER" ]
        # filter out by berth
        print(df.shape)
        #print(df)
        
        setName =  "unmatched_commodities"
        df = self.vesselDAO.convertToPandasDataframe(setName)
        print(df.shape)
        #print(df.head())
        
    def testGetVesselArrivals(self):
        scheduleVesselArrivalEvents = self.vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
        commoditiesVesselArrivalEvents = self.vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents

        dayEpsilon = 0
        print("# First pass:  Same shipName and overlapping dates")
        fusionMethod = "SHIP_DATE"
        self.vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
        self.vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )
        self.vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents, \
                                                   commoditiesVesselArrivalEvents,\
                                                   dayEpsilon,\
                                                   fusionMethod)

        # Get the vessel arrivals and validate
        setName = "intersection"
        shipmentOutfilePrefix = "shipments"
        disruptionsList = []
        transportationNetworkFilePath = "../network/transportation.json"
        startTime = "2018-05-01 00:00:00-0400"
        workdayStart = "08:00"
        workdayEnd = "17:00"

        vesselScheduleDict = self.vesselDAO.getVesselSchedule(setName,\
                                                                  shipmentOutfilePrefix,\
                                                                  disruptionsList,\
                                                                  transportationNetworkFilePath,\
                                                                  startTime,\
                                                                  workdayStart,\
                                                                  workdayEnd)
        validate(vesselScheduleDict, self.vesselScheduleSchema)
        self.assertEqual( len(vesselScheduleDict["shipments"]), 135 )
        
    def testGetVesselShipments(self):
        scheduleVesselArrivalEvents = self.vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
        commoditiesVesselArrivalEvents = self.vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents

        dayEpsilon = 0
        print("# First pass:  Same shipName and overlapping dates")
        fusionMethod = "SHIP_DATE"
        self.vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
        self.vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )
        self.vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents, \
                                                   commoditiesVesselArrivalEvents,\
                                                   dayEpsilon,\
                                                   fusionMethod)
        vesselShipmentsDict = self.vesselDAO.getVesselShipments("intersection", self.coDAO)
        self.assertEqual(len(vesselShipmentsDict.keys()), 135)
        for shipmentKey in vesselShipmentsDict:
            shipments = vesselShipmentsDict[shipmentKey]
            shipmentsDict = { "commodities": shipments }
            validate(shipmentsDict, self.vesselShipmentSchema)

if __name__ == '__main__':
    unittest.main()

        
