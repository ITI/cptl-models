"""
Created April 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.dao.VesselShipmentDAO import CSVVesselShipmentDAO
from ciri.ports.util.ShipmentSerializer import BasicScenarioGenerator
import json
import logging
import os
import unittest

class TestBasicMeasurementDAO(unittest.TestCase):
    
    logging.basicConfig( filename="/tmp/BasicMeasurementDAO.log" )

    installHome = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des"    
    
    economicDataFY2017FilePath = installHome + "/data/everglades/TEU Report FY2017.csv"
    vesselScheduleFY2017FilePath = installHome + "/data/everglades/Vessel Calls Grid_FY 2017.csv"
    vesselCommoditiesFY2017FilePath = installHome + "/data/everglades/PEV Commods by Vessel FY2017.csv"       
    vesselODPairsFY2017FilePath = installHome + "/data/everglades/Commodity O-D Pairs FY2017.csv"
    
    dataSources = None

    def setUp(self):
        self.dataSources = {}
        self.dataSources["PEV.EconomicDataFY2017"] = \
            (economicDataFY2017FilePath, "CSVTEUReportDAO")
        self.dataSources["PEV.VesselCallsFY2017"] = \
            (vesselScheduleFY2017FilePath, "CSVVesselScheduleDAO")
        self.dataSources["PIERS.VesselCommoditiesFY2017"] = \
            (vesselCommoditiesFY2017FilePath, "CSVVesselShipmentDAO")
        self.dataSources["PIERS.CommoditiesODPairsFY2017"] = \
            (vesselODPairsFY2017FilePath, "CSVODPairsVesselShipmentDAO")

    def testCreate(self):
        basicScenarioGenerator = BasicScenarioGenerator.create(dataSources)
        # Unfiltered, just all the data
        self.assertEqual( len(dataSources.keys()), 3 )
        self.assertEqual( basicScenarioGenerator.df["PEV.EconomicDataFY2017"].shape, (180,5) )
        self.assertEqual( basicScenarioGenerator.df["PIERS.VesselCommoditiesFY2017"].shape, (2668, 0) )
        self.assertEqual( basicScenarioGenerator.df["PIERS.CommoditiesODPairsFY2017"].shape, (1742, 0) ) 
        
    def testGetDataSourceInventory(self):
        basicScenarioGenerator = BasicScenarioGenerator.create(self.dataSources)
        resultDataSources = basicScenarioGenerator.getDataSourceInventory()  
        
        self.assertEqual( len(resultDataSources), 4)
        self.assertTrue( "PEV.EconomicDataFY2017" in resultDataSources )
        self.assertTrue( "PEV.VesselCallsFY2017" in resultDataSources )
        self.assertTrue( "PIERS.VesselCommoditiesFY2017" in resultDataSources )
        self.assertTrue( "PIERS.CommoditiesODPairsFY2017" in resultDataSources )

    def testGetValidMeasurements(self):
        measurements["PEV.EconomicDataFY2017"]= [ "NumberOfLoadedTEUImport/Month" ]
        measurements["PEV.VesselCallsFY2017"] = [ "VesselNames/Hour", "ShippingLines/Hour" ]
        measurements["PIERS.VesselCommoditiesFY2017"] = [ "NumberOfLoadedTEUImport/Day", "VesselNames/Day", "ShippingLines/Day" ]
        measurements["PIERS.CommoditiesODPairsFY2017"] = [ "NumberOfLoadedTEUImport/Month", "NumberOfCommodityTEUImport/Month" ]

        basicScenarioGenerator = BasicScenarioGenerator.create(dataSources)

        economicDataMeasurements = basicScenarioGenerator.getValidMeasurements("PEV.EconomicDataFY2017")
        vesselCallMeasurements = basicScenarioGenerator.getValidMeasurements("PEV.VesselCallsFY2017")
        vesselCommoditiesMeasurements = basicScenarioGenerator.getValidMeasurements("PIERS.VesselCommoditiesFY2017")
        odPairsMeasurements = basicScenarioGenerator.getValidMeasurements("PIERS.CommoditiesODPairsFY2017")
        
        self.assertEqual( economicDataMeasurements, measurements["PEV.EconomicDataFY2017"] )
        self.assertEqual( vesselCallMeasurements, measurements["PEV.VesselCallsFY2017"] )
        self.assertEqual( vesselCommoditiesMeasurements, measurements["PIERS.VesselCommoditiesFY2017"] )
        self.assertEqual( odPairsMeasurements, measurements["PIERS.CommoditiesODPairsFY2017"] )

    def testGetMeasurement(self):
        basicScenarioGenerator = BasicScenarioGenerator.create(dataSources)
        
        econDf = basicScenarioGenerator.getMeasurement("PEV.EconomicDataFY2017#NumberOfLoadedTEUImport/Month")
        self.assertEqual( econDf.shape, (12,2) )
        self.assertEqual( econDf.columns, ["NumberOfLoadedTEUImport", "Month"] )
        
        vesselsDf = basicScenarioGenerator.getMeasurement("PEV.VesselCallsFY2017#VesselNames/Hour")
        self.assertEqual( vesselsDf.shape, (334, 2) ) 
        self.assertEqual( vesselsDf.columns, ["VesselNames", "Hour"] )
        
        linesDf = basicScenarioGenerator.getMeasurements("PEV.VesselCallsFY2017#ShippingLines/Hour")
        self.assertEqual( linesDf.shape( 334, 2) )
        self.assertEqual( linesDf.columns, ["ShippingLines", "Hour"] )
        
        teuDayDf = basicScenarioGenerator.getMeasurements("PIERS.VesselCommoditiesFY2017#NumberOfLoadedTEUImport/Day")
        self.assertEqual( teuDayDf.shape( 334, 2) )
        self.assertEqual( teuDayDf.columns, ["NumberOfLoadedTEUImport", "Day"] )

        vesselsDf2 = basicScenarioGenerator.getMeasurements("PIERS.VesselCommoditiesFY2017#VesselNames/Day")
        self.assertEqual( vesselsDf2.shape( 334, 2) )
        self.assertEqual( vesselsDf2.columns, ["VesselNames", "Day"] )

        linesDf2 = basicScenarioGenerator.getMeasurements("PEV.VesselCommoditiesFY2017#ShippingLines/Day")
        self.assertEqual( linesDf.shape( 334, 2) )
        self.assertEqual( linesDf.columns, ["ShippingLines", "Day"] )
        
        teuMonthDf = basicScenarioGenerator.getMeasurements("PIERS.CommoditiesODPairsFY2017#NumberOfLoadedTEUImport/Month")
        self.assertEqual( teuMonthDf.shape( 334, 2) )
        self.assertEqual( teuMonthDf.columns, ["NumberOfLoadedTEUImport", "Month"] )

        cTeuMonthDf = basicScenarioGenerator.getMeasurements("PIERS.CommoditiesODPairsFY2017#NumberOfCommodityTEUImport/Month")
        self.assertEqual( cTeuMonthDf.shape( 334, 3) )
        self.assertEqual( cTeuMonthDf.columns, ["NumberOfCommodityTEUImport", "CommodityGroup", "Month"]
        
        
        
    

        
