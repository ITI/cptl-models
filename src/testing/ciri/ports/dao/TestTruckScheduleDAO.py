"""
Created on March 18, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign.
All Rights Reserved
"""

from ciri.ports.dao.TruckScheduleDAO import SensorCSVTruckScheduleDAO
import unittest

class TestSensorCSVTruckScheduleDAO(unittest.TestCase):

    def setUp(self):
        self.truckDAO = SensorCSVTruckScheduleDAO()

    def testReadTruckSchedule(self):
        scheduleInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/Traffic Sensor Data 2017.csv"
        truckSchedule = self.truckDAO.readTruckSchedule(scheduleInputFilePath)
        self.assertEqual( len(truckSchedule), 1982)

    def testConvertToPandasDataframe(self):
        scheduleInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/Traffic Sensor Data 2017.csv"
        truckSchedule = self.truckDAO.readTruckSchedule(scheduleInputFilePath)

        df = self.truckDAO.convertToPandasDataframe(truckSchedule, discretized=False)
        print(df.head())
        print(df.dtypes)

if __name__ == '__main__':
    unittest.main()

