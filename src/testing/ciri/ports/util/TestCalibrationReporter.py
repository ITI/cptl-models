"""
Created April 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.util.CalibrationReporter import CoreCalibrationReporter, EconomicCalibrationReporter
import json
import unittest

class TestEconomicCalibrationReporter(unittest.TestCase):

    ecReporter = None

    def setUp(self):
        scenarioDir = "data/test-scenarios/PEV-SouthPortImports.FY2018_10"
        configDir = "/".join([scenarioDir, "config"])

        # Data sources
        dataSourceInvPath = "/".join([scenarioDir, "config/inventory.json"])
        with open(dataSourceInvPath) as dataSourceInvFile:
            dataSourceInv = json.load(dataSourceInvFile)
        month = 10
        simDuration = 15

        self.assertEqual(len(dataSourceInv.keys()), 8)
        self.ecReporter = EconomicCalibrationReporter.create(scenarioDir, configDir, dataSourceInv, month, simDuration)

    def testCreate(self):
        self.assertTrue( self.ecReporter != None )
        self.assertEqual( len(self.ecReporter.dataSourceDict.keys()), 8)

    def testLoadDataSources(self):
        
        self.ecReporter.loadDataSources()
        self.assertEqual( len(self.ecReporter.dataSourceDict.keys()), 8)
        hs2CodesUrn = "urn:cite:PDT_Econ:HS2Codes"
        hs2CodesDf = \
            self.ecReporter.dataFramesDict[ hs2CodesUrn ]
        self.assertEqual(hs2CodesDf.shape[0], 98)
        
        importedCommodsUrn = "urn:cite:PEV:ImportedCommods.FY2018_10"
        importedCommodsDf = \
            self.ecReporter.dataFramesDict[ importedCommodsUrn ]
        self.assertEqual(importedCommodsDf.shape[0], 1581)
        
        economicAnalysisUrn = "urn:cite:PEV:PDTInputEconomicAnalysis.FY2018"
        economicAnalysisDf = \
            self.ecReporter.selectAllCountries(economicAnalysisUrn)
        self.assertEqual(economicAnalysisDf.shape[0], 75)
        
        #outputDbUrn = "urn:cite:PEV:PDTOutputDB.FY2018_10"
        #commodityTEUDf = \
        #    self.ecReporter.selectAllHS2CodeTEU(outputDbUrn)
        #self.assertEqual(commodityTEUDf.shape[0], 30)
        
    def testGetMeasurement(self):
        self.ecReporter.loadDataSources()
        mUrn = "urn:cite:PDT_Econ:NumberOfCountries"
        result = self.ecReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT_Econ:NumberOfHS2Codes"
        result = self.ecReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT_Econ:PercentTEUPerHS2Code"
        result = self.ecReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT_Econ:PercentTEUPerCountry"
        result = self.ecReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT_Econ:NumberCountriesPerHS2Code"
        result = self.ecReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn= "urn:cite:PDT_Econ:PercentTEUPerHS2Code,Country"
        results = self.ecReporter.getMeasurement(mUrn)
        for key in results.keys():
            print(key)
            print(results[key].head())
        
        #mUrn = "urn:cite:PDT_Econ:USDValueOfHS2CodeTEU"
        #result = self.ecReporter.getMeasurement(mUrn)
        #print(result.head())

        #mUrn = "urn:cite:PDT_Econ:USDValueOfTEUPerCountry"
        #result = self.ecReporter.getMeasurement(mUrn)
        #print(result.head())

        #mUrn = "urn:cite:PDT_Econ:USDValueOfHS2CodeTEUPerCountry"
        #result = self.ecReporter.getMeasurement(mUrn)
        #print(result.head())
        
class TestCoreCalibrationReporter(unittest.TestCase):

    cReporter = None
    
    def setUp(self):
        scenarioDir = "data/test-scenarios/PEV-SouthPortImports.FY2018_10"
        configDir = "config"

        # Data sources
        dataSourceKeys = ["urn:cite:PEV:VesselCalls.FY2018_10",\
                          "urn:cite:PEV:TEUReport.FY2018",\
                          "urn:cite:PEV:ImportedCommods.FY2018_10",\
                          "urn:cite:PEV:SouthPortImports.FY2018_10#Inputs.DESInputSchedule",\
                          "urn:cite:PEV:SouthPortImports.FY2018_10#Outputs.DESOutputDB"]

        vesselCallsPath = "data/VesselCalls.csv"
        teuReportPath = "data/TEU Report FY2018.csv"
        importedCommodsPath = "data/ImportedCommods.csv"
        vesselSchedulePath = "flows/schedule.json"
        desDatabasePath = "results/output.sqlite"
        
        dataSourcePaths = [ vesselCallsPath,
                            teuReportPath,
                            importedCommodsPath,
                            vesselSchedulePath,
                            desDatabasePath ]
        dataSourceDict = dict(zip(dataSourceKeys, dataSourcePaths))
        month = 10
        simDuration = 15

        self.assertEqual(len(dataSourceDict.keys()), 5)
        self.cReporter = CoreCalibrationReporter.create(scenarioDir, configDir, dataSourceDict, month, simDuration)

    def testCreate(self):
        self.assertTrue( self.cReporter != None )
        self.assertEqual( len(self.cReporter.dataSourceDict.keys()), 5)

    def testLoadDataSources(self):
        self.cReporter.loadDataSources()
        self.assertEqual( len(self.cReporter.dataSourceDict.keys()), 5)

        vesselCallsUrn = "urn:cite:PEV:VesselCalls.FY2018_10"
        vesselCallsDf =\
            self.cReporter.dataFramesDict[ vesselCallsUrn ]
        self.assertEqual(vesselCallsDf.shape[0], 62)

        vesselScheduleUrn = "urn:cite:PEV:SouthPortImports.FY2018_10#Inputs.DESInputSchedule"
        vesselSchedule = self.cReporter.dataFramesDict[ vesselScheduleUrn ]
        self.assertEqual( len(vesselSchedule["shipments"]), 18 )
    
        outputDbUrn = "urn:cite:PEV:SouthPortImports.FY2018_10#Outputs.DESOutputDB"
        simVesselCallsDf = self.cReporter.selectAllVessels(outputDbUrn)
        self.assertEqual(simVesselCallsDf.shape[0], 18)

    def testGetMeasurement(self):
        self.cReporter.loadDataSources()
        mUrn = "urn:cite:PDT:NumberOfVessels"
        result = self.cReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT:NumberOfTEU"
        result = self.cReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT:VesselDwellTime"
        result = self.cReporter.getMeasurement(mUrn)
        print(result.head())

        mUrn = "urn:cite:PDT:TEUTransitTime"
        result = self.cReporter.getMeasurement(mUrn)
        print(result.head())
        
if __name__ == '__main__':
    unittest.main()
