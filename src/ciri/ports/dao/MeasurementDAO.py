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

class BasicMeasurementDAO():

    daos = None
    dataSources = None
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
                reportDAO = CSVTEUReportDAO.create(dataFilePath)
                sGenerator.daos[ref] = reportDAO
            elif "CSVVesselScheduleDAO" == daoType:
                vesselDAO = CSVVesselScheduleDAO.create(dataFilePath)
                sGenerator.daos[ref] = vesselDAO
            elif "CSVVesselShipmentDAO" == daoType:
                vsDAO = CSVVesselShipmentDAO.create(dataFilePath)
                sGenerator.daos[ref] = vsDAO
            elif "CSVODPairsVesselShipmentDAO" == daoType:
                vsODDAO = CSVODPairsVesselShipmentDAO.create(dataFilePath)
                sGenerator.daos[ref] = vsODDAO
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
        

