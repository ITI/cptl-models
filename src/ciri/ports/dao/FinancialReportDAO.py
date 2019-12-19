"""
Created on February 27, 2019

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

TEUReportRow = collections.namedtuple('TEUReportRow',\
                                          'direction fy empty oct nov dec jan feb mar apr may jun jul aug sep' )

class CSVTEUReportDAO():
    """
    This is an interface to read in the TEU report data
    """

    _measurements = [ "NumberOfLoadedTEUImport/Month" ]

    def createTEUReportRow(self, teuReportRowData, fiscalYear):
        reportRow = TEUReportRow( direction = teuReportRowData["DIRECTION"],
                                  fy = fiscalYear,
                                  empty = teuReportRowData["EMPTY"],
                                  oct = teuReportRowData["OCT"],
                                  nov = teuReportRowData["NOV"],
                                  dec = teuReportRowData["DEC"],
                                  jan = teuReportRowData["JAN"],
                                  feb = teuReportRowData["FEB"],
                                  mar = teuReportRowData["MAR"],
                                  apr = teuReportRowData["APR"],
                                  may = teuReportRowData["MAY"],
                                  jun = teuReportRowData["JUN"],
                                  jul = teuReportRowData["JUL"],
                                  aug = teuReportRowData["AUG"],
                                  sep = teuReportRowData["SEP"] )
        return reportRow

    def readTEUReport(self, teuReportInputFilePath, fiscalYear):
        teuReport = []
        with open(teuReportInputFilePath, 'r') as teuReportInputFile:
            teuReportReader = csv.DictReader(teuReportInputFile)
            for teuReportRowData in teuReportReader:
                reportRow = self.createTEUReportRow(teuReportRowData, fiscalYear)
                teuReport.append(reportRow)
        return teuReport

    def convertToPandasDataframe(self, teuReport, discretized=True):
        result = pd.DataFrame()
        
        if discretized:
            teuReportData = teuReport
            fields = TEUReportRow._fields

            dtype = 'category'
            for fIdx, field in enumerate(fields):
                if field in ["oct", "nov", "dec", "jan", "feb", "mar", "apr", "may",\
                                 "jun", "jul", "aug", "sep"]:
                    dtype = 'int64'
                elif field in ["fy"]:
                    dtype = 'datetime64[ns]'

                result[field] = pd.Series(list(map(lambda x: x[fIdx], teuReportData))).astype(dtype)
        else:
            result["direction"] = pd.Series(list(map(lambda x: x.direction, teuReport))).astype('category')
            result["fy"] = pd.Series(list(map(lambda x: x.fy, teuReport))).astype('datetime64[ns]')
            result["empty"] = pd.Series(list(map(lambda x: x.empty, teuReport))).astype('category')
            result["oct"] = pd.Series(list(map(lambda x: x.oct, teuReport))).astype('int64')
            result["nov"] = pd.Series(list(map(lambda x: x.nov, teuReport))).astype('int64')
            result["dec"] = pd.Series(list(map(lambda x: x.dec, teuReport))).astype('int64')
            result["jan"] = pd.Series(list(map(lambda x: x.jan, teuReport))).astype('int64')
            result["feb"] = pd.Series(list(map(lambda x: x.feb, teuReport))).astype('int64')
            result["mar"] = pd.Series(list(map(lambda x: x.mar, teuReport))).astype('int64')
            result["apr"] = pd.Series(list(map(lambda x: x.apr, teuReport))).astype('int64')
            result["may"] = pd.Series(list(map(lambda x: x.may, teuReport))).astype('int64')
            result["jun"] = pd.Series(list(map(lambda x: x.jun, teuReport))).astype('int64')
            result["jul"] = pd.Series(list(map(lambda x: x.jul, teuReport))).astype('int64')
            result["aug"] = pd.Series(list(map(lambda x: x.aug, teuReport))).astype('int64')
            result["sep"] = pd.Series(list(map(lambda x: x.sep, teuReport))).astype('int64')

        return result

    def discretize(self, teuReport):
        """
        In order to explore the data, we convert the field values into numbers
        
        """
        # sync this up with fields in TruckSchedule if we fuse!
        directions = list( set(map(lambda x: x.direction, teuReport)) )
        empties = list( set(map(lambda x: x.empty, teuReport)) )
        
        directions.sort()
        empties.sort()
              
        result = []
        
        for reportRow in teuReport:
            direction = directions.index(reportRow.direction)
            fy = reportRow.fy.year
            empty = empties.index(reportRow.empty)
            oct = reportRow.oct
            nov = reportRow.nov
            dec = reportRow.dec
            jan = reportRow.jan
            feb = reportRow.feb
            mar = reportRow.mar
            apr = reportRow.apr
            may = reportRow.may
            jun = reportRow.jun
            jul = reportRow.jul
            aug = reportRow.aug
            sep = reportRow.sep

            result.append( [direction, fy, empty, oct, nov, dec, jan, feb, mar, apr, may,\
                                jun, jul, aug, sep] )
        return np.asarray(result)

    def plotPCA(self, teuReportData, nDimensions, colorField):
        colorFieldIdx = TEUReportRow._fields.index(colorField)

        pca = PCA(nDimensions)
        projected = pca.fit_transform(truckScheduleData)
        nVals = len( set(teuReportData[:, colorFieldIdx]) )
        plt.scatter(projected[:,0], projected[:,1], c=teuReportData[:,colorFieldIdx], edgecolor='none', alpha=0.5, cmap=plt.cm.get_cmap('viridis', nVals))
        plt.colorbar()
        plt.show()


            
