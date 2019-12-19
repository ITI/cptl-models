"""
Created on March 21, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from ciri.ports.dao.FinancialReportDAO import CSVTEUReportDAO
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
from ciri.ports.dao.VesselShipmentDAO import CSVODPairsVesselShipmentDAO, CSVVesselShipmentDAO
from jsonschema import validate
import datetime
import json
import logging
import pandas as pd
import random
import uuid

class ScenarioGenerator():

    daos = None
    dataSources = None
    dfs = None
    logger = None

    @staticmethod
    def create(dataSources):
        sGenerator = ScenarioGenerator()

        sGenerator.daos = {}
        sGenerator.dataSources = dataSources
        sGenerator.dfs = {}

        for ref, t in self.dataSources:
            filePath = t[0]
            daoType = t[1]
            
            if "CSVTEUReportDAO" == daoType:
                reportDAO = CSVTEUReportDAO()
                # cheat
                fiscalYear = datetime.strptime("2017", "%Y")
                teuReport = reportDAO.readTEUReport(filePath, fiscalYear)
                sGenerator.daos[ref] = reportDAO
                sGenerator.dfs[ref] = reportDAO.convertToPandasDataframe(teuReport, discretized=False)
            elif "CSVVesselScheduleDAO" == daoType:
                vesselDAO = CSVVesselScheduleDAO()
                vesselSchedule = vesselDAO.readVesselSchedule(filePath)
                sGenerator.daos[ref] = vesselDAO
                sGenerator.dfs[ref] = vesselDAO.convertToPandasDataframe(vesselSchedule, discretized=False)
            elif "CSVVesselShipmentDAO" == daoType:
                vsDAO = CSVVesselShipmentDAO()
                vesselCommodities = vsDAO.readVesselCommodities(filePath)
                sGenerator.daos[ref] = vsDAO
                sGenerator.dfs[ref] = vsDAO.convertToPandasDataframe(vesselCommodities, discretized=False)
            elif "CSVODPairsVesselShipmentDAO" == daoType:
                vsODDAO = CSVODPairsVesselShipmentDAO()
                vesselCommoditiesImports = vsODDAO.readVesselCommodities(filePath)
                sGenerator.daos[ref] = vsODDAO
                sGenerator.dfs[ref] = vsODDAO.convertToPandasDataframe(vesselCommoditiesImports, discretized=False)
            else:
                raise Exception("Unrecognized DAO Type!")
            
        return sGenerator

    def getDataSourceInventory(self):
        return self.dataSources.keys()
    
    def getValidMeasurements(self, dataSourceRef):
        measurements = self.daos[dataSourceRef]._measurements 
        return measurements

    def getMeasurement(self, measurementRef):
        dataSourceRef, measurementName = measurementRef.split("#")
        return self.daos[dataSourceRef].getMeasurement(measurementName)
        

