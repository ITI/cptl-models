"""
Created on February 26, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
import collections
from datetime import datetime
from sklearn.decomposition import PCA
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

TruckEvent = collections.namedtuple('TruckEvent',\
                                        'county site begDate direction type cl1 cl2 cl3 cl4 cl5 cl6 cl7 cl8 cl9 cl10 cl11 cl12 cl13 cl14 cl15 totalVolume')

# Error codes for field input
DATA_UNAVAILABLE = 0

class SensorCSVTruckScheduleDAO():
    """
    This is an interface to read in the truck sensor data
    """
    
    def createTruckEvent(self, truckScheduleData):
        truckEvent = TruckEvent( county = truckScheduleData["COUNTY"],
                                 site = int(truckScheduleData["SITE"]),
                                 begDate = datetime.strptime( truckScheduleData["BEGDATE"], \
                                                               "%m/%d/%Y" ), 
                                 direction = truckScheduleData["DIR"],
                                 type = truckScheduleData["TYPE"],
                                 cl1 = int(truckScheduleData["CL1"].replace(",", "")),
                                 cl2 = int(truckScheduleData["CL2"].replace(",", "")),
                                 cl3 = int(truckScheduleData["CL3"].replace(",", "")),
                                 cl4 = int(truckScheduleData["CL4"].replace(",", "")),
                                 cl5 = int(truckScheduleData["CL5"].replace(",", "")),
                                 cl6 = int(truckScheduleData["CL6"].replace(",", "")),
                                 cl7 = int(truckScheduleData["CL7"].replace(",", "")),
                                 cl8 = int(truckScheduleData["CL8"].replace(",", "")),
                                 cl9 = int(truckScheduleData["CL9"].replace(",", "")),
                                 cl10 = int(truckScheduleData["CL10"].replace(",", "")),
                                 cl11 = int(truckScheduleData["CL11"].replace(",", "")),
                                 cl12 = int(truckScheduleData["CL12"].replace(",", "")),
                                 cl13 = int(truckScheduleData["CL13"].replace(",", "")),
                                 cl14 = int(truckScheduleData["CL14"].replace(",", "")),
                                 cl15 = int(truckScheduleData["CL15"].replace(",", "")),
                                 totalVolume = int(truckScheduleData["TOTVOL"].replace(",","")) )
        return truckEvent

    def readTruckSchedule(self, truckScheduleInputFilePath):
        truckSchedule = []
        with open(truckScheduleInputFilePath, 'r') as truckScheduleInputFile:
            truckScheduleReader = csv.DictReader(truckScheduleInputFile)
            for truckEventData in truckScheduleReader:
                truckEvent = self.createTruckEvent(truckEventData)
                truckSchedule.append(truckEvent)
        return truckSchedule

    def convertToPandasDataframe(self, truckSchedule, discretized=True):
        result = pd.DataFrame()
        
        if discretized:
            truckScheduleData = truckSchedule
            fields = TruckEvent._fields

            dtype = 'category'
            for fIdx, field in enumerate(fields):
                if field in ["COUNTY", "SITE", "CL1", "CL2", "CL3", "CL4", "CL5", "CL6", "CL7",\
                                 "CL8", "CL9", "CL10", "CL11", "CL12", "CL13", "CL14", "CL15",\
                                 "TOTVOL"]:
                    dtype = 'int64'
                result[field] = pd.Series(list(map(lambda x: x[fIdx], truckScheduleData))).astype(dtype)                
    
        else:
            result["county"] = pd.Series(list(map(lambda x: x.county, truckSchedule))).astype('int64')
            result["site"] = pd.Series(list(map(lambda x: x.site, truckSchedule))).astype('int64')
            result["begDate"] = pd.Series(list(map(lambda x: x.begDate, truckSchedule))).astype('int64')
            result["direction"] = pd.Series(list(map(lambda x: x.direction, truckSchedule))).astype('category')
            result["type"] = pd.Series(list(map(lambda x: x.type, truckSchedule))).astype('category')
            result["cl1"] = pd.Series(list(map(lambda x: x.cl1, truckSchedule))).astype('int64')
            result["cl2"] = pd.Series(list(map(lambda x: x.cl2, truckSchedule))).astype('int64')
            result["cl3"] = pd.Series(list(map(lambda x: x.cl3, truckSchedule))).astype('int64')
            result["cl4"] = pd.Series(list(map(lambda x: x.cl4, truckSchedule))).astype('int64')
            result["cl5"] = pd.Series(list(map(lambda x: x.cl5, truckSchedule))).astype('int64')
            result["cl6"] = pd.Series(list(map(lambda x: x.cl6, truckSchedule))).astype('int64')
            result["cl7"] = pd.Series(list(map(lambda x: x.cl7, truckSchedule))).astype('int64')
            result["cl8"] = pd.Series(list(map(lambda x: x.cl8, truckSchedule))).astype('int64')
            result["cl9"] = pd.Series(list(map(lambda x: x.cl9, truckSchedule))).astype('int64')
            result["cl10"] = pd.Series(list(map(lambda x: x.cl10, truckSchedule))).astype('int64')
            result["cl11"] = pd.Series(list(map(lambda x: x.cl11, truckSchedule))).astype('int64')
            result["cl12"] = pd.Series(list(map(lambda x: x.cl12, truckSchedule))).astype('int64')
            result["cl13"] = pd.Series(list(map(lambda x: x.cl13, truckSchedule))).astype('int64')
            result["cl14"] = pd.Series(list(map(lambda x: x.cl14, truckSchedule))).astype('int64')
            result["cl15"] = pd.Series(list(map(lambda x: x.cl15, truckSchedule))).astype('int64')
            result["totalVolume"] = pd.Series(list(map(lambda x: x.totalVolume, truckSchedule))).astype('int64')
            
        return result

    def discretize(self, truckSchedule):
        """
        In order to explore the data, we convert the field values into numbers
        """
        directions = list( set(map(lambda x: x.direction, truckSchedule)) )
        types = list( set(map(lambda x: x.type, truckSchedule)) )
        
        directions.sort()
        types.sort()

        result = []
        for truckEvent in truckSchedule:
            county = truckEvent.county
            site = truckEvent.site
            begDate = truckEvent.begDate.month
            direction = directions.index(truckEvent.direction)
            type = types.index(truckEvent.type)
            cl1 = truckEvent.cl1
            cl2 = truckEvent.cl2
            cl3 = truckEvent.cl3
            cl4 = truckEvent.cl4
            cl5 = truckEvent.cl5
            cl6 = truckEvent.cl6
            cl7 = truckEvent.cl7
            cl8 = truckEvent.cl8
            cl9 = truckEvent.cl9
            cl10 = truckEvent.cl10
            cl11 = truckEvent.cl11
            cl12 = truckEvent.cl12
            cl13 = truckEvent.cl13
            cl14 = truckEvent.cl14
            cl15 = truckEvent.cl15
            totalVolume = truckEvent.totalVolume

            result.append( [county, site, begDate, direction, type, cl1, cl2, cl3,\
                                cl4, cl5, cl6, cl7, cl8, cl9, cl10, cl11, cl12,\
                                cl13, cl14, cl15, totalVolume] )
        return np.asarray(result)

    def plotPCA(self, truckScheduleData, nDimensions, colorField):
        colorFieldIdx = TruckEvent._fields.index(colorField)

        pca = PCA(nDimensions)
        projected = pca.fit_transform(truckScheduleData)
        nVals = len( set(truckScheduleData[:, colorFieldIdx]) )
        plt.scatter(projected[:,0], projected[:,1], c=truckScheduleData[:,colorFieldIdx], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('viridis', nVals))
        plt.colorbar()
        plt.show()

    

    

    
                                 
                                 
                                     
