"""
Created on March-April, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019, University of Illinois at Urbana Champaign.
All rights reserved.
"""
from ciri.ports.dao.VesselShipmentDAO import CSVVesselShipmentDAO
from ciri.ports.util.ShipmentSerializer import JSONShipmentSerializer
import json
import logging
import os
import unittest

class TestJSONShipmentSerializer(unittest.TestCase):
    
    logging.basicConfig( filename="/tmp/scenariogen.log") 

    # Let's stick with May since there is the least difference
    #   between the number of imported, loaded TEUs billed and the 
    #   number of TEU in the commodities per vessel spreadsheet

    installHome = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des"

    vesselScheduleInputFilePath = installHome + "/data/everglades/Vessel Calls Grid_FY 2017.csv"
    vesselCommoditiesInputFilePath = installHome + "/data/everglades/PEV Commods by Vessel FY2017.csv"       
    vesselODPairsInputFilePath = installHome + "/data/everglades/Commodity O-D Pairs FY2017.csv"
    vesselShipmentSchemaFilePath = installHome + "/data/shipment.schema.v2.json"
    startDate, endDate = '2017-05-01', '2017-06-01'

    startMonth = '2017-05'
    outfilePrefix = "/".join([installHome, "build", startMonth])

    def setUp(self):
        os.makedirs(self.outfilePrefix, exist_ok=True)
        os.makedirs(self.outfilePrefix + "/shipments", exist_ok=True)

 
    def testCreate(self):
        shipmentSerializer = JSONShipmentSerializer.create( self.vesselScheduleInputFilePath,\
                                                                self.vesselCommoditiesInputFilePath, \
                                                                self.vesselODPairsInputFilePath, \
                                                                self.vesselShipmentSchemaFilePath,\
                                                                self.startDate,\
                                                                self.endDate)
        # vessels, not filtering for southport
        self.assertEqual(shipmentSerializer.vsDf.shape[0], 180)
        # 2668 commodity bundles
        self.assertEqual(shipmentSerializer.vcDf.shape[0], 2668)
        # 1742 O-D, per-commodity pairs
        self.assertEqual(shipmentSerializer.odDf.shape[0], 1742)


    def testGetVesselCommodities(self):
        shipmentSerializer = JSONShipmentSerializer.create( self.vesselScheduleInputFilePath,\
                                                                self.vesselCommoditiesInputFilePath, \
                                                                self.vesselODPairsInputFilePath, \
                                                                self.vesselShipmentSchemaFilePath,\
                                                                self.startDate,\
                                                                self.endDate)
        # Makes a difference, be sure to just include the day, not the hour, min, etc
        vesselName = "K-BREEZE"
        vesselArrivalTime = '2017-05-01'
        vesselDepartureTime = '2017-05-09'
        vesselCommoditiesDf = shipmentSerializer.getVesselCommodities(vesselName,\
                                                                          vesselArrivalTime,\
                                                                          vesselDepartureTime)
        self.assertTrue( vesselCommoditiesDf.shape[0] == 17 )
        
        # We have an entry for CARIBE NAVIGATOR, but this is for exported commodities
        # Same with KATHARINA B, ALLEGRO, DENEB J
        vsVessels = shipmentSerializer.vsDf['shipName'].unique()
        vcVessels = shipmentSerializer.vcDf['vesselName'].unique()        
        vsVesselSet = set(vsVessels.tolist())
        vcVesselSet = set(vcVessels.tolist())

        sharedVessels = vcVesselSet & vsVesselSet
        matchedVesselPct = len(sharedVessels) / len(vsVesselSet)
        self.assertTrue(matchedVesselPct >= 0.90)
        
        missingVessels = vsVesselSet - sharedVessels
        # {'SCM ELPIDA', 'ROTHORN', 'CHARLOTTE', 'ELISABETH-S.', 'CARIBE NAVIGATOR', 'VANTAGE', 'E.R. CAEN'}
        # THESE LOOK TO BE SHIPS WITH EXCLUSIVELY EXPORTS 
        #  OR LEGITIMATE MISSES

        #vesselName = "SCM ELPIDA"
        #vesselArrivalTime = '2017-05-11'
        #vesselDepartureTime = '2017-05-13'
        #vesselCommoditiesDf = shipmentSerializer.getVesselCommodities(vesselName,\
        #                                                                  vesselArrivalTime,\
        #                                                                  vesselDepartureTime)
        #self.assertTrue( vesselCommoditiesDf.shape[0] == 17 )


    def testComputeIntervals(self):
        shipmentSerializer = JSONShipmentSerializer.create( self.vesselScheduleInputFilePath,\
                                                                self.vesselCommoditiesInputFilePath, \
                                                                self.vesselODPairsInputFilePath, \
                                                                self.vesselShipmentSchemaFilePath,\
                                                                self.startDate,\
                                                                self.endDate)
        self.assertEqual( len(shipmentSerializer.intervals.keys()), 66 )
    
    def testGenerateShipments(self):
        shipmentSerializer = JSONShipmentSerializer.create( self.vesselScheduleInputFilePath,\
                                                                self.vesselCommoditiesInputFilePath, \
                                                                self.vesselODPairsInputFilePath, \
                                                                self.vesselShipmentSchemaFilePath,\
                                                                self.startDate,\
                                                                self.endDate)
        shipmentsDict = shipmentSerializer.generateShipments()
        vesselCalls = shipmentsDict.keys()
        self.assertEqual( len(vesselCalls), 180 )
        
        # Any filtering by southport berths?
        #vesselCall = vesselCalls.keys[0]
        #vesselCallShipments = shipmentsDict[vesselCall]
        #self.assertEqual( len(vesselCallShipments), 50 )
                                                            
    def testOutputShipments(self):
        shipmentSerializer = JSONShipmentSerializer.create( self.vesselScheduleInputFilePath,\
                                                                self.vesselCommoditiesInputFilePath, \
                                                                self.vesselODPairsInputFilePath, \
                                                                self.vesselShipmentSchemaFilePath,\
                                                                self.startDate,\
                                                                self.endDate)
        shipmentsDict = shipmentSerializer.generateShipments()
        outfilePath = "/".join( [self.outfilePrefix, "shipments"] )

        shipmentSerializer.outputShipments(shipmentsDict, outfilePath)


if __name__ == '__main__':
    unittest.main()
    
