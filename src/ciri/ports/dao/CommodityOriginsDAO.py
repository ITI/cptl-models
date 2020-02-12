"""
Created on December 17, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from datetime import datetime, timedelta
import collections
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

CommodityOrigin = collections.namedtuple('CommodityOrigin',\
                                             'direction date origin commodityGroup nTEU')

# Error codes for field input
DATA_UNAVAILABLE = 0

class CSVCommodityOriginsDAO():
    
    def createCommodityOrigin(self, commodityOriginData):
        commodityOrigin = CommodityOrigin( direction = commodityOriginData["Direction"],\
                                               date = datetime.strptime( commodityOriginData["YYYYMM"], "%Y%m" ),\
                                               origin = commodityOriginData["Foreign Initial Country"],\
                                               commodityGroup = commodityOriginData["HS Code 2 Digit"],\
                                               nTEU = commodityOriginData["TEUS"] )
        return commodityOrigin

    def readCommodityCodes(self, commodityCodeDictInputFilePath):
        commodityCodes = {}
        with open(commodityCodeDictInputFilePath, 'r') as commodityCodeDictInputFile:
            commodityCodesReader = csv.DictReader(commodityCodeDictInputFile)
            for commodityCodesData in commodityCodesReader:
                key = commodityCodesData["HS Code"]
                if '' != key:
                    key = str(int(key))
                value = commodityCodesData["Commodity Description"]
                commodityCodes[key] = value
        return commodityCodes

    def readCommodityOrigins(self, commodityOriginsInputFilePath):
        commodityOrigins = []
        with open(commodityOriginsInputFilePath, 'r') as commodityOriginsInputFile:
            commodityOriginsReader = csv.DictReader(commodityOriginsInputFile)
            for idx, commodityOriginsData in enumerate(commodityOriginsReader):
                commodityOrigin = self.createCommodityOrigin(commodityOriginsData)
                commodityOrigins.append(commodityOrigin)
        return commodityOrigins
    
    def convertToPandasDataframe(self, commodityOrigins):
        result = pd.DataFrame()
        
        result["direction"] = pd.Series(list(map(lambda x: x.direction, commodityOrigins))).astype('category')
        result["date"] = pd.Series(list(map(lambda x: x.date, commodityOrigins))).astype('datetime64[ns]')
        result["origin"] = pd.Series(list(map(lambda x: x.origin, commodityOrigins))).astype('category')
        result["commodityGroup"] = pd.Series(list(map(lambda x: x.commodityGroup, commodityOrigins))).astype('category')
        result["nTEU"] = pd.Series(list(map(lambda x: x.nTEU, commodityOrigins))).astype('float64')

        return result
    
    def computeCommodityGroupIntervals(self, odDf):
        #commoditiesODDf = odDf.groupby(['commodityGroup', 'origin'], as_index=False).agg({'nTEU':'sum'})
        commoditiesODDf = odDf.groupby(['commodityGroup', 'origin'], as_index=False).agg({'nTEU':'sum'})
        commodityGroupDf = odDf.groupby(['commodityGroup'], as_index=False).agg({'nTEU':'sum'})

        df2 = commoditiesODDf.merge(commodityGroupDf, on='commodityGroup')
        df2.columns = ['commodityGroup', 'origin', 'nTEU', 'nTEU Per Month'] #'destination' was removed
        df2['p(O|K)'] = df2['nTEU'] / df2['nTEU Per Month']
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

            endInterval = commodityEntries["p(O|K)"].cumsum()
            startInterval = pd.Series([0]).append(endInterval)
            commodityIntervals = pd.DataFrame(list(zip(origins, startInterval, endInterval))) #removed destinations
            commodityIntervals.columns = commodityIntervalColumnNames
            intervals[commodityGroup] = commodityIntervals

        self.commodityGroupIntervals = intervals

    def getOrigins(self, commodityGroup):
        """
        Given a commodity group, use a random number to select a 
          Origin-Destination pair.
        """
        n = random.random()

        commodityIntervalsDf = self.commodityGroupIntervals[commodityGroup]

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
        destination = "McIntosh Intersection" # Hardcoded
        t = ( origin, destination )
        return t
        
    def plotHelper(self, pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d} g)".format(pct, absolute)

    def plotCommodityOrigins(self, commodityCodes, commodityGroup, outFilePath):
        fig, ax = plt.subplots(figsize=(6,3), subplot_kw=dict(aspect="equal"))
        
        if commodityGroup in self.commodityGroupIntervals:
            commodityIntervalsDf = self.commodityGroupIntervals[commodityGroup]
            data = commodityIntervalsDf['end interval'] - commodityIntervalsDf['start interval']
            labels = commodityIntervalsDf['origin']

            wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: self.plotHelper(pct, data),\
                                                  textprops=dict(color="w"))
            ax.legend(wedges, labels,\
                          title="Origins",\
                          loc="center left",\
                          bbox_to_anchor=(1, 0, 0.5, 1))
            plt.setp(autotexts, size=8, weight="bold")
            commodityName = commodityCodes[commodityGroup]
            ax.set_title(f"Imported {commodityName}")
            plt.savefig(outFilePath)
        else:
            print(f"Commodity group {commodityGroup} not found, continuing")
