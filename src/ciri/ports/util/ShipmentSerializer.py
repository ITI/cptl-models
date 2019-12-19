"""
Created on March 21, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved.
"""
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
from ciri.ports.dao.VesselShipmentDAO import CSVODPairsVesselShipmentDAO, CSVVesselShipmentDAO
from jsonschema import validate
import copy
import datetime
import json
import logging
import pandas as pd
import random
import uuid

class JSONShipmentSerializer():
    
    vsDf = None     # Vessel Schedule Data Frame
    vcDf = None     # Vessel Commodities Data Frame
    odDf = None     # Commodity OD pairs data frame 
    intervals = None 
    startDate, endDate = None, None
    shipmentSchema = None
    logger = None

    @staticmethod
    def create(vesselScheduleInputFilePath,\
                   vesselCommoditiesInputFilePath,\
                   vesselODPairsInputFilePath,\
                   shipmentSchemaFilePath, startDate, endDate):
        shipmentSerializer = JSONShipmentSerializer()

        shipmentSerializer.logger = logging.getLogger('ShipmentSerializer')
        shipmentSerializer.logger.setLevel(logging.DEBUG)

        # Data Source 0:  Vessel Schedule
        vesselDAO = CSVVesselScheduleDAO()
        vesselSchedule = vesselDAO.readVesselSchedule(vesselScheduleInputFilePath)
        vesselDf = vesselDAO.convertToPandasDataframe(vesselSchedule, discretized=False)
        shipmentSerializer.logger.info("create:  VesselScheduleDAO")
        shipmentSerializer.logger.info("\t Instantiated from %s" % vesselScheduleInputFilePath)

        #-- select the date range and cargo type that we want
        date_mask2= (vesselDf['startTime'] >= startDate) & (vesselDf['startTime'] < endDate)
        container_mask = vesselDf['cargoType'] == 'CONTAINER'
        berth_mask = vesselDf['arrivalBerth'].isin(['30','31','32','33A','33B','33C'])
        monthVesselDf = vesselDf[date_mask2 & container_mask & berth_mask]
        shipmentSerializer.unmaskedVsDf = vesselDf
        shipmentSerializer.vsDf = monthVesselDf
        shipmentSerializer.logger.info("\t Filtered by date and cargo type")
        
        # Data Source 1:  Per-Vessel Commodities List
        vsDAO = CSVVesselShipmentDAO()
        vesselCommodities = vsDAO.readVesselCommodities(vesselCommoditiesInputFilePath)
        vcDf = vsDAO.convertToPandasDataframe(vesselCommodities, discretized=False)
        shipmentSerializer.vcDf = vcDf
        shipmentSerializer.logger.info("create:  VesselShipmentDAO")
        shipmentSerializer.logger.info("\t Instantiated from %s" % vesselCommoditiesInputFilePath)

        #-- select the date range and direction that we want
        import_mask = shipmentSerializer.vcDf['direction'] == 'I'
        date_mask = (vcDf['date'] >= startDate) & (vcDf['date'] < endDate)
        monthImportsDf = vcDf[date_mask & import_mask]
        shipmentSerializer.unmaskedVcDf = vcDf
        shipmentSerializer.vcDf = monthImportsDf
        shipmentSerializer.logger.info("\t Filtered by date and imports")

        # Data Source 2:  Origin-Destination Commodity Pairs
        vsODDAO = CSVODPairsVesselShipmentDAO()
        vesselCommoditiesImports = vsODDAO.readVesselCommodities(vesselODPairsInputFilePath, startDate)
        odDf = vsODDAO.convertToPandasDataframe(vesselCommoditiesImports, discretized=False)
        shipmentSerializer.logger.info("create:  ODPairsVesselShipmentDAO")
        shipmentSerializer.logger.info("\t Instantiated from %s" % vesselODPairsInputFilePath)

        #-- select the date range that we want
        #    no need to select direction as this data source is only imports
        #date_mask = (odDf['date'] >= startDate) & (odDf['date'] < endDate)
        #monthImportsODDf = odDf[date_mask]
        shipmentSerializer.odDf = odDf #monthImportsODDf
        #shipmentSerializer.logger.info("\t Filtered by date")

        # Compute the intervals for O-D pairs
        shipmentSerializer.intervals = shipmentSerializer.computeIntervals()

        # open the schema
        with open(shipmentSchemaFilePath) as shipmentSchemaFile:
            shipmentSerializer.shipmentSchema = json.load(shipmentSchemaFile)

        return shipmentSerializer


    def generateShipments(self):
        shipmentsDict = {}

        for idx, row in self.vsDf.iterrows():
            # Iterate through the vessel schedule and use this to drive
            #  shipments

            # key shipments by day and vessel name
            vesselArrivalDateTime = row['startTime']
            vesselDepartureDateTime = row['endTime']
            vesselArrivalDate = "-".join([str(vesselArrivalDateTime.year), str(vesselArrivalDateTime.month), str(vesselArrivalDateTime.day)])
            vesselDepartureDate = "-".join([str(vesselDepartureDateTime.year), str(vesselDepartureDateTime.month), str(vesselDepartureDateTime.day)])
            
            vesselName = row['shipName']
            shipmentKey = "-".join([vesselName, str(vesselArrivalDateTime), str(vesselDepartureDateTime)])
            if not shipmentKey in shipmentsDict:
                shipmentsDict[shipmentKey] = []
            
            # Now create an entry 
            commodityBundle = {}

            #-- properties based on Data Source 0:  Vessel Schedule
            eat = self.getEAT(vesselArrivalDateTime, vesselName)
            berth = self.getBerth(vesselArrivalDateTime, vesselName)
            
            if eat == None:
                self.logger.info("generateShipments:  EAT null for %s %s" % (row['date'], vesselName))
                self.logger.info("\t Continuing along")
            else:
                commodityBundle["EAT"] = eat.strftime("%Y-%m-%d %H:%M:%S%z")
                commodityBundle["LDT"] = (eat + datetime.timedelta(days=1.5)).strftime("%Y-%m-%d %H:%M:%S%z")

            if berth == None:
                self.logger.info("generateShipments:  Berth null for %s %s" % (row['date'], vesselName))
                self.logger.info("\t Continuing along")
            else:
                commodityBundle["source"] = "Berth " + berth

            commodityBundle["name"] = row["shipName"]
            
            # properties based on no data source
            commodityBundle["group_uuid"] = str(uuid.uuid4())
            commodityBundle["cargo_categories"] = ["Non-hazardous"]
            commodityBundle["delay_cost"] = None
            commodityBundle["transportation_methods"] = ["Roadway", "Sea", "Transloading"]

            # properties based on Data Source 1:  Per-Vessel Commodities
            # We have to create a bundle for each commodity group
            #  found in the query with shipment Key
            vesselCommoditiesDf = self.getVesselCommodities(vesselName, \
                                                            vesselArrivalDate,\
                                                            vesselDepartureDate)
            for idx2, row2 in vesselCommoditiesDf.iterrows():
                cb = copy.deepcopy(commodityBundle)
                commodityGroup = row2["commodityGroup"]
                cb["commodityGroup"] = commodityGroup
                cb["nTEU"] = row2["TEUs"]
    
                # properties based on Data Source 2:  Commodity Origin-Destinations
                odPair = self.getODPair2(commodityGroup)
                cb["destination"] = odPair[1]
                cb["origin"] = odPair[0]
                shipmentsDict[shipmentKey].append(cb)
        
        return shipmentsDict

    def outputShipments(self, shipmentsDict, outfilePath):
        # Make sure we are generating valid output
        for shipmentKey in shipmentsDict.keys():
            shipmentFileName = ".".join([ "shipments", shipmentKey, "json" ])
            shipmentFilePath = "/".join([outfilePath, shipmentFileName])

            commoditiesList = shipmentsDict[shipmentKey]
            vesselShipmentDict = {}
            vesselShipmentDict["commodities"] = commoditiesList

            validate(vesselShipmentDict, self.shipmentSchema)
            result = json.dumps(vesselShipmentDict, indent=4)
            with open(shipmentFilePath, 'w') as outFile:
                outFile.write(result)
            outFile.close()

    def getVesselCommodities(self, vesselName, vesselArrivalTime, vesselDepartureTime):
        vessel_mask = (self.vcDf['vesselName'] == vesselName)
        date_mask = (vesselArrivalTime <= self.vcDf['date']) & \
            (self.vcDf['date'] <= vesselDepartureTime)

        vesselCommoditiesDf = self.vcDf[vessel_mask & date_mask]
        if vesselCommoditiesDf.shape[0] == 0:
            self.logger.info("getVesselCommodities:  No entries found for %s at %s to %s" % (vesselName, vesselArrivalTime, vesselDepartureTime) )

        return vesselCommoditiesDf

    def getODPair2(self, commodityGroup):
        """
        Given a commodity group, use a random number to select a 
          Origin-Destination pair.

        In the future for more sophisticated analysis, we can 
          consider conditioning on the vessel route
        """
        n = random.random()
        commodityIntervalsDf = self.intervals[commodityGroup]

        if 0 == commodityIntervalsDf.shape[0]:
            self.logger.info("getODPair2: No OD pair found for Commodity Group %s", commodityGroup)
            self.logger.info("\t continuing by returning ('Unknown Country', 'Unknown State')")
            return ( "Unknown Country", "Unknown State")

        sinterval_mask = (n >= commodityIntervalsDf['start interval'])
        einterval_mask = (n < commodityIntervalsDf['end interval'])

        rows = commodityIntervalsDf[ sinterval_mask & einterval_mask ]
        if len(rows) != 1:
            print("Strange, should only be 1 row in result set!")
        row = rows.iloc[0]
        origin = row['origin']
        destination = row['destination']
        if "(blank" == destination:
            destination = "Unknown"
        t = ( row['origin'], row['destination'])
        return t

    def computeIntervals(self):
        #commoditiesODDf = self.odDf.groupby(['commodityGroup', 'origin', 'destination'], as_index=False).agg({'TEUs':'sum'})
        commoditiesODDf = self.odDf.groupby(['commodityGroup', 'origin'], as_index=False).agg({'TEUs':'sum'})
        commodityGroupDf = self.odDf.groupby(['commodityGroup'], as_index=False).agg({'TEUs':'sum'})

        df2 = commoditiesODDf.merge(commodityGroupDf, on='commodityGroup')
        df2.columns = ['commodityGroup', 'origin', 'TEUs', 'TEUs Per Month'] #'destination' was removed
        df2['p(OD|K)'] = df2['TEUs'] / df2['TEUs Per Month']
        # missing group by
        commodityGroups = df2['commodityGroup'].cat.categories.tolist()
        
        intervals = {}
        commodityIntervalColumnNames = ["origin", "start interval", "end interval"] #"destination" was removed
        for commodityGroup in commodityGroups:
            commodity_mask = (df2['commodityGroup'] == commodityGroup)
            commodityEntries = df2[ commodity_mask ]

            # There may not be any commodities of that type in the dataframe
            #  odDf filtered at time of 'create'
            if 0 == commodityEntries.shape[0]:
                intervals[commodityGroup] = pd.DataFrame(columns=commodityIntervalColumnNames)
                continue
        
            # otherwise
            origins = commodityEntries["origin"]
            #destinations = commodityEntries["destination"]

            endInterval = commodityEntries["p(OD|K)"].cumsum()
            startInterval = pd.Series([0]).append(endInterval)
            commodityIntervals = pd.DataFrame(list(zip(origins, startInterval, endInterval))) #removed destinations
            commodityIntervals.columns = commodityIntervalColumnNames
            intervals[commodityGroup] = commodityIntervals

        return intervals
    
    def getEAT(self, date, vesselName):
        date_mask = (pd.DatetimeIndex(self.vsDf['startTime']).day == date.day) & \
            (pd.DatetimeIndex(self.vsDf['startTime']).month == date.month) # on the day
        name_mask = (self.vsDf['shipName'] == vesselName)
        rowsDf = self.vsDf[date_mask & name_mask]

        result = None
        if rowsDf.shape[0] == 0:
            self.logger.info("getEAT:  Cannot find vessel {0} on {1}".format(vesselName, date) )
        elif rowsDf.shape[0] > 1:
            self.logger.info("getEAT:  Multiple entries for vessel " + vesselName)
        else:
            result = rowsDf['startTime'].iloc[0]
        return result

    def getBerth(self, date, vesselName):
        date_mask = (pd.DatetimeIndex(self.vsDf['startTime']).day == date.day) & \
            (pd.DatetimeIndex(self.vsDf['startTime']).month == date.month) # on the day
        name_mask = (self.vsDf['shipName'] == vesselName)
        rowsDf = self.vsDf[date_mask & name_mask]

        result = None
        if rowsDf.shape[0] == 0:
            self.logger.info("getBerth:  Cannot find vessel {0} on {1}".format(vesselName, date) )
            return
        elif rowsDf.shape[0] > 1:
            self.logger.info("getBerth:  Multiple entries for vessel " + vesselName)
            return
        else:
            result = rowsDf['arrivalBerth'].iloc[0]
        return result
        

    
