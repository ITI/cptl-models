"""
Created on February 25, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
import unittest

class TestCSVVesselSchedule(unittest.TestCase):

    def setUp(self):
        self.scenarioBase = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/test-scenarios/onf2"
        
        self.scheduleInputFilePath = "/".join([self.scenarioBase, "data/PEV-FY2018", "Vessel Calls GRID_FY 2018.csv"])
        self.networkFilePath = "/".join([self.scenarioBase, "networks/transportation.extended.json"])

        self.startTime = "2018-05-01 00:00:00-0500"
        self.workdayStart = "08:00"
        self.workdayEnd = "17:00"
        
        self.vesselDAO = CSVVesselScheduleDAO.create(self.networkFilePath, self.startTime, self.workdayStart, self.workdayEnd)

    def test_init(self):
        self.assertEqual(self.vesselDAO.networkFilePath, self.networkFilePath)

    def test_node_id(self):
        berthId = "33A"
        nodeId = self.vesselDAO.get_node_id(berthId)
        self.assertEqual(nodeId, "Berth 33")

    def test_get_minutes_from_start_time(self):
        min1 = self.vesselDAO.getMinutesFromStartTime("05/26/18 08:15-0500")
        self.assertTrue( 24 * 60 - min1 <= 1)   # Within 1 minuten bitte
        
    def testReadVesselSchedule(self):
        vesselSchedule = self.vesselDAO.readVesselSchedule(self.scheduleInputFilePath)
        self.assertEqual( len(vesselSchedule), 4214 )

    def testConvertToPandasDataframe(self):
        vesselSchedule = self.vesselDAO.readVesselSchedule(self.scheduleInputFilePath)
        
        df = self.vesselDAO.convertToPandasDataframe(vesselSchedule, discretized=False)
        print(df.head())
        print(df.dtypes)

if __name__ == '__main__':
    unittest.main()

        
