"""
Created on February 27, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved
"""
from ciri.ports.dao.FinancialReportDAO import CSVTEUReportDAO
from datetime import datetime
import unittest

class TestCSVTEUReportDAO(unittest.TestCase):
    
    def setUp(self):
        self.reportDAO = CSVTEUReportDAO()

    def testReadTEUReport(self):
        reportFY2017InputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/TEU Report FY2017.csv"        
        fiscalYear = datetime.strptime( "2017", "%Y")
        teuReport = self.reportDAO.readTEUReport(reportFY2017InputFilePath, fiscalYear)
        self.assertEqual( len(teuReport), 4 )
        
    def testConvertToPandasDataframe(self):
        reportFY2017InputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/TEU Report FY2017.csv"  
        fiscalYear = datetime.strptime( "2017", "%Y")
        teuReport = self.reportDAO.readTEUReport(reportFY2017InputFilePath, fiscalYear)
        
        df = self.reportDAO.convertToPandasDataframe(teuReport, discretized=False)
        print(df.head())
        print(df.dtypes)

if __name__ == '__main__':
    unittest.main()

