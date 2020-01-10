"""
Created on December 5, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.CommodityOriginsDAO import CSVCommodityOriginsDAO
from datetime import datetime, timedelta
import copy
import csv
import json
import math
import numpy as np
import pandas as pd
import uuid

# Error codes for field input
DATA_UNAVAILABLE = 0

class VesselArrivalEvent():
    
    id = None
    shipName = None
    cargoType = None
    startDateTime = None
    endDateTime = None
    shipLine = None
    arrivalBerth = None
    gt = None
    commodityTEU = None
    
    def __init__(self, id, shipName, cargoType, startDateTime, endDateTime,\
                     shipLine, arrivalBerth, gt, commodityTEU):
        self.id = id
        self.shipName = shipName
        self.cargoType = cargoType
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
        self.shipLine = VesselArrivalEvent.normalizeShipLine(shipLine)
        self.arrivalBerth = arrivalBerth
        self.gt = gt
        self.commodityTEU = commodityTEU

    @staticmethod
    def normalizeShipLine(shipLine):
        equivalences = {"SEABOARD MARINE LTD":[],
                        "OCEAN NETWORK EXPRESS": [],
                        "CMA-CGM": ["CMA CGM"],
                        "KING OCEAN SERVICES": ["King Ocean Services Limited (Cayman Islands) Incorporated"],
                        "DOLE OCEAN CARGO EXPRESS": ["Dole Fresh Fruit International LTD."],
                        "CROWLEY LINER SERVICES": ["Crowley Liner Services, Inc."],
                        "MEDITERRANEAN SHIPPING COMPANY": ["MSC Container Mediterranean Shipping"],
                        "HAMBURG SUD": ["Hamburg-Sud"],
                        "YANG MING LINE": [],
                        "SEALAND": ["Maersk/Sealand.  (Containers)"],
                        "SEACOR ISLAND LINES LLC": ["Seacor Marine Inc."]}
        
        result = shipLine
        if shipLine in equivalences.keys():
            results = equivalences[shipLine]
            if len(results) > 0:
                result = results[0]
        return result

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        startDateTimeStr = datetime.strftime( self.startDateTime, "%m/%d/%y %H:%M" )
        endDateTimeStr = datetime.strftime( self.endDateTime, "%m/%d/%y %H:%M" )

        result = {"id": self.id, "shipName": self.shipName, "cargoType": self.cargoType,\
                      "startDateTime": startDateTimeStr, "endDateTime": endDateTimeStr,\
                      "shipLine": self.shipLine, "arrivalBerth": self.arrivalBerth,\
                      "gt": self.gt, "commodityTEU": self.commodityTEU }
        return json.dumps(result, indent=4)


class VesselArrivalEventFusionDAO():
    """
    Class used to fuse the VesselArrivals from 
      the Vessel Schedule and the Vessel Commodities
    """
    vesselArrivalEvents = None
    matchedScheduleVesselArrivalEvents = None
    matchedCommoditiesVesselArrivalEvents = None
    scheduleVesselArrivalEventDAO = None
    commoditiesVesselArrivalEventDAO = None
    commodityGroupIntervals = None
    
    def __init__(self):
        self.vesselArrivalEvents = []

    @staticmethod
    def create(vesselScheduleInputFilePath,\
                   vesselCommoditiesInputFilePath):
        vaDAO = VesselArrivalEventFusionDAO()

        vaDAO.scheduleVesselArrivalEventDAO = \
            VesselScheduleVesselArrivalEventDAO.create(vesselScheduleInputFilePath)
        vaDAO.commoditiesVesselArrivalEventDAO = \
            VesselCommoditiesVesselArrivalEventDAO.create(vesselCommoditiesInputFilePath)
        return vaDAO


    def fuseVesselArrivalEvents(self, scheduleVesselArrivalEvents, \
                                    commoditiesVesselArrivalEvents,\
                                    dayEpsilon,\
                                    fusionMethod):
                
        for va_s_idx, va_s in enumerate(scheduleVesselArrivalEvents):
            for va_c_idx, va_c in enumerate(commoditiesVesselArrivalEvents):
                
                shipNameCondition = None
                shipLineCondition = None
                dateCondition = None

                if "SHIP_LINE_DATE" == fusionMethod:
                    shipNameCondition = (va_s.shipName.replace("-", " ") == va_c.shipName.replace("-", " ").rstrip())
                    shipLineCondition = (va_s.shipLine == va_c.shipLine)
                    dateCondition = (va_s.startDateTime.date() - timedelta(days=dayEpsilon) <= va_c.startDateTime.date()) and\
                        (va_c.startDateTime.date() <= va_s.endDateTime.date() + timedelta(days=dayEpsilon))
                elif "LINE_DATE" == fusionMethod:
                    shipNameCondition = True
                    shipLineCondition = (va_s.shipLine == va_c.shipLine)
                    dateCondition = (va_s.startDateTime.date() - timedelta(days=dayEpsilon) <= va_c.startDateTime.date()) and\
                        (va_c.startDateTime.date() <= va_s.endDateTime.date() + timedelta(days=dayEpsilon))
                elif "SHIP_DATE" == fusionMethod:
                    # Use this method
                    shipNameCondition = (va_s.shipName.replace("-", " ") == va_c.shipName.replace("-", " ").rstrip())
                    shipLineCondition = True
                    dateCondition1 = (va_s.startDateTime.date() - timedelta(days=dayEpsilon) <= va_c.startDateTime.date()) and\
                        (va_c.startDateTime.date() <= va_s.endDateTime.date() + timedelta(days=dayEpsilon))
                    dateCondition2 = (va_c.startDateTime.date() - timedelta(days=dayEpsilon) <= va_s.startDateTime.date()) and\
                        (va_s.startDateTime.date() <= va_c.endDateTime.date() + timedelta(days=dayEpsilon))
                    dateCondition = dateCondition1 or dateCondition2
                else:
                    raise Exception(f"Fusion method {fusionMethod} not recognized")

                if shipNameCondition and shipLineCondition and dateCondition:
                    va = self.createFusedVesselArrivalEvent(va_s, va_c)
                    self.vesselArrivalEvents.append(va)
                    self.matchedScheduleVesselArrivalEvents[va_s_idx] = 1
                    self.matchedCommoditiesVesselArrivalEvents[va_c_idx] = 1

        return


    def getUnmatchedVesselArrivalEvents(self, dataSource):
        matchedEventIdxList = None
        dataSourceEvents = None
        if "VesselSchedule" == dataSource:
            matchedEventIdxList = self.matchedScheduleVesselArrivalEvents
            dataSourceEvents = self.scheduleVesselArrivalEventDAO.vesselArrivalEvents
        elif "Commodities" == dataSource:
            matchedEventIdxList = self.matchedCommoditiesVesselArrivalEvents
            dataSourceEvents = self.commoditiesVesselArrivalEventDAO.vesselArrivalEvents
        else:
            raise Exception(f"Unrecognized data source {dataSource}")
        
        unmatchedEventIdx = np.where(matchedEventIdxList == 0)[0]
        unmatchedEvents = [ dataSourceEvents[idx] for idx in unmatchedEventIdx ]
        return unmatchedEvents


    def createFusedVesselArrivalEvent(self, va_s, va_c):        
        id = va_s.id
        shipName = va_s.shipName
        if va_s.shipName.replace("-", " ") != va_c.shipName.replace("-", " "):
            shipName = va_s.shipName + "," + va_c.shipName
        cargoType = va_s.cargoType
        startDateTime = min(va_s.startDateTime, va_c.startDateTime)
        endDateTime = min(va_s.endDateTime, va_c.endDateTime)
        shipLine = va_s.shipLine
        arrivalBerth = va_s.arrivalBerth
        gt = va_s.gt
        commodityTEU = va_c.commodityTEU
        
        va = VesselArrivalEvent(id, shipName, cargoType, startDateTime, endDateTime, shipLine,\
                                    arrivalBerth, gt, commodityTEU)
        return va

    def getEventList(self, setName):
        eventList = None
        if "intersection" == setName:
            eventList = self.vesselArrivalEvents
        elif "unmatched_schedule" == setName:
            eventList = self.getUnmatchedVesselArrivalEvents("VesselSchedule")
        elif "unmatched_commodities" == setName:
            eventList = self.getUnmatchedVesselArrivalEvents("Commodities")
        else:
            raise Exception(f"Unrecognized setName {setName}")
        return eventList

    def convertToPandasDataframe(self, setName):
        eventList = self.getEventList(setName)
        print(f"Event List Size {setName}: {len(eventList)}")
        result = pd.DataFrame()
        result['id'] = pd.Series(list(map(lambda x: x.id, eventList))).astype('category')
        result['shipName'] = pd.Series(list(map(lambda x: x.shipName, eventList))).astype('category')
        result['cargoType'] = pd.Series(list(map(lambda x: x.cargoType, eventList))).astype('category')
        result['startDateTime'] = pd.Series(list(map(lambda x: x.startDateTime, eventList))).astype('datetime64[ns]')
        result['endDateTime'] = pd.Series(list(map(lambda x: x.endDateTime, eventList))).astype('datetime64[ns]')
        result['shipLine'] = pd.Series(list(map(lambda x: x.shipLine, eventList))).astype('category')
        result['arrivalBerth'] = pd.Series(list(map(lambda x: x.arrivalBerth, eventList))).astype('category')
        result['gt'] = pd.Series(list(map(lambda x: x.gt, eventList))).astype('float64')
        result['commodityTEU'] = pd.Series(list(map(lambda x: x.commodityTEU, eventList)))
        return result

    def getStartTime(self):
        return ""

    def getVesselSchedule(self, setName,\
                              shipmentOutfilePrefix,\
                              disruptionsList,\
                              transportationNetworkFilePath,\
                              startTime,\
                              workdayStart,\
                              workdayEnd):
        vesselScheduleDict = {}
        vesselScheduleDict["shipments"] = []
        vesselScheduleDict["disruptions"] = disruptionsList
        vesselScheduleDict["network"] = transportationNetworkFilePath
        vesselScheduleDict["start_time"] = startTime
        startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S%z")
        vesselScheduleDict["workday_end"] = workdayStart
        vesselScheduleDict["workday_start"] = workdayEnd

        vaEventList = self.getEventList(setName)
        for va in vaEventList:
            vesselArrivalDateTime = va.startDateTime
            vesselDepartureDateTime = va.endDateTime
            vesselArrivalDate = "-".join([str(vesselArrivalDateTime.year), str(vesselArrivalDateTime.day)])
            vesselDepartureDate = "-".join([str(vesselDepartureDateTime.year), str(vesselDepartureDateTime.day)])

            vesselArrivalEvent = {}
            vesselArrivalEvent["arrival_node"] = "PEV"
            vesselArrivalEvent["departure_node"] = "PEV"
            berthNum = str(va.arrivalBerth)
            vesselArrivalEvent["destination_node"] = "Berth " + self.normalizeBerth(berthNum)
            day = vesselArrivalDateTime.day
            vesselName = va.shipName
            shipmentKey = "-".join([vesselName, str(vesselArrivalDateTime), str(vesselDepartureDateTime)])
            shipmentFileName = ".".join([shipmentKey, "json" ])
            shipmentFilePath = "/".join([shipmentOutfilePrefix, shipmentFileName])
            vesselArrivalEvent["shipment_file"] = shipmentFilePath
            vesselArrivalEvent["shipment_uuid"] = str(uuid.uuid4())
            vesselArrivalEvent["shipper"] = self.normalizeShipLine(va.shipLine, berthNum)
            vesselArrivalEvent["time"] = self.getMinutesFromStartTime(va.startDateTime, startTime)
            if vesselArrivalEvent["time"] < 0:
                print(shipmentFilePath)
                print(f"Likely on a month border, start at start of month:  {va.startDateTime}, {startTime}")

            vesselScheduleDict["shipments"].append(vesselArrivalEvent)
        return vesselScheduleDict
    
    def getMinutesFromStartTime(self, timestamp, simStartTime):
        """
        Get the number of minutes from the origin time
        """
        result = int( ( timestamp - simStartTime).total_seconds() / 60 )
        if result < 0:
            result = 0
        return result

    def normalizeShipLine(self, shipLine, berthNum):
        result = shipLine
        if "Crowley" in shipLine:
            result = "Crowley"
        elif "King Ocean" in shipLine:
            result = "King Ocean"
        elif "MSC" in shipLine:
            result = "MSC"
        elif "33" in berthNum:
            # Ugly hack assumption
            result = "FIT"

        return result

    def normalizeBerth(self, berthNum):
        result = berthNum
        berthConditions = ("33A" == berthNum) or\
            ("33B" == berthNum) or ("33C" == berthNum)
        if berthConditions:
            result = "33"
        return result

    def getVesselShipments(self, setName, startTime, commodityOriginsDAO):
        shipmentsDict = {}
        startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S%z")

        vaEventList = self.getEventList(setName)
        for va_idx, va in enumerate(vaEventList):
            # Iterate through the vessel arrivals and use this to drive shipments
            
            # key shipments by day and vessel name
            vesselArrivalDateTime = va.startDateTime
            vesselDepartureDateTime = va.endDateTime
            vesselArrivalDate = "-".join([str(vesselArrivalDateTime.year), str(vesselArrivalDateTime.month), str(vesselArrivalDateTime.day)])
            vesselDepartureDate = "-".join([str(vesselDepartureDateTime.year), str(vesselDepartureDateTime.month), str(vesselDepartureDateTime.day)])
            
            vesselName = va.shipName
            shipmentKey = "-".join([vesselName, str(vesselArrivalDateTime), str(vesselDepartureDateTime)])
            if not shipmentKey in shipmentsDict:
                shipmentsDict[shipmentKey] = []
            
            # Now create an entry 
            commodityBundle = {}
            
            eat = va.startDateTime
            berthNum = str(va.arrivalBerth)
            
            commodityBundle["EAT"] = self.getMinutesFromStartTime(eat, startTime)
            ldt = eat + timedelta(days=5)
            commodityBundle["LDT"] = self.getMinutesFromStartTime(ldt, startTime)
            commodityBundle["cargo_categories"] = ["Non-hazardous"]            
            commodityBundle["delay_cost"] = None
            commodityBundle["group_uuid"] = str(uuid.uuid4())
            commodityBundle["source"] = "Berth " + self.normalizeBerth(berthNum)
            commodityBundle["transportation_methods"] = ["Roadway", "Sea", "Transloading"]

            # Iterate through each of the commodities and generate a bundle
            for cg_idx, commodityGroup in enumerate(va.commodityTEU.keys()):
                cb = copy.deepcopy(commodityBundle)

                direction = va.commodityTEU[commodityGroup][0]
                shipLine = va.commodityTEU[commodityGroup][1]
                nTEU = float(va.commodityTEU[commodityGroup][2])

                #cb["commodityGroup"] = commodityGroup
                cb["shipper"] = self.normalizeShipLine(shipLine, berthNum)
                cb["nTEU"] = nTEU
                (origin, destination) = commodityOriginsDAO.getOrigins(commodityGroup)
                cb["origin"] = origin
                cb["destination"] = destination
                cb["name"] = f"{va_idx}-{vesselName}-{cg_idx}:{commodityGroup}:{origin}"
                shipmentsDict[shipmentKey].append(cb)
        return shipmentsDict
        

class VesselCommoditiesVesselArrivalEventDAO():
    """
    Class used to instantiate a sequence of vessel arrival events from PIERS data
    """
    vesselArrivalEvents = None

    def __init__(self):
        self.vesselArrivalEvents = []

    @staticmethod
    def isKnownArrival(knownVesselArrivalEvent, newVesselArrivalEvent):

        result = False
        if knownVesselArrivalEvent != None and\
                knownVesselArrivalEvent.startDateTime <= newVesselArrivalEvent.startDateTime and \
                newVesselArrivalEvent.startDateTime <= (knownVesselArrivalEvent.endDateTime + timedelta(days=1)) and \
                newVesselArrivalEvent.shipName == knownVesselArrivalEvent.shipName:
            # Ship line is not part of this as a vessel arrival may serve multiple 
            #   ship lines
            result = True
        return result

    @staticmethod
    def create(vesselCommoditiesInputFilePath):
        vaDAO = VesselCommoditiesVesselArrivalEventDAO()
        with open(vesselCommoditiesInputFilePath, 'r') as vesselCommoditiesInputFile:
            vesselCommoditiesReader = csv.DictReader(vesselCommoditiesInputFile)
            vesselArrivalEvent = None
            for vesselCommoditiesData in vesselCommoditiesReader:
                vesselArrivalEvent = VesselCommoditiesVesselArrivalEventDAO.createVesselArrivalEvent(vesselCommoditiesData)
                knownVesselArrivals = [ (idx, va) for idx, va in enumerate(vaDAO.vesselArrivalEvents) if VesselCommoditiesVesselArrivalEventDAO.isKnownArrival(va, vesselArrivalEvent) ]
                
                shipLine = VesselArrivalEvent.normalizeShipLine( vesselCommoditiesData["Ship Line Name"] )
                dateTime = datetime.strptime( vesselCommoditiesData["Date"] + " 00:00:00-0400", "%m/%d/%y %H:%M:%S%z" )
                commodityGroup = vesselCommoditiesData["HS Code 2 Digit"]
                direction = vesselCommoditiesData["Direction"]
                TEUs = vesselCommoditiesData["TEUS"]

                if len(knownVesselArrivals) == 1:
                    # known arrival
                    eventIdx = knownVesselArrivals[0][0]
                    vesselArrivalEvent = knownVesselArrivals[0][1]
                    if dateTime > vesselArrivalEvent.endDateTime:
                        vesselArrivalEvent.endDateTime = dateTime
                    vesselArrivalEvent.commodityTEU[commodityGroup] = (direction, shipLine, TEUs)
                    vaDAO.vesselArrivalEvents[eventIdx] = vesselArrivalEvent
                        
                elif len(knownVesselArrivals) > 1:
                    print("Unusual, expected one match")
                    for va in knownVesselArrivals:
                        print(va)
                else:
                    # new arrival
                    vesselArrivalEvent.commodityTEU[commodityGroup] = (direction, shipLine, TEUs)
                    vaDAO.vesselArrivalEvents.append(vesselArrivalEvent)

        vesselCommoditiesInputFile.close()
        return vaDAO

    @staticmethod
    def createVesselArrivalEvent(vesselCommoditiesData):
        # create a vessel arrival event 
        id = DATA_UNAVAILABLE
        shipName = vesselCommoditiesData["Vessel Name"]
        cargoType = "CONTAINER"
        startDateTime = datetime.strptime( vesselCommoditiesData["Date"] + " 00:00:00-0400", "%m/%d/%y %H:%M:%S%z" )
        endDateTime = startDateTime
        shipLine = DATA_UNAVAILABLE #None #vesselCommoditiesData["Ship Line Name"]
        arrivalBerth = DATA_UNAVAILABLE
        gt = DATA_UNAVAILABLE

        commodityGroup = vesselCommoditiesData["HS Code 2 Digit"]
        direction = vesselCommoditiesData["Direction"]
        TEUs = vesselCommoditiesData["TEUS"]
        commodityTEU = { commodityGroup: (direction, shipLine, TEUs)}
        
        va = VesselArrivalEvent( id, shipName, cargoType, startDateTime, endDateTime, shipLine,\
                                     arrivalBerth, gt, commodityTEU )
        return va

    def convertToPandasDataframe(self):
        result = pd.DataFrame()

        result['id'] = pd.Series(list(map(lambda x: x.id, self.vesselArrivalEvents))).astype('category')
        result['shipName'] = pd.Series(list(map(lambda x: x.shipName, self.vesselArrivalEvents))).astype('category')
        result['cargoType'] = pd.Series(list(map(lambda x: x.cargoType, self.vesselArrivalEvents))).astype('category')
        result['startDateTime'] = pd.Series(list(map(lambda x: x.startDateTime, self.vesselArrivalEvents))).astype('datetime64[ns]')
        result['endDateTime'] = pd.Series(list(map(lambda x: x.endDateTime, self.vesselArrivalEvents))).astype('datetime64[ns]')
        result['shipLine'] = pd.Series(list(map(lambda x: x.shipLine, self.vesselArrivalEvents))).astype('category')
        result['arrivalBerth'] = pd.Series(list(map(lambda x: x.arrivalBerth, self.vesselArrivalEvents))).astype('category')
        result['gt'] = pd.Series(list(map(lambda x: x.gt, self.vesselArrivalEvents))).astype('float64')
        result['commodityTEU'] = pd.Series(list(map(lambda x: x.commodityTEU, self.vesselArrivalEvents)))
        return result

class VesselScheduleVesselArrivalEventDAO():
    
    """
    Class used to instantiate a sequence of vessel arrival events from a schedule
    """
    vesselArrivalEvents = None

    def __init__(self):
        self.vesselArrivalEvents = []

    @staticmethod
    def create(vesselScheduleInputFilePath):
        
        vaDAO = VesselScheduleVesselArrivalEventDAO()
        with open(vesselScheduleInputFilePath, 'r') as vesselScheduleInputFile:
            vesselScheduleReader = csv.DictReader(vesselScheduleInputFile)
            for vesselArrivalData in vesselScheduleReader:
                vesselArrivalEvent = VesselScheduleVesselArrivalEventDAO.createVesselArrivalEvent(vesselArrivalData)
                vaDAO.vesselArrivalEvents.append(vesselArrivalEvent)
        vesselScheduleInputFile.close()
        return vaDAO

    @staticmethod
    def createVesselArrivalEvent(vesselArrivalData):
        id = vesselArrivalData["Visit #"]
        shipName = vesselArrivalData["Ship"]
        cargoType = vesselArrivalData["Cargo Type Name"]
        startDateTime = datetime.strptime( vesselArrivalData["Start Time"] + "-0400", "%m/%d/%y %H:%M%z" )
        endDateTime = datetime.strptime( vesselArrivalData["End Time"] + "-0400", "%m/%d/%y %H:%M%z" )
        shipLine = vesselArrivalData["Visit Shipping Line Name"]
        arrivalBerth = vesselArrivalData["Arrival Berth Name"]
        gt = vesselArrivalData["GT"]
        commodityTEU = {}

        va = VesselArrivalEvent( id, shipName, cargoType, startDateTime, endDateTime, shipLine,\
                                     arrivalBerth, gt, commodityTEU)
        return va

    
    def convertToPandasDataframe(self):
        result = pd.DataFrame()

        result['id'] = pd.Series(list(map(lambda x: x.id, self.vesselArrivalEvents))).astype('category')
        result['shipName'] = pd.Series(list(map(lambda x: x.shipName, self.vesselArrivalEvents))).astype('category')
        result['cargoType'] = pd.Series(list(map(lambda x: x.cargoType, self.vesselArrivalEvents))).astype('category')
        result['startDateTime'] = pd.Series(list(map(lambda x: x.startDateTime, self.vesselArrivalEvents))).astype('datetime64[ns]')
        result['endDateTime'] = pd.Series(list(map(lambda x: x.endDateTime, self.vesselArrivalEvents))).astype('datetime64[ns]')
        result['shipLine'] = pd.Series(list(map(lambda x: x.shipLine, self.vesselArrivalEvents))).astype('category')
        result['arrivalBerth'] = pd.Series(list(map(lambda x: x.arrivalBerth, self.vesselArrivalEvents))).astype('category')
        result['gt'] = pd.Series(list(map(lambda x: x.gt, self.vesselArrivalEvents))).astype('float64')
        result['commodityTEU'] = pd.Series(list(map(lambda x: x.commodityTEU, self.vesselArrivalEvents)))
        return result

    
