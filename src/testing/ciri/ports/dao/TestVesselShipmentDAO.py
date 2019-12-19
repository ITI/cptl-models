"""
Created February 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.VesselShipmentDAO import CSVODPairsVesselShipmentDAO
from jsonschema import validate
import json
import unittest

class TestCSVODPairsVesselShipmentDAO(unittest.TestCase):


    vesselCommoditiesInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/Commodity O-D Pairs FY2017.csv"        
    vesselScheduleSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/schedule.schema.json"
    vesselShipmentSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/shipment.schema.json"

    def testReadVesselCommodities(self):
        vsDAO = CSVODPairsVesselShipmentDAO()
        vesselCommodities = vsDAO.readVesselCommodities(self.vesselCommoditiesInputFilePath)
        self.assertEqual( len(vesselCommodities), 21397)
        print(vesselCommodities[0].date)
        print(vesselCommodities[0].date.month)
        
    def testConvertToPandasDataframe(self):
        vsDAO = CSVODPairsVesselShipmentDAO()
        vesselCommodities = vsDAO.readVesselCommodities(self.vesselCommoditiesInputFilePath)
        
        df = vsDAO.convertToPandasDataframe(vesselCommodities, discretized=False)
        print(df.head())
        print(df.dtypes)

        vesselCommoditiesData = vsDAO.discretize(vesselCommodities)
        df = vsDAO.convertToPandasDataframe(vesselCommoditiesData, discretized=True)
        print(df.head())
        print(df.dtypes)

class TestCSVVesselShipmentDAO(unittest.TestCase):
    
    vesselCommoditiesInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/PEV Commods by Vessel FY2018.csv"        
    vesselScheduleSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/schedule.schema.json"
    vesselShipmentSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/shipment.schema.json"
    
    def testReadVesselCommodities(self):
        vsDAO = CSVVesselShipmentDAO()
        vesselCommodities = vsDAO.readVesselCommodities(self.vesselCommoditiesInputFilePath)
        self.assertEqual( len(vesselCommodities), 85097 )
        
    def testExportVesselSchedule(self):
        vsDAO = CSVVesselShipmentDAO()
        vesselCommodities = vsDAO.readVesselCommodities(self.vesselCommoditiesInputFilePath)
        vesselScheduleJSON = vsDAO.exportVesselSchedule(vesselCommodities)        
        validate(vesselScheduleJSON, self.vesselShipmentSchemaFilePath)

        
if __name__ == '__main__':
    unittest.main()

