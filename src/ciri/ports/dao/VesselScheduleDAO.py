"""
Created on February 19, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved.
"""
from datetime import datetime, timedelta
from sklearn.decomposition import PCA
import collections
import csv
import dateutil.tz as tz
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import uuid


VesselVisitEvent = collections.namedtuple('VesselVisitEvent', \
                                              'id startTime endTime shipName cargoType shippingLine arrivalBerth departureBerth gt')

class CSVVesselScheduleDAO():

    """
    Class used to instantiate a Vessel Schedule from a static vessel schedule CSV file.
    """

    networkFilePath = None
    startTime = None
    workdayStart = None
    workdayEnd = None

    _measurements = [ "VesselNames/Hour", "ShippingLines/Hour" ]

    @staticmethod
    def create(networkFilePath, startTime, workdayStart, workdayEnd):
        vesselDAO = CSVVesselScheduleDAO()

        vesselDAO.networkFilePath = networkFilePath
        vesselDAO.startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S%z")
        vesselDAO.workdayStart = workdayStart
        vesselDAO.workdayEnd = workdayEnd
        return vesselDAO
        
    def get_node_id(self, value):
        value = value[:2]
        return "Berth " + value

    def getMinutesFromStartTime(self, timestamp):
        """
        Get the number of minutes from the origin time
        """
        dt = datetime.strptime(timestamp, "%m/%d/%y %H:%M%z")
        return int( ( dt - self.startTime ).total_seconds() / 60 )

    def shouldSchedule(self, visitEvent):
        result = False
        isContainer = ( "CONTAINER" == visitEvent.cargoType)
        isValidBerth = ( "30" == visitEvent.arrivalBerth or
                         "31" == visitEvent.arrivalBerth or
                         "32" == visitEvent.arrivalBerth or
                         "33" == visitEvent.arrivalBerth )

        if isContainer and isValidBerth:
            result = True

        return result

    def serializeVisitEventToSchedule(self, S, visitEvent):
        """
        Translate the visit event to a schedule
        NB:  Some of this is a hack.  In addition, at some point 
           we want to add namespaces
        """
        time = self.getMinutesFromStartTime( visitEvent.startTime + "-0500" )
        visitDict = {}
        visitDict["arrival_node"] = "PEV"
        visitDict["departure_node"] = "PEV"
        visitDict["destination_node"] = visitEvent.arrivalBerth
        visitDict["shipment_file"] = ".".join([ visitEvent.id, "json"])
        visitDict["shipment_uuid"] = str(uuid.uuid4())
        visitDict["shipper"] = visitEvent.shippingLine
        visitDict["time"] = time
        S["shipments"].append(visitDict)
        
    def createVesselVisitEvent(self, visitEventData):
        visit = VesselVisitEvent(id = visitEventData["Visit #"],\
                                     startTime = datetime.strptime( visitEventData["Start Time"], "%m/%d/%y %H:%M" ),\
                                     endTime = datetime.strptime( visitEventData["End Time"], "%m/%d/%y %H:%M" ),\
                                     shipName = visitEventData["Ship"],\
                                     cargoType = visitEventData["Cargo Type Name"],\
                                     shippingLine = visitEventData["Visit Shipping Line Name"],\
                                     arrivalBerth = visitEventData["Arrival Berth Name"],\
                                     departureBerth = visitEventData["Departure Berth Name"],\
                                     gt = visitEventData["GT"])
        return visit
        
    def readVesselSchedule(self, vesselScheduleInputFilePath):
        vesselSchedule = []
        with open(vesselScheduleInputFilePath, 'r') as vesselScheduleInputFile:
            vesselScheduleReader = csv.DictReader(vesselScheduleInputFile)
            for vesselVisitData in vesselScheduleReader:
                visitEvent = self.createVesselVisitEvent(vesselVisitData)
                vesselSchedule.append(visitEvent)
        return vesselSchedule

    def convertToPandasDataframe(self, vesselSchedule, discretized=True):
        result = pd.DataFrame()
        
        if discretized:
            vesselScheduleData = vesselSchedule
            fields = VesselVisitEvent._fields

            for fIdx, field in enumerate(fields):
                dtype = 'int64'
                result[field] = pd.Series(list(map(lambda x: x[fIdx], vesselScheduleData))).astype(dtype)
            
        else:
            result['id'] = pd.Series(list(map(lambda x: x.id, vesselSchedule))).astype('category')
            result['startTime'] = pd.Series(list(map(lambda x: x.startTime, vesselSchedule))).astype('datetime64[ns]')
            result['endTime'] = pd.Series(list(map(lambda x: x.endTime, vesselSchedule))).astype('datetime64[ns]')
            result['shipName'] = pd.Series(list(map(lambda x: x.shipName, vesselSchedule))).astype('category')
            result['cargoType'] = pd.Series(list(map(lambda x: x.cargoType, vesselSchedule))).astype('category')
            result['shippingLine'] = pd.Series(list(map(lambda x: x.shippingLine, vesselSchedule))).astype('category')
            result['arrivalBerth'] = pd.Series(list(map(lambda x: x.arrivalBerth, vesselSchedule))).astype('category')
            result['departureBerth'] = pd.Series(list(map(lambda x: x.departureBerth, vesselSchedule))).astype('category')
            result['gt'] = pd.Series(list(map(lambda x: x.gt, vesselSchedule))).astype('float64')
        return result

    def discretize(self, vesselSchedule, timeScale="Month"):
        """
        In order to explore the data, we convert the field values into numbers
        """
        visitIds = list( set(map(lambda x: x.id, vesselSchedule)) )
        vessels = list( set(map(lambda x: x.shipName, vesselSchedule)) )
        cargoTypes = list( set(map(lambda x: x.cargoType, vesselSchedule)) )
        shipLines = list( set(map(lambda x: x.shippingLine, vesselSchedule)) )
        arrivalBerths = list( set(map(lambda x: x.arrivalBerth, vesselSchedule)) )
        departureBerths = list( set(map(lambda x: x.departureBerth, vesselSchedule)) )

        berths = list( set(arrivalBerths + departureBerths) )

        visitIds.sort()
        vessels.sort()
        cargoTypes.sort()
        shipLines.sort()
        berths.sort()

        result = []
        for vesselVisit in vesselSchedule:
            visitId = visitIds.index(vesselVisit.id)
            startTime = vesselVisit.startTime
            endTime = vesselVisit.endTime
            shipName = vessels.index(vesselVisit.shipName)
            cargoType = cargoTypes.index(vesselVisit.cargoType)
            shippingLine = shipLines.index(vesselVisit.shippingLine)
            arrivalBerth = berths.index(vesselVisit.arrivalBerth)
            departureBerth = berths.index(vesselVisit.departureBerth)
            
            result.append( [visitId, startTime, endTime, shipName, cargoType, shippingLine, arrivalBerth, departureBerth] )

        return np.asarray(result)

    def plotPCA(self, vesselScheduleData, nDimensions, colorField):
        colorFieldIdx = VesselVisitEvent._fields.index(colorField)

        pca = PCA(nDimensions)
        projected = pca.fit_transform(vesselScheduleData)
        nVals = len( set(vesselScheduleData[:, colorFieldIdx]) )
        plt.scatter(projected[:,0], projected[:,1], c=vesselScheduleData[:,colorFieldIdx], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('viridis', nVals))
        plt.colorbar()
        plt.show()

    def csv2json(self, scheduleInputFilePath, scheduleOutputFilePath):
        # Convert the CSV Vessel Schedule to a JSON Schedule
        
        S = {}
        S["shipments"] = []
        S["disruptions"] = []
        S["start_time"] = datetime.strftime(self.startTime, "%Y-%m-%d %H:%M:%S%z")
        S["workday_start"] = self.workdayStart
        S["workday_end"] = self.workdayEnd
        S["network"] = self.networkFilePath
        
        with open(scheduleInputFilePath) as scheduleInputFile:
            scheduleReader = csv.DictReader(scheduleInputFile)
            for visitEventData in scheduleReader:
                visitEvent = self.createVesselVisitEvent(visitEventData)

                if self.shouldSchedule(visitEvent):
                    self.serializeVisitEventToSchedule(S, visitEvent)
                    
        with open(scheduleOutputFilePath, 'w') as scheduleOutputFile:
            json.dump(S, scheduleOutputFile, indent=4)
            
        
