"""
Created April 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
from jsonschema import validate
import json
import uuid

class JSONScheduleSerializer():

    scheduleDf = None
    startDate, endDate = None, None
    vesselScheduleSchema = None

    @staticmethod
    def create(scheduleInputFilePath, vesselScheduleSchemaFilePath, startDate, endDate):
        scheduleSerializer = JSONScheduleSerializer()

        vesselDAO = CSVVesselScheduleDAO()
        vesselSchedule = vesselDAO.readVesselSchedule(scheduleInputFilePath)
        vesselDf = vesselDAO.convertToPandasDataframe(vesselSchedule, discretized=False)

        scheduleSerializer.startDate = startDate
        scheduleSerializer.endDate = endDate

        with open(vesselScheduleSchemaFilePath) as vesselScheduleSchemaFile:
            scheduleSerializer.vesselScheduleSchema = json.load(vesselScheduleSchemaFile)
        
        # select the date range that we want
        date_mask2 = (vesselDf['startTime'] >= startDate) & (vesselDf['startTime'] < endDate)
        container_mask = vesselDf['cargoType'] == 'CONTAINER'
        monthVesselDf = vesselDf[date_mask2 & container_mask]
        scheduleSerializer.scheduleDf = monthVesselDf
        return scheduleSerializer

    def generateSchedule(self, workdayStart,  workdayEnd, \
                             graphOutfilePath, shipmentOutfilePrefix):
        vesselScheduleDict = {}
        vesselScheduleDict["disruptions"] = []
        vesselScheduleDict["network"] = graphOutfilePath
        vesselScheduleDict["shipments"] = []
        vesselScheduleDict["start_time"] = self.startDate + " 00:00:00-0400"
        vesselScheduleDict["workday_end"] = workdayStart
        vesselScheduleDict["workday_start"] = workdayEnd

        for idx, row in self.scheduleDf.iterrows():
            vesselArrivalDateTime = row['startTime']
            vesselDepartureDateTime = row['endTime']
            vesselArrivalDate = "-".join([str(vesselArrivalDateTime.year), str(vesselArrivalDateTime.month), str(vesselArrivalDateTime.day)])
            vesselDepartureDate = "-".join([str(vesselDepartureDateTime.year), str(vesselDepartureDateTime.month), str(vesselDepartureDateTime.day)])

            vesselArrivalEvent = {}
            vesselArrivalEvent["arrival_node"] = "PEV"
            vesselArrivalEvent["departure_node"] = "PEV"
            berthNum = str(row['arrivalBerth'])
            vesselArrivalEvent["destination_node"] = "Berth " + berthNum
            day = row['startTime'].day
            vesselName = row['shipName']
            shipmentKey = "-".join([vesselName, str(vesselArrivalDateTime), str(vesselDepartureDateTime)])
            shipmentFileName = ".".join([ "shipments", shipmentKey, "json" ])
            shipmentFilePath = "/".join([shipmentOutfilePrefix, shipmentFileName])
            vesselArrivalEvent["shipment_file"] = shipmentFilePath
            vesselArrivalEvent["shipment_uuid"] = str(uuid.uuid4())
            vesselArrivalEvent["shipper"] = row["shippingLine"]
            vesselArrivalEvent["time"] = row["startTime"].strftime("%Y-%m-%d %H:%M:%S%z")
            vesselScheduleDict["shipments"].append(vesselArrivalEvent)
        
        return vesselScheduleDict

    def outputSchedule(self, vesselScheduleDict, outfilePath):
        # Make sure we are generating valid output
        validate(vesselScheduleDict, self.vesselScheduleSchema)
        result = json.dumps(vesselScheduleDict, indent=4)
        with open(outfilePath, 'w') as outFile:
            outFile.write(result)
        outFile.close()


