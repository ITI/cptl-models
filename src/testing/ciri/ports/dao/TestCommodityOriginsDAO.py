"""
Created on December 17, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from ciri.ports.dao.CommodityOriginsDAO import CSVCommodityOriginsDAO
import json
import unittest

class TestCSVCommodityOriginsDAO(unittest.TestCase):

    def setUp(self):
        self.scenarioBase = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/test-scenarios/onf2/"        
        self.commodityOriginsInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "PEV Trading Partners May FY2018.csv"])
        self.commodityCodeDictInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "HS Codes.csv"])
        self.coDAO = CSVCommodityOriginsDAO()
    
    def testReadCommodityOrigins(self):
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        self.assertEqual( len(commodityOrigins), 1070)

    def testReadCommmodityCodes(self):
        commodityCodes = self.coDAO.readCommodityCodes(self.commodityCodeDictInputFilePath)
        self.assertEqual( len(commodityCodes), 98)

    def testConvertToPandasDataframe(self):
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        df = self.coDAO.convertToPandasDataframe(commodityOrigins)
        print(df.head())
        print(df.dtypes)

    def testComputeCommodityGroupIntervals(self):
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        odDf = self.coDAO.convertToPandasDataframe(commodityOrigins)
        self.coDAO.computeCommodityGroupIntervals(odDf)
        self.assertEqual( len(self.coDAO.commodityGroupIntervals.keys()), 91 )
        
    def testGetOrigins(self):
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        odDf = self.coDAO.convertToPandasDataframe(commodityOrigins)
        self.coDAO.computeCommodityGroupIntervals(odDf)
        t = self.coDAO.getOrigins("97")
        print(t)
        
    def testPlotCommodityOrigins(self):
        commodityOrigins = self.coDAO.readCommodityOrigins(self.commodityOriginsInputFilePath)
        commodityCodes = self.coDAO.readCommodityCodes(self.commodityCodeDictInputFilePath)

        odDf = self.coDAO.convertToPandasDataframe(commodityOrigins)
        self.coDAO.computeCommodityGroupIntervals(odDf)
        commodityGroup = "97"
        outFilePath = f"/tmp/commodityGroup{commodityGroup}.png"
        self.coDAO.plotCommodityOrigins(commodityCodes, commodityGroup, outFilePath)

if __name__ == '__main__':
    unittest.main()
        
        
