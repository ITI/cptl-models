"""
Created on April 2020

@author:  Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana Champaign.
All rights reserved.
"""
import json
import numpy as np
import pandas as pd
import pint
import re
import sqlite3

class CoreCalibrationReporter():

    scenarioDir = None
    configDir = None
    dataSourceDict = None
    dataFramesDict = None
    unitRegistry = None
    month = None
    measurementUrns = ["urn:cite:PDT:NumberOfVessels",\
                       "urn:cite:PDT:NumberOfTEU",\
                       "urn:cite:PDT:VesselDwellTime",\
                       "urn:cite:PDT:TEUTransitTime"]
    
    @staticmethod
    def create(scenarioDir, configDir, dataSourceDict, month, simDuration):
        ccReporter = CoreCalibrationReporter()
        ccReporter.scenarioDir = scenarioDir
        ccReporter.configDir = configDir
        ccReporter.dataSourceDict = dataSourceDict
        ccReporter.month = month
        
        # Initialize Unit Registry
        unitDefsFilePath = "/".join([configDir, "pdt_units.txt"])
        ccReporter.unitRegistry = pint.UnitRegistry()
        ccReporter.unitRegistry.load_definitions(unitDefsFilePath)
        ccReporter.simDuration =\
            ccReporter.unitRegistry.Quantity(simDuration, 'day')
        return ccReporter

    # MEASUREMENTS
    def getMeasurement(self, measurementUrn):
        result = None
        if "urn:cite:PDT:NumberOfVessels" == measurementUrn:
            result = self.getNumberOfVessels()
        elif "urn:cite:PDT:NumberOfTEU" == measurementUrn:
            result = self.getNumberOfTEU()
        elif "urn:cite:PDT:VesselDwellTime" == measurementUrn:
            result = self.getVesselDwellTimes()
        elif "urn:cite:PDT:TEUTransitTime" == measurementUrn:
            result = self.getTEUTransitTimes()
        return result

    def getNumberOfVessels(self):
        measurementUrn = "urn:cite:PDT:NumberOfVessels"
        dataSourceUrns = self.dataSourceDict.keys()
  
        nVesselsDf = pd.DataFrame(columns = ["Value", "Data Source", "Ref"])

        #-- Data Source 1:  VesselCalls
        vesselCallUrns = list(filter(lambda x: "VesselCalls" in x, dataSourceUrns))        
        for vesselCallUrn in vesselCallUrns:
            vesselCallEdition = vesselCallUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, vesselCallEdition])
            vesselCallsDf = self.dataFramesDict[vesselCallUrn]
            numVesselCalls = vesselCallsDf.shape[0]
            numVesselCalls = self.unitRegistry.Quantity(numVesselCalls, 'vsl')
            nVesselsDf = nVesselsDf.append({"Value": numVesselCalls,\
                                            "Data Source": vesselCallUrn,\
                                            "Ref": measurementEditionUrn},\
                                           ignore_index=True)

        #-- Data Source 2:  DESInputSchedule
        vesselScheduleUrns = list(filter(lambda x: "DESInputSchedule" in x, dataSourceUrns))
        for vesselScheduleUrn in vesselScheduleUrns:
            vesselScheduleEdition = vesselScheduleUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, vesselScheduleEdition])
            vesselScheduleJSON = self.dataFramesDict[vesselScheduleUrn]
            numVesselCalls = len(vesselScheduleJSON["shipments"])
            numVesselCalls = self.unitRegistry.Quantity(numVesselCalls, 'vsl')
            nVesselsDf = nVesselsDf.append({"Value": numVesselCalls,\
                                            "Data Source": vesselScheduleUrn,\
                                            "Ref": measurementEditionUrn},\
                                           ignore_index=True)

        #-- Data Source 3:  DESOutputDB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            vesselsArrivedDf = self.selectAllVessels(outputDbUrn)
            vesselsArrived = vesselsArrivedDf.shape[0]
            numVesselsArrived = self.unitRegistry.Quantity(vesselsArrived, 'vsl')
            nVesselsDf = nVesselsDf.append({"Value": numVesselsArrived,\
                                            "Data Source": outputDbUrn,\
                                            "Ref": measurementEditionUrn},\
                                           ignore_index=True)
        return nVesselsDf

    def getNumberOfTEU(self):
        measurementUrn = "urn:cite:PDT:NumberOfTEU"
        dataSourceUrns = self.dataSourceDict.keys()

        nTEUDf = pd.DataFrame(columns = ["Value", "Data Source", "Ref"])

        #-- Data Source 1:  ImportedCommods
        importedCommodsUrns = list(filter(lambda x: "ImportedCommods" in x, dataSourceUrns))
        for importedCommodsUrn in importedCommodsUrns:
            importedCommodsEdition = importedCommodsUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, importedCommodsEdition])
            importedCommodsDf = self.dataFramesDict[importedCommodsUrn]
            importedCommodsDf["TEU_CEIL"] =\
                importedCommodsDf["TEUS"].apply(np.ceil)
            numTEUInImportedCommods = int(importedCommodsDf["TEU_CEIL"].sum())
            numTEUInImportedCommods =\
                self.unitRegistry.Quantity(numTEUInImportedCommods, 'TEU')
            nTEUDf = nTEUDf.append({"Value": numTEUInImportedCommods,\
                                    "Data Source": importedCommodsUrn,\
                                    "Ref": measurementEditionUrn},\
                                   ignore_index=True)

        #-- Data Source 2:  TEUReport
        teuReportUrns = list(filter(lambda x: "TEUReport" in x, dataSourceUrns))
        for teuReportUrn in teuReportUrns:
            teuReportEdition = teuReportUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, teuReportEdition])
            teuReportDf = self.dataFramesDict[teuReportUrn]
            monthColName = self.getMonth()
            numTEUInTEUReport = int(teuReportDf[monthColName])
            numTEUInTEUReport =\
                self.unitRegistry.Quantity(numTEUInTEUReport, 'TEU/month')
            nTEUDf = nTEUDf.append({"Value": numTEUInTEUReport,\
                                    "Data Source": teuReportUrn,\
                                    "Ref": measurementEditionUrn},\
                                   ignore_index=True)
            
        #-- Data Source 3:  DESOutputDB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            teuInSimulationDf = self.selectAllTEU(outputDbUrn)
            numTEUInSimulation = teuInSimulationDf.shape[0]
            numTEUInSimulation = self.unitRegistry.Quantity(numTEUInSimulation, 'TEU')
            nTEUDf = nTEUDf.append({"Value": numTEUInSimulation,\
                                    "Data Source": outputDbUrn,\
                                    "Ref": measurementEditionUrn},\
                                   ignore_index=True)
        return nTEUDf

    def getVesselDwellTimes(self):
        measurementUrn = "urn:cite:PDT:VesselDwellTime"
        dataSourceUrns = self.dataSourceDict.keys()

        vesselCallDurationsDf = pd.DataFrame(columns = ["min", "max", "mean", "Data Source", "Ref"])

        #-- Data Source 1:  VesselCalls
        vesselCallUrns = list(filter(lambda x: "VesselCalls" in x, dataSourceUrns))
        for vesselCallUrn in vesselCallUrns:
            vesselCallEdition = vesselCallUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, vesselCallEdition])
            vesselCallsDf = self.dataFramesDict[vesselCallUrn]
            vesselCallsDf["Duration"] =\
                vesselCallsDf["Length Of Stay"].map(lambda x: self.getMinutes(x).magnitude)
            minDuration = np.round(vesselCallsDf["Duration"].min())
            minDuration = self.unitRegistry.Quantity(minDuration, 'min')
            maxDuration = np.round(vesselCallsDf["Duration"].max())
            maxDuration = self.unitRegistry.Quantity(maxDuration, 'min')
            meanDuration = np.round(vesselCallsDf["Duration"].mean())
            meanDuration = self.unitRegistry.Quantity(meanDuration, 'min')
            
            vesselCallDurationsDf =\
                vesselCallDurationsDf.append({"min": minDuration,\
                                              "max": maxDuration,\
                                              "mean": meanDuration,\
                                              "Data Source": vesselCallUrn,\
                                              "Ref": measurementEditionUrn},\
                                             ignore_index=True)
        #-- Data Source 2:  DESOutputDB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            vesselsArrivedDf = self.selectAllVessels(outputDbUrn)
            vesselCallsDf = self.getVesselDurationsFromDESOutputDB(vesselsArrivedDf)
            minDuration = np.round(vesselCallsDf["DurationAtBerth"].min())
            minDuration = self.unitRegistry.Quantity(minDuration, 'min')
            maxDuration = np.round(vesselCallsDf["DurationAtBerth"].max())
            maxDuration = self.unitRegistry.Quantity(maxDuration, 'min')
            meanDuration = np.round(vesselCallsDf["DurationAtBerth"].mean())
            meanDuration = self.unitRegistry.Quantity(meanDuration, 'min')

            vesselCallDurationsDf =\
                vesselCallDurationsDf.append({"min": minDuration,\
                                              "max": maxDuration,\
                                              "mean": meanDuration,\
                                              "Data Source": outputDbUrn,\
                                              "Ref": measurementEditionUrn},\
                                             ignore_index=True)            
        return vesselCallDurationsDf

    def getVesselDurationsFromDESOutputDB(self, vesselsArrivedDf):

        vesselDurationsDf = \
            pd.DataFrame(columns = ["DurationInPEV", "DurationAtBerth"])

        for index, row in vesselsArrivedDf.iterrows():
            vesselArrivalEvent = row
            vesselKey = vesselArrivalEvent["Commodity Name"]
            vesselDurationInPEV = \
                vesselArrivalEvent["End Time"] - vesselArrivalEvent["Start Time"]
            vesselDurationInPEV = self.unitRegistry.Quantity(vesselDurationInPEV, 'min')
            vesselDurationAtBerth = self.getVesselDurationAtBerth(vesselArrivalEvent)
            vesselDurationAtBerth = self.unitRegistry.Quantity(vesselDurationAtBerth, 'min')
            
            vesselDurationsDf =\
                vesselDurationsDf.append({"DurationInPEV": vesselDurationInPEV.magnitude,\
                                          "DurationAtBerth": vesselDurationAtBerth.magnitude},\
                                         ignore_index=True)
        return vesselDurationsDf

    def getVesselDurationAtBerth(self, vesselArrivalEvent):
        vesselPath = vesselArrivalEvent["Path Traveled"]
        vesselPathTimes = vesselArrivalEvent["Times"].split(",")
        vesselPathTimes = list(map(lambda x: float(x), vesselPathTimes))
        pathElements = vesselPath.split(",")

        berthList = ["Berth 30", "Berth 31", "Berth 32", "Berth 33"]

        berthIdx = -1
        for berth in berthList:
            berthIdx = pathElements.index(berth) if berth in pathElements else -1
            if -1 != berthIdx:
                break

        result = -1
        if -1 == berthIdx:
            print(f"Berth not found in path {vesselsArrived}")
        else:
            # Assuming that the times are arrival times at nodes
            result = vesselPathTimes[berthIdx + 1] - vesselPathTimes[berthIdx]

        return result
    
    def getMinutes(self, durationStr):
        result = 0
        resultStr = [durationStr]
        if "h" in durationStr:
            hourPat = re.compile("(\d){1,2}h")
            match = hourPat.search(durationStr)
            result += int(match[0].replace("h","")) * 60
            resultStr.append(match[0].replace("h",""))
        if "d" in durationStr:
            dayPat = re.compile("(\d){1,2}d")
            match = dayPat.search(durationStr)
            result += int(match[0].replace("d","")) * 24 * 60
            resultStr.append(match[0].replace("d",""))

        result = self.unitRegistry.Quantity(int(result), 'min')
        return result

    def getTEUTransitTimes(self):
        measurementUrn = "urn:cite:PDT:TEUTransitTime"
        dataSourceUrns = self.dataSourceDict.keys()

        teuTransitTimesDf = pd.DataFrame(columns = ["min","max", "mean", "Data Source", "Ref"])

        #-- Data Source 1:  DESOutputDB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            teuInSimulation = self.selectAllTEU(outputDbUrn)
            teuDurationsInSimulation = teuInSimulation.apply(lambda x: self.getDuration(x), axis=1)

            minDuration = np.round(teuDurationsInSimulation.min())
            minDuration = self.unitRegistry.Quantity(minDuration, 'min')
            maxDuration = np.round(teuDurationsInSimulation.max())
            maxDuration = self.unitRegistry.Quantity(maxDuration, 'min')
            
            meanDuration = np.round(teuDurationsInSimulation.mean())
            meanDuration = self.unitRegistry.Quantity(meanDuration, 'min')
            teuTransitTimesDf =\
                teuTransitTimesDf.append({"min": minDuration,\
                                          "max": maxDuration,\
                                          "mean": meanDuration,\
                                          "Data Source": outputDbUrn,\
                                          "Ref": measurementEditionUrn},\
                                         ignore_index=True)            
        return teuTransitTimesDf

    def getDuration(self, x):
        oIdx, dIdx = self.getOriginDestIdx(x["Path Traveled"])
        sTime, eTime = self.getStartEndTime(oIdx, dIdx, x["Times"])
        duration = eTime - sTime
        return duration

    def getOriginDestIdx(self, pathStr):
        pathList = pathStr.split(",")
        berthList = ["Berth 30", "Berth 31", "Berth 32", "Berth 33"]
        oIdx = -1

        for originName in berthList:
            if originName in pathList:
                oIdx = pathList.index(originName)
                break

        dIdx = -1
        destName= "McIntosh Intersection"
        if destName in pathList:
            dIdx = pathList.index(destName)
        return oIdx, dIdx

    def getStartEndTime(self, oIdx, dIdx, timesStr):
        timesList = list(map(lambda x: float(x), timesStr.split(",")))
        sTime = timesList[oIdx]
        eTime = timesList[dIdx]
        return sTime, eTime
    
    # DATA SOURCES
    def loadDataSources(self):
        # Load data sources into data frames
        self.dataFramesDict = {}
        for dataSourceUrn in self.dataSourceDict.keys():
            if "VesselCalls" in dataSourceUrn:
                self.loadVesselCalls(dataSourceUrn)
            elif "TEUReport" in dataSourceUrn:
                self.loadTEUReport(dataSourceUrn)
            elif "ImportedCommods" in dataSourceUrn:
                self.loadImportedCommods(dataSourceUrn)
            elif "DESInputSchedule" in dataSourceUrn:
                self.loadDESInputSchedule(dataSourceUrn)
            elif "DESOutputDB" in dataSourceUrn:
                self.loadDESOutputDB(dataSourceUrn)
        return

    def loadVesselCalls(self, dataSourceUrn):
        vesselCallsDf = pd.read_csv( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        vesselCallsDf["Start Time"] = vesselCallsDf["Start Time"].astype('datetime64[ns]')
        vesselCallsDf["End Time"] = vesselCallsDf["End Time"].astype('datetime64[ns]')

        nDays = self.simDuration
        dayMask = vesselCallsDf["Start Time"].map(lambda x: x.day <= nDays.magnitude)
        vesselCallsDf = vesselCallsDf[ dayMask ]

        berths = ['30', '31', '32', '33A', '33B', '33C']
        berthMask = vesselCallsDf["Arrival Berth Name"].map(lambda x: x in berths)
        vesselCallsDf = vesselCallsDf[ berthMask ]
        self.dataFramesDict[dataSourceUrn] = vesselCallsDf

    def getMonth(self):
        monthList = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",\
                     "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        monthStr = monthList[ self.month - 1 ]
        return monthStr
    
    def loadTEUReport(self, dataSourceUrn):
        teuReportDf = pd.read_csv( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        monthColName = self.getMonth()

        imports_mask = teuReportDf["DIRECTION"] == "Inbound"
        loaded_mask = teuReportDf["EMPTY"] == "Loaded"
        teuReportDf = teuReportDf[ imports_mask ]
        teuReportDf = teuReportDf[ loaded_mask ]
        self.dataFramesDict[dataSourceUrn] = teuReportDf

    def loadImportedCommods(self, dataSourceUrn):
        importedCommodsDf = pd.read_csv( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        importedCommodsDf = importedCommodsDf.fillna(0)
        importedCommodsDf = \
            importedCommodsDf.astype({"HS Code 2 Digit": 'int32'})
        
        importedCommodsDf["day"] = pd.DatetimeIndex(importedCommodsDf["Date"]).day
        nDays = self.simDuration        
        day_mask = importedCommodsDf["day"] <= nDays.magnitude
        importedCommodsDf = importedCommodsDf[day_mask]
        self.dataFramesDict[dataSourceUrn] = importedCommodsDf

    def loadDESInputSchedule(self, dataSourceUrn):
        vesselSchedule = {}
        with open( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]), 'r') as vesselScheduleFile:
            vesselSchedule = json.load(vesselScheduleFile)
        self.dataFramesDict[dataSourceUrn] = vesselSchedule

    def loadDESOutputDB(self, dataSourceUrn):
        conn = self.createConnection( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        self.dataFramesDict[dataSourceUrn] = conn

    # Utility function for DB queries
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def createConnection(self, dbPath):
        """
        create a database connection to the SQLite database
        specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(dbPath)
            conn.row_factory = self.dict_factory
        except sqlite3.Error as e:
            print(e)

        return conn
        
    def selectAllVessels(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT * FROM output WHERE \"Transport Unit\"='Ship'"
        df = pd.read_sql_query(query, conn)
        return df

    def selectAllTEU(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT \"Commodity Name\", \"Path Traveled\", Times FROM output WHERE \"Transport Unit\" = 'Container'"
        df = pd.read_sql_query(query, conn)
        return df

class EconomicCalibrationReporter(CoreCalibrationReporter):

    scenarioDir = None
    configDir = None
    dataSourceDict = None
    dataFramesDict = None
    unitRegistry = None
    month = None
    measurementUrns = ["urn:cite:PDT_Econ:NumberOfCountries",\
                       "urn:cite:PDT_Econ:NumberOfHS2Codes",\
                       "urn:cite:PDT_Econ:PercentTEUPerHS2Code",\
                       "urn:cite:PDT_Econ:PercentTEUPerCountry",\
                       "urn:cite:PDT_Econ:NumberCountriesPerHS2Code",\
                       "urn:cite:PDT_Econ:PercentTEUPerHS2Code,Country"]

    @staticmethod
    def create(scenarioDir, configDir, dataSourceDict, month, simDuration):
        ecReporter = EconomicCalibrationReporter()
        ecReporter.scenarioDir = scenarioDir
        ecReporter.configDir = configDir
        ecReporter.dataSourceDict = dataSourceDict
        ecReporter.month = month

        # Initialize Unit Registry
        unitDefsFilePath = "/".join([configDir, "pdt_units.txt"])
        ecReporter.unitRegistry = pint.UnitRegistry()
        ecReporter.unitRegistry.load_definitions(unitDefsFilePath)
        ecReporter.simDuration =\
            ecReporter.unitRegistry.Quantity(simDuration, 'day')
        return ecReporter

    # DATA SOURCES
    def loadDataSources(self):
        # Load data sources into data frames
        self.dataFramesDict = {}
        for dataSourceUrn in self.dataSourceDict.keys():
            if "VesselCalls" in dataSourceUrn:
                self.loadVesselCalls(dataSourceUrn)
            elif "TEUReport" in dataSourceUrn:
                self.loadTEUReport(dataSourceUrn)
            elif "CommodityOrigins" in dataSourceUrn:
                self.loadCommodityOrigins(dataSourceUrn)
            elif "ImportedCommods" in dataSourceUrn:
                self.loadImportedCommods(dataSourceUrn)
            elif "HS2Codes" in dataSourceUrn:
                self.loadHS2Codes(dataSourceUrn)
            elif "PDTInputEconomicAnalysis" in dataSourceUrn:
                self.loadPDTInputEconomicAnalysis(dataSourceUrn)
            elif "DESInputSchedule" in dataSourceUrn:
                self.loadDESInputSchedule(dataSourceUrn)
            elif "DESOutputDB" in dataSourceUrn:
                self.loadDESOutputDB(dataSourceUrn)
        return

    def loadCommodityOrigins(self, dataSourceUrn):
        commodityOriginsDf = pd.read_csv( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        commodityOriginsDf = commodityOriginsDf.fillna(0)
        commodityOriginsDf = \
            commodityOriginsDf.astype({"HS Code 2 Digit": 'int32'})
        self.dataFramesDict[dataSourceUrn] = commodityOriginsDf
        
    def loadHS2Codes(self, dataSourceUrn):
        hs2CodesDf = pd.read_csv( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        self.dataFramesDict[dataSourceUrn] = hs2CodesDf

    def loadPDTInputEconomicAnalysis(self, dataSourceUrn):
        conn = self.createConnection( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        self.dataFramesDict[dataSourceUrn] = conn

    def loadDESOutputDB(self, dataSourceUrn):
        conn = self.createConnection( "/".join([self.scenarioDir, self.dataSourceDict[dataSourceUrn]]) )
        self.dataFramesDict[dataSourceUrn] = conn
        
    # MEASUREMENTS
    def getMeasurement(self, measurementUrn):
        result = None
        if "urn:cite:PDT_Econ:NumberOfCountries" ==\
           measurementUrn:
            result  = self.getNumberOfCountries()
        #elif "urn:cite:PDT_Econ:NumberOfTEUPerCountry" ==\
        #     measurementUrn:
        #    result = self.getNumberOfTEUPerCountry()
        #elif "urn:cite:PDT_Econ:NumberOfHS2CodesPerCountry" ==\
        #     measurementUrn:
        #    result = self.getNumberOfHS2CodesPerCountry()
        elif "urn:cite:PDT_Econ:NumberOfHS2Codes" ==\
             measurementUrn:
            result = self.getNumberOfHS2Codes()
        elif "urn:cite:PDT_Econ:PercentTEUPerHS2Code" ==\
             measurementUrn:
            result = self.getPercentTEUPerHS2Code()
        elif "urn:cite:PDT_Econ:PercentTEUPerCountry" ==\
             measurementUrn:
            result = self.getPercentTEUPerCountry()
        elif "urn:cite:PDT_Econ:PercentTEUPerHS2Code,Country" ==\
             measurementUrn:
            result = self.getPercentTEUPerHS2CodeCountry()
        elif "urn:cite:PDT_Econ:NumberCountriesPerHS2Code" ==\
             measurementUrn:
            result = self.getNumberCountriesPerHS2Code()
        #elif "urn:cite:PDT_Econ:USDPerCountry" ==\
        #     measurementUrn:
        #    result = self.getUSDPerCountry()
        #elif "urn:cite:PDT_Econ:USDPerHS2Code" ==\
        #     measurementUrn:
        #    result = self.getUSDValuePerHS2Code()
        #elif "urn:cite:PDT_Econ:USDPerHS2CodePerCountry" ==\
        #     mesurementUrn:
        #    result = self.getUSDPerHS2CodeCountry()
        return result

    def getNumberOfCountries(self):
        """
        Considering countries of Origin
        """
        result = None
        measurementUrn = "urn:cite:PDT_Econ:NumberOfCountries"
        dataSourceUrns = self.dataSourceDict.keys()
        
        nCountriesDf = pd.DataFrame(columns=["Value", "Data Source", "Ref"])
        
        #-- Data Source 1:  CommodityOrigins
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numCountries = commodityOriginDf["Foreign Initial Country"].nunique()
            numCountries = self.unitRegistry.Quantity(numCountries, 'country')            
            nCountriesDf = nCountriesDf.append({"Value": numCountries, "Data Source": commodityOriginUrn, "Ref": measurementEditionUrn}, ignore_index=True)

        #-- Data Source 2:  DESInputSchedule
        # TBD
        
        #-- Data Source 3:  PDTInputEconomicAnalysis
        econDbUrns = list(filter(lambda x: "PDTInputEconomicAnalysis" in x, dataSourceUrns))
        for econDbUrn in econDbUrns:
            econDbEdition = econDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = ".".join([measurementUrn, econDbEdition])
            countriesDf = self.selectAllCountries(econDbUrn)
            numCountries = countriesDf.shape[0]
            numCountries = self.unitRegistry.Quantity(numCountries, 'country')
            nCountriesDf = nCountriesDf.append({"Value": numCountries, "Data Source": econDbUrn, "Ref": measurementEditionUrn}, ignore_index=True)
        
        #-- Data Source 4:  DESOutputDB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            countriesDf = self.selectAllCountries(outputDbUrn)
            numCountries = countriesDf.shape[0]
            numCountries = self.unitRegistry.Quantity(numCountries, 'country')            
            nCountriesDf = nCountriesDf.append({"Value": numCountries, "Data Source": outputDbUrn, "Ref": measurementEditionUrn}, ignore_index=True)
        return nCountriesDf

    def selectAllCountries(self, dbUrn):
        conn = self.dataFramesDict[dbUrn]
        df = None
        if "PDTInputEconomicAnalysis" in dbUrn:
            monthStr = self.getMonthTable()
            query = "SELECT DISTINCT Country FROM " + monthStr
            df = pd.read_sql_query(query, conn)
        elif "DESOutputDB" in dbUrn:
            query = "SELECT DISTINCT Origin FROM output"
            df = pd.read_sql_query(query, conn)
        return df

    def getMonthTable(self):
        tableList = ["Jan18", "Feb18", "Mar18", "Apr18", "May18", "Jun18", "Jul18", "Aug18", "Sep18", "Oct17", "Nov17", "Dec17"]
        monthStr = tableList[ self.month - 1]
        return monthStr
    
    def getNumberOfHS2Codes(self):
        measurementUrn = "urn:cite:PDT_Econ:NumberOfHS2Codes"
        dataSourceUrns = self.dataSourceDict.keys()
        nHS2CodesDf = pd.DataFrame(columns = ["Value", "Data Source", "Ref"])
        
        #-- Data Source 1:  Commodity Origins
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numHS2Codes = commodityOriginDf["HS Code 2 Digit"].nunique()
            numHS2Codes = self.unitRegistry.Quantity(numHS2Codes, 'HS2')            
            nHS2CodesDf = nHS2CodesDf.append({"Value": numHS2Codes, "Data Source": commodityOriginUrn, "Ref": measurementEditionUrn}, ignore_index=True)
            
        #-- Data Source 2:  Imported Commods
        importedCommodsUrns = list(filter(lambda x: "ImportedCommods" in x, dataSourceUrns))
        for importedCommodsUrn in importedCommodsUrns:
            importedCommodsEdition = importedCommodsUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, importedCommodsEdition])
            importedCommodsDf = self.dataFramesDict[importedCommodsUrn]
            numHS2Codes = commodityOriginDf["HS Code 2 Digit"].nunique()
            numHS2Codes = self.unitRegistry.Quantity(numHS2Codes, 'HS2')                        
            nHS2CodesDf = nHS2CodesDf.append({"Value": numHS2Codes, "Data Source": importedCommodsUrn, "Ref": measurementEditionUrn}, ignore_index=True)
            
        #-- Data Source 3:  HS2Codes
        hs2CodeUrns = list(filter(lambda x: "HS2Codes" in x, dataSourceUrns))
        for hs2CodeUrn in hs2CodeUrns:
            hs2CodeEdition = hs2CodeUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, hs2CodeEdition])
            hs2CodeDf = self.dataFramesDict[hs2CodeUrn]
            numHS2Codes = hs2CodeDf["HS Code"].nunique()
            numHS2Codes = self.unitRegistry.Quantity(numHS2Codes, 'HS2')                        
            nHS2CodesDf = nHS2CodesDf.append({"Value": numHS2Codes, "Data Source": hs2CodeUrn, "Ref": measurementEditionUrn}, ignore_index=True)

        #-- Data Source 4:  PDT Input Economic Analysis
        econDbUrns = list(filter(lambda x: "PDTInputEconomicAnalysis" in x, dataSourceUrns))
        for econDbUrn in econDbUrns:
            econDbEdition = econDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = ".".join([measurementUrn, econDbEdition])
            hs2CodeDf = self.selectAllHS2Codes(econDbUrn)
            numHS2Codes = len(np.flatnonzero((hs2CodeDf != 0).any(axis=0)))
            numHS2Codes = self.unitRegistry.Quantity(numHS2Codes, 'HS2')                        
            nHS2CodesDf = nHS2CodesDf.append({"Value": numHS2Codes, "Data Source": econDbUrn, "Ref": measurementEditionUrn}, ignore_index=True)
            
        #-- Data Source 5:  PDT Output DB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurmentEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            nHSCodesDf = self.selectAllHS2Codes(outputDbUrn)
            numHS2Codes = nHSCodesDf.shape[0]
            numHS2Codes = self.unitRegistry.Quantity(numHS2Codes, 'HS2')            
            nHS2CodesDf = nHS2CodesDf.append({"Value": numHS2Codes, "Data Source": outputDbUrn, "Ref": measurementEditionUrn}, ignore_index=True)
        return nHS2CodesDf

    def selectAllHS2Codes(self, dbUrn):
        conn = self.dataFramesDict[dbUrn]
        df = None
        if "PDTInputEconomicAnalysis" in dbUrn:
            monthStr = self.getMonthTable()
            query = "SELECT * FROM " + monthStr
            df = pd.read_sql_query(query, conn)
        elif "DESOutputDB" in dbUrn:
            query = "SELECT DISTINCT \"NAICS Type\" FROM output"
            df = pd.read_sql_query(query, conn)
        return df

    def getPercentTEUPerHS2Code(self):
        measurementUrn = "urn:cite:PDT_Econ:PercentTEUPerHS2Code"
        dataSourceUrns = self.dataSourceDict.keys()

        nCodes = 98
        hs2CodeCols = list(map(lambda x: x, range(0, nCodes+1)))
        hs2CodeCols = hs2CodeCols + ["Data Source", "Ref"]
        pctTEUPerHS2CodeDf = pd.DataFrame(columns = hs2CodeCols)

        #-- Data Source 1:  Commodity Origins
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numTEUDf = commodityOriginDf.groupby(["HS Code 2 Digit"])["TEUS"].sum()
            total = numTEUDf.sum()  # different if sum by CommodityOrigin by 1500 TODO: debug
            numTEUDfPct = numTEUDf / total * 100
            numTEUDfPct = numTEUDfPct.round(2)
            hs2CodeDict =\
                dict(zip( range(1,nCodes+1), np.zeros(nCodes) ))

            for hs2Code in range(1,nCodes+1):
                if hs2Code in numTEUDfPct:
                    val = numTEUDfPct.at[hs2Code]
                    hs2CodeDict[hs2Code] = val
            hs2CodeDict["Data Source"] = commodityOriginUrn
            hs2CodeDict["Ref"] = measurementEditionUrn
            pctTEUPerHS2CodeDf = \
                pctTEUPerHS2CodeDf.append(pd.Series(hs2CodeDict), ignore_index=True)
            
        #-- Data Source 2:  Imported Commods
        importedCommodsUrns = list(filter(lambda x: "ImportedCommods" in x, dataSourceUrns))
        for importedCommodsUrn in importedCommodsUrns:
            importedCommodsEdition = importedCommodsUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, importedCommodsEdition])
            importedCommodsDf = self.dataFramesDict[importedCommodsUrn]
            numTEUDf = importedCommodsDf.groupby(["HS Code 2 Digit"])["TEUS"].sum()
            total = numTEUDf.sum()
            numTEUDfPct = numTEUDf / total * 100
            numTEUDfPct = numTEUDfPct.round(2).sort_values(ascending=False)
            hs2CodeDict =\
                dict(zip( range(1, nCodes+1), np.zeros(nCodes) ))

            for hs2Code in range(1, nCodes+1):
                if hs2Code in numTEUDfPct:
                    val = numTEUDfPct.at[hs2Code]
                    hs2CodeDict[hs2Code] = val 
                else:
                    hs2CodeDict[hs2Code] = 0
            hs2CodeDict["Data Source"] = importedCommodsUrn
            hs2CodeDict["Ref"] = measurementEditionUrn
            pctTEUPerHS2CodeDf = \
                pctTEUPerHS2CodeDf.append(pd.Series(hs2CodeDict), ignore_index=True)

        #-- Data Source 3:  PDT Output DB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            hs2CodeDictDf = self.selectTEUCountsByHS2Codes(outputDbUrn)
            hs2CodeDict =\
                dict(zip( range(0, nCodes+1), np.zeros(nCodes+1) ))
            #includes '' and n/a so won't sum to 100%
            total = hs2CodeDictDf["TEU"].sum() 
            for idx, row in hs2CodeDictDf.iterrows():
                key = int(idx)
                if key in range(0, nCodes+1):
                    val = float(row["TEU"]) / total * 100
                    hs2CodeDict[key] = round(val, 2)
            hs2CodeDict["Data Source"] = outputDbUrn
            hs2CodeDict["Ref"] = measurementEditionUrn
            pctTEUPerHS2CodeDf = \
                pctTEUPerHS2CodeDf.append(pd.Series(hs2CodeDict), ignore_index=True)

        return pctTEUPerHS2CodeDf

    def selectTEUCountsByHS2Codes(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT \"NAICS Type\", COUNT(DISTINCT container_name) as TEU FROM container GROUP BY \"NAICS Type\""
        df = pd.read_sql_query(query,conn)
        df = df.set_index("NAICS Type")
        df.loc['0'] = df.loc[''] + df.loc['n/a']
        df.drop('', inplace=True)
        df.drop('n/a', inplace=True)
        #df.index = df.index.astype('int32')
        return df
    
    def getPercentTEUPerCountry(self):
        measurementUrn = "urn:cite:PDT_Econ:PercentTEUPerCountry"
        dataSourceUrns = self.dataSourceDict.keys()

        #-- Data Source 0:  Country Cols
        pctTEUPerCountryDf = None

        #-- Data Source 1:  Commodity Origins
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numTEUDf = commodityOriginDf.groupby(["Foreign Initial Country"])["TEUS"].sum()
            total = float(numTEUDf.sum())
            numTEUDfPct = numTEUDf / total * 100
            numTEUDfPct = numTEUDfPct.round(2)

            countryCodes = commodityOriginDf["Foreign Initial Country"].unique().tolist()
            countryCodeCols = countryCodes + ["Data Source", "Ref"]            
            pctTEUPerCountryDf = pd.DataFrame(columns=countryCodeCols)  #Better have this data source!
            
            nCodes = len(countryCodes)
            countryCodesDict = \
                dict(zip( countryCodes, np.zeros(nCodes) ))

            for countryCode in countryCodes:
                if countryCode in numTEUDfPct:
                    val = numTEUDfPct.at[countryCode]
                    countryCodesDict[countryCode] = val
            countryCodesDict["Data Source"] = commodityOriginUrn
            countryCodesDict["Ref"] = measurementEditionUrn
            pctTEUPerCountryDf = \
                pctTEUPerCountryDf.append(pd.Series(countryCodesDict), ignore_index=True)

        #-- Data Source 2:  PDT Input Schedule
        # TBD
        
        #-- Data Source 3:  PDT Output DB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            countryCodesDictDf = self.selectTEUCountsByCountry(outputDbUrn)
            countryCodeDict = \
                dict(zip( countryCodes, np.zeros(nCodes) ))

            total = countryCodesDictDf["TEU"].sum()
            for idx, row in countryCodesDictDf.iterrows():
                key = row["Origin"]
                if '' == key or "n/a" == key:
                    continue
                if key in countryCodes:
                    val = float(row["TEU"]) / total * 100
                    countryCodeDict[key] = round(val, 2)
            countryCodeDict["Data Source"] = outputDbUrn
            countryCodeDict["Ref"] = measurementEditionUrn
            pctTEUPerCountryDf = \
                pctTEUPerCountryDf.append(pd.Series(countryCodeDict), ignore_index=True)
        return pctTEUPerCountryDf

    def selectTEUCountsByCountry(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT Origin, COUNT(DISTINCT container_name) as TEU from container GROUP BY Origin"
        df = pd.read_sql_query(query, conn)
        return df

    def getNumberCountriesPerHS2Code(self):
        measurementUrn = "urn:cite:PDT_Econ:NumberCountriesPerHS2Code"
        dataSourceUrns = self.dataSourceDict.keys()

        nCodes = 98
        hs2CodeCols = list(map(lambda x: x, range(1, 98+1)))
        hs2CodeCols = hs2CodeCols + ["Data Source", "Ref"]
        countriesPerHS2CodeDf = pd.DataFrame(columns = hs2CodeCols)

        #-- Data Source 1:  CommodityOrigins
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numCountriesDf = commodityOriginDf.groupby(["HS Code 2 Digit"])["Foreign Initial Country"].count()

            hs2CodeDict =\
                dict(zip( range(1, nCodes+1), np.zeros(nCodes) ))

            for hs2Code in range(1, nCodes+1):
                if hs2Code in numCountriesDf:
                    val = numCountriesDf.at[hs2Code]
                    hs2CodeDict[hs2Code] = val
            hs2CodeDict["Data Source"] = commodityOriginUrn
            hs2CodeDict["Ref"] = measurementEditionUrn
            countriesPerHS2CodeDf = \
                countriesPerHS2CodeDf.append(pd.Series(hs2CodeDict), ignore_index=True)
            
        #-- Data Source 2:  PDT Input Schedule
        #-- Data Source 3:  PDT Output DB
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            hs2CodeDictDf = self.selectCountryCountsByHS2Codes(outputDbUrn)
            hs2CodeDict =\
                dict(zip( range(1, nCodes+1), np.zeros(nCodes) ))
            #includes '' and n/a so won't sum to 100%

            for idx, row in hs2CodeDictDf.iterrows():
                key = row["NAICS Type"]
                if '' != key and "n/a" != key:
                    key = int(key)
                if key in range(1, nCodes+1):
                    val = row["NumOriginCountries"]
                    hs2CodeDict[key] = val
            hs2CodeDict["Data Source"] = outputDbUrn
            hs2CodeDict["Ref"] = measurementEditionUrn
            countriesPerHS2CodeDf = \
                countriesPerHS2CodeDf.append(pd.Series(hs2CodeDict), ignore_index=True)
        return countriesPerHS2CodeDf
    
    def selectCountryCountsByHS2Codes(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT \"NAICS Type\", COUNT(DISTINCT Origin) as NumOriginCountries FROM container GROUP BY \"NAICS Type\""
        df = pd.read_sql_query(query,conn)
        return df
            
    def getPercentTEUPerHS2CodeCountry(self):
        result = {}
        resultKeys = []
        measurementUrn = "urn:cite:PDT_Econ:PercentTEUPerHS2Code"
        dataSourceUrns = self.dataSourceDict.keys()

        # HS 2 Codes
        nCodes = 98
        hs2CodeCols = list(map(lambda x: x, range(0, 98+1)))

        # Country codes as an index
        countryCodes = None
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            countryCodes = commodityOriginDf["Foreign Initial Country"].unique()

        # Data Source 1:  CommodityOrigins
        resultDf = pd.DataFrame(index=countryCodes, columns=hs2CodeCols)                
        pctTEUHS2CodeCountryDf = None
        commodityOriginUrns = list(filter(lambda x: "CommodityOrigins" in x, dataSourceUrns))
        for commodityOriginUrn in commodityOriginUrns:
            commodityOriginEdition = commodityOriginUrn.split(':')[-1].replace(".","_")
            measurementEditionUrn = \
                ".".join([measurementUrn, commodityOriginEdition])
            commodityOriginDf = self.dataFramesDict[commodityOriginUrn]
            numTEUHS2CodeCountryDf = commodityOriginDf.groupby(["HS Code 2 Digit","Foreign Initial Country"])["TEUS"].sum()
            numTEUHS2CodeDf = commodityOriginDf.groupby(["HS Code 2 Digit"])["TEUS"].sum()
            pctTEUHS2CodeCountryDf = numTEUHS2CodeCountryDf / numTEUHS2CodeDf * 100
            pctTEUHS2CodeCountryDf = pctTEUHS2CodeCountryDf.round(2)
            resultKeys.append(commodityOriginUrn)

        # Data Source 2:  PDT Output DB
        resultDf2 = pd.DataFrame(index=countryCodes, columns=hs2CodeCols)                
        pctTEUHS2CodeCountryDf2 = None
        outputDbUrns = list(filter(lambda x: "DESOutputDB" in x, dataSourceUrns))
        for outputDbUrn in outputDbUrns:
            outputDbEdition = outputDbUrn.split(':')[-1].replace(".", "_")
            measurementEditionUrn = \
                ".".join([measurementUrn, outputDbEdition])
            numTEUHS2CodeCountryDf2 = self.selectTEUCountsByHS2CodeCountry(outputDbUrn)
            numTEUHS2CodeDf2 = self.selectTEUCountsByHS2Codes(outputDbUrn)
            pctTEUHS2CodeCountryDf2 = numTEUHS2CodeCountryDf2 / numTEUHS2CodeDf2 * 100
            pctTEUHS2CodeCountryDf2 = pctTEUHS2CodeCountryDf2.round(2)
            resultKeys.append(outputDbUrn)

        # ITERATE AND OUTPUT RESULT
        resultDf.fillna(0.0,inplace=True)
        for hs2Code, newDf in pctTEUHS2CodeCountryDf.groupby(level=0):
            for country in newDf.index.get_level_values("Foreign Initial Country"):
                resultDf.loc[country][hs2Code] = newDf.loc[hs2Code, country]
                
        resultDf2.fillna(0.0,inplace=True)
        for hs2Code, newDf in pctTEUHS2CodeCountryDf2.groupby(level=0):
            for country in newDf.index.get_level_values("Origin"):
                if 'n/a' == country:
                    continue
                resultDf2.loc[country][int(hs2Code)] = newDf.loc[hs2Code,country]["TEU"]
                
        # FOLD EconCalibrationReporter into build
        # NOLH Extension for Baseline and Disrupted
        results = dict(zip( resultKeys, [resultDf, resultDf2] ))
        return results

    def selectTEUCountsByHS2CodeCountry(self, outputDbUrn):
        conn = self.dataFramesDict[outputDbUrn]
        query = "SELECT \"NAICS Type\", Origin, COUNT(DISTINCT container_name) as TEU FROM container GROUP BY \"NAICS Type\", Origin"
        df = pd.read_sql_query(query, conn)
        df = df.set_index(["NAICS Type", "Origin"])
        df = df.rename(index={'':'0'})
        df.loc[('0', 'n/a'), :] = df.loc['n/a','n/a']["TEU"]
        df.drop('n/a', inplace=True)
        return df
