"""
Created on February 19, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
import collections
from datetime import datetime
from sklearn.decomposition import PCA
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import uuid

VesselCommodity = collections.namedtuple('VesselCommodity',\
                                             'direction date commodityGroup shipLine vesselName TEUs origin destination')

# Error codes for field input
DATA_UNAVAILABLE = 0

    
class CSVODPairsVesselShipmentDAO():

    _measurements = [ "NumberOfLoadedTEUImport/Month", "NumberOfCommodityTEUImport/Month" ]

    def createVesselCommodity(self, vesselCommodityData, commodity, monthDate):
        """
        This breaks the DAO interface but that's OK for now
        """
        vesselCommodity = VesselCommodity( direction = DATA_UNAVAILABLE,\
                                               date = datetime.strptime(monthDate, "%Y-%m-%d"),\
                                               commodityGroup = commodity,\
                                               shipLine = DATA_UNAVAILABLE,\
                                               vesselName = DATA_UNAVAILABLE,\
                                               TEUs = vesselCommodityData[commodity],\
                                               origin = vesselCommodityData["Country"],\
                                               destination = DATA_UNAVAILABLE)
        return vesselCommodity

    def readVesselCommodities(self, vesselCommoditiesInputFilePath, monthDate):
        vesselCommodities = []
        with open(vesselCommoditiesInputFilePath, 'r') as vesselCommoditiesInputFile:
            vesselCommoditiesReader = csv.DictReader(vesselCommoditiesInputFile)
            for vesselCommodityData in vesselCommoditiesReader:
                commodityGroups = list(vesselCommodityData.keys())[3:]
                for cIdx, commodity in enumerate(commodityGroups):
                    if vesselCommodityData[commodity] != "":
                        vesselCommodity = self.createVesselCommodity(vesselCommodityData, commodity, monthDate)
                        vesselCommodities.append(vesselCommodity)

        return vesselCommodities
    
    def convertToPandasDataframe(self, vesselCommodities, discretized=True):
        result = pd.DataFrame()
        
        if discretized:
            vesselCommoditiesData = vesselCommodities
            fields = VesselCommodity._fields
            
            for fIdx, field in enumerate(fields):
                if 'TEUs' == field:
                    dtype = 'float64'
                else:
                    dtype = 'int64'
                    
                result[field] = pd.Series(list(map(lambda x: x[fIdx], vesselCommoditiesData))).astype(dtype)

        else:
            result['direction'] = pd.Series(list(map(lambda x: x.direction, vesselCommodities))).astype('category')
            result['date'] = pd.Series(list(map(lambda x: x.date, vesselCommodities))).astype('datetime64[ns]')
            result['commodityGroup'] = pd.Series(list(map(lambda x: x.commodityGroup, vesselCommodities))).astype('category')
            result['shipLine'] = pd.Series(list(map(lambda x: x.shipLine, vesselCommodities))).astype('category')
            result['vesselName'] = pd.Series(list(map(lambda x: x.vesselName, vesselCommodities))).astype('category')
            result['TEUs'] = pd.Series(list(map(lambda x: pd.to_numeric(x.TEUs), vesselCommodities))).astype('float64')
            result['origin'] = pd.Series(list(map(lambda x: x.origin, vesselCommodities))).astype('category')
            result['destination'] = pd.Series(list(map(lambda x: x.destination, vesselCommodities))).astype('category')
        
        return result

    def discretize(self, vesselCommodities):
        """
        In order to explore the data, we have to convert the field values into numbers.
        """
        commodityGroups = list( set(map(lambda x: x.commodityGroup, vesselCommodities)) )
        origins = list( set(map(lambda x: x.origin, vesselCommodities)) )
        destinations = list( set(map(lambda x: x.destination, vesselCommodities)) )
        
        commodityGroups.sort()
        origins.sort()
        destinations.sort()
        
        result = []
        for vesselCommodity in vesselCommodities:
            direction = vesselCommodity.direction  # assumed to be 0 due to error codes of reading
            date = vesselCommodity.date.month 
            commodityGroup = commodityGroups.index(vesselCommodity.commodityGroup)
            shipLine = DATA_UNAVAILABLE
            vesselName = DATA_UNAVAILABLE
            TEUs = vesselCommodity.TEUs
            origin = origins.index(vesselCommodity.origin)
            destination = destinations.index(vesselCommodity.destination)
            
            result.append( [direction, date, commodityGroup, shipLine, vesselName, TEUs, origin, destination] )

        return np.asarray(result)

    def plotPCA(self, vesselCommoditiesData, nDimensions, colorField):
        colorFieldIdx = VesselCommodity._fields.index(colorField)

        #vesselCommoditiesData = self.discretize(vesselCommodities)
        pca = PCA(nDimensions)
        projected = pca.fit_transform(vesselCommoditiesData)
        nVals = len( set(vesselCommoditiesData[:,colorFieldIdx]) )
        plt.scatter(projected[:,0], projected[:,1], c=vesselCommoditiesData[:,colorFieldIdx], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('viridis', nVals))
        plt.colorbar()
        plt.show()



class CSVVesselShipmentDAO():

    """
    Class used to instantiate a vessel shipment manifest from a CSV file.
    """
    vesselDAO = None
    
    _measurements = [ "NumberOfLoadedTEUImport/Day", "VesselNames/Day", "ShippingLines/Day" ]

    def createVesselCommodity(self, vesselCommodityData):
        vesselCommodity = VesselCommodity(direction = 'I',\
                                              date = datetime.strptime( vesselCommodityData["Date"], \
                                                                            "%m/%d/%y" ),\
                                              commodityGroup = vesselCommodityData["HS Code 2 Digit"],\
                                              shipLine = vesselCommodityData["Ship Line Name"],\
                                              vesselName = vesselCommodityData["Vessel Name"],\
                                              TEUs = vesselCommodityData["TEUS"],\
                                              origin = DATA_UNAVAILABLE,\
                                              destination = DATA_UNAVAILABLE)

        return vesselCommodity


    def readVesselCommodities(self, vesselCommoditiesInputFilePath):
        vesselCommodities = []
        with open(vesselCommoditiesInputFilePath, 'r') as vesselCommoditiesInputFile:
            vesselCommoditiesReader = csv.DictReader(vesselCommoditiesInputFile)
            for vesselCommodityData in vesselCommoditiesReader:

                vesselCommodity = self.createVesselCommodity(vesselCommodityData)
                vesselCommodities.append(vesselCommodity)

        return vesselCommodities

    def convertToPandasDataframe(self, vesselCommodities, discretized=True):
        result = pd.DataFrame()
        
        if discretized:
            vesselCommoditiesData = vesselCommodities
            fields = VesselCommodity._fields
            
            for fIdx, field in enumerate(fields):
                if 'TEUs' == field:
                    dtype = 'float64'
                else:
                    dtype = 'int64'
                    
                result[field] = pd.Series(list(map(lambda x: x[fIdx], vesselCommoditiesData))).astype(dtype)

        else:
            result['direction'] = pd.Series(list(map(lambda x: x.direction, vesselCommodities))).astype('category')
            result['date'] = pd.Series(list(map(lambda x: x.date, vesselCommodities))).astype('datetime64[ns]')
            result['commodityGroup'] = pd.Series(list(map(lambda x: x.commodityGroup, vesselCommodities))).astype('category')
            result['shipLine'] = pd.Series(list(map(lambda x: x.shipLine, vesselCommodities))).astype('category')
            result['vesselName'] = pd.Series(list(map(lambda x: x.vesselName, vesselCommodities))).astype('category')
            result['TEUs'] = pd.Series(list(map(lambda x: pd.to_numeric(x.TEUs), vesselCommodities))).astype('float64')
            result['origin'] = pd.Series(list(map(lambda x: x.origin, vesselCommodities))).astype('category')
            result['destination'] = pd.Series(list(map(lambda x: x.destination, vesselCommodities))).astype('category')

        return result

    def discretize(self, vesselCommodities):
        """
        In order to explore the data, we have to convert the field values into numbers.
        """

        # Convert the categorical data to numeric, discrete by getting unique values
        #   and sorting them.  An entity's numeric value is its index within the sorted
        #   vector of possible field values.
        directions = list( set(map(lambda x: x.direction, vesselCommodities)) )
        commodityGroups = list( set(map(lambda x: x.commodityGroup, vesselCommodities)) )
        shipLines = list( set(map(lambda x: x.shipLine, vesselCommodities)) )
        vesselNames = list( set(map(lambda x: x.vesselName, vesselCommodities)) )

        directions.sort()
        commodityGroups.sort()
        shipLines.sort()
        vesselNames.sort()
        
        result = []
        for vesselCommodity in vesselCommodities:
            direction = directions.index(vesselCommodity.direction)
            # four days in a month plus the day of the week [0,6]
            date = vesselCommodity.date.month * 4 + vesselCommodity.date.weekday()
            commodityGroup = commodityGroups.index(vesselCommodity.commodityGroup)
            shipLine = shipLines.index(vesselCommodity.shipLine)
            vesselName = vesselNames.index(vesselCommodity.vesselName)
            TEUs = vesselCommodity.TEUs
            origin = vesselCommodity.origin            # assumed DATA_UNAVAILABLE 
            destination = vesselCommodity.destination  # ditto
            
            result.append( [direction, date, commodityGroup, shipLine, vesselName, TEUs, origin, destination] )
        
        return np.asarray(result)


    def plotPCA(self, vesselCommoditiesData, nDimensions, colorField):
        colorFieldIdx = VesselCommodity._fields.index(colorField)

        #vesselCommoditiesData = self.discretize(vesselCommodities)
        pca = PCA(2)
        projected = pca.fit_transform(vesselCommoditiesData)
        nVals = len( set(vesselCommoditiesData[:,colorFieldIdx]) )
        plt.scatter(projected[:,0], projected[:,1], c=vesselCommoditiesData[:,colorFieldIdx], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('viridis', nVals))
        plt.colorbar()
        plt.show()
            
    def exportVesselShipments(self, vesselCommodities):
        """
        Export per vessel shipments.  A shipment is identified by
          a vesselName at a given time.
        """
        
        shipmentDict = {}
        vcDf = self.convertToPandasDataframe(vesselCommodities, discretized=False)
        
        for vesselCommodity in vesselCommodities:
            shipmentDict[vesselName] = vesselCommodity.vesselName
            shipmentDict["core:direction"] = vesselCommodity.direction
            shipmentDict["core:date"] = datetime.strftime( vesselCommodity.date,\
                                                               "%Y-%m-%d %H:%M:%S%z")
            shipmentDict["core:commodity"] = vesselCommodity.commodityGroup
            shipmentDict["core:shipLine"] = vesselCommodity.shipLine
            
        return shipmentDict


    # Start with P(K, nTEU | t, shipper)
    #  - plot commodities by shipper
    #  
    # Also do    P(K, nTEU | t, vessel)
    #  - 

    #    P(K,nTEU | t, shipper, vessel)
    #    P(K,nTEU | t, shipper)
    #    P(K,nTEU | t, vessel)
    #    P(K,nTEU | shipper, vessel)
    #
    # 0.  Iterate through the Vessel Visit Events (named tuple?)
    # 1.  Use the Vessel Visit Event to generate a shipment based on empirical PIERS data.
    #     - Given:    arrival time and vessel name
    #     - Tell us:  (a) how many TEU to generate, (b) commodities per TEU
    # 2.  Use the PIERS data to get P(O,D |t,K).  Use this to assign a source and destination
    #     - Given:    arrival time and commodities of each TEU
    #     - Tell us:  the origin/destination pair for each TEU
    # 3.  The shipment DAO can then be used if a disruption were to occur at a given time
    #      which counties/commodities would be most affected
    #     - Allow folks to look at commodity groups (checkbox)
    #     - Outputs:  I/O Matrix (National/Regional would need RIMS)
    #                 Cholopleth (National/Regional)
    #                  https://beta.observablehq.com/@mbostock/d3-choropleth
    #                  http://mbostock.github.io/d3/talk/20111018/azimuthal.html
    #                  http://bl.ocks.org/palewire/d2906de347a160f38bc0b7ca57721328

def basicInit():
    vsDAO = CSVVesselShipmentDAO()
    vesselCommoditiesInputFilePath = "data/everglades/PEV Commods by Vessel FY2018.csv"
    vesselCommodities = vsDAO.readVesselCommodities(vesselCommoditiesInputFilePath)
    vesselCommoditiesData = vsDAO.discretize(vesselCommodities)
    return vesselCommoditiesData
