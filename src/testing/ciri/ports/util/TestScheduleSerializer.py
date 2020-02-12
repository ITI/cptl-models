"""
Created April 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.util.ScheduleSerializer import JSONScheduleSerializer
import os
import unittest

class TestJSONScheduleSerializer(unittest.TestCase):

    # In May, 8 of vessels don't have a match
    # In May, a discrepancy of about 3300 containers in May for
    #  loaded imports
    installHome = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des"
    vesselScheduleSchemaFilePath = installHome + "/data/schedule.schema.v2.json"
    scheduleInputFilePath = installHome + "/data/everglades/Vessel Calls Grid_FY 2017.csv"

    startDate, endDate = '2017-05-01', '2017-06-01'    
    startMonth = '2017-05'
    outfilePrefix = "/".join([installHome, "build", startMonth])

    def setUp(self):
        os.makedirs(self.outfilePrefix, exist_ok=True)
            
    def testCreate(self):
        scheduleSerializer = JSONScheduleSerializer.create(self.scheduleInputFilePath, \
                                                               self.vesselScheduleSchemaFilePath, \
                                                               self.startDate, \
                                                               self.endDate)
        self.assertEqual(scheduleSerializer.scheduleDf.shape[0], 180)
        
    def testGenerateSchedule(self):
        scheduleSerializer = JSONScheduleSerializer.create(self.scheduleInputFilePath, \
                                                               self.vesselScheduleSchemaFilePath, \
                                                               self.startDate, \
                                                               self.endDate)
        workdayStart = "08:00"
        workdayEnd = "17:00"
        graphOutfilePath = "/".join( [self.outfilePrefix, "transportation-network.json"] )
        shipmentOutfilePrefix = "/".join( [self.outfilePrefix, "shipments"] )
        vesselScheduleDict = scheduleSerializer.generateSchedule(workdayStart,\
                                                                     workdayEnd,\
                                                                     graphOutfilePath, \
                                                                     shipmentOutfilePrefix)
        shipments = vesselScheduleDict["shipments"]
        self.assertEqual(len(shipments), 180)        
        shipment = shipments[0]
        self.assertTrue(shipmentOutfilePrefix in shipment["shipment_file"])
        
        southportBerths = ['30','31','32','33A','33B','33C']
        berth_mask = ( scheduleSerializer.scheduleDf["arrivalBerth"].isin(southportBerths) )
        scheduleSerializer.scheduleDf = scheduleSerializer.scheduleDf[ berth_mask ]
        vesselScheduleDict = scheduleSerializer.generateSchedule(workdayStart,\
                                                                     workdayEnd,\
                                                                     graphOutfilePath, \
                                                                     shipmentOutfilePrefix)
        shipments = vesselScheduleDict["shipments"]
        self.assertEqual(len(shipments), 130)        
        shipment = shipments[0]
        self.assertTrue(shipmentOutfilePrefix in shipment["shipment_file"])


    def testOutputSchedule(self):
        scheduleSerializer = JSONScheduleSerializer.create(self.scheduleInputFilePath, \
                                                               self.vesselScheduleSchemaFilePath, \
                                                               self.startDate, \
                                                               self.endDate)
        workdayStart = "08:00"
        workdayEnd = "17:00"
        graphOutfilePath = "/".join( [self.outfilePrefix, "transportation-network.json"] )
        shipmentOutfilePrefix = "/".join( [self.outfilePrefix, "shipments"] )

        # Filter out southport berths
        southportBerths = ['30','31','32','33A','33B','33C']
        berth_mask = ( scheduleSerializer.scheduleDf["arrivalBerth"].isin(southportBerths) )
        scheduleSerializer.scheduleDf = scheduleSerializer.scheduleDf[ berth_mask ]

        vesselScheduleDict = scheduleSerializer.generateSchedule(workdayStart,\
                                                                     workdayEnd,\
                                                                     graphOutfilePath, \
                                                                     shipmentOutfilePrefix)
        outfilePath = "/".join( [self.outfilePrefix, "schedule.json"] )
        scheduleSerializer.outputSchedule(vesselScheduleDict, outfilePath)
        self.assertTrue( os.path.exists(outfilePath) )

if __name__ == '__main__':
    unittest.main()
        
