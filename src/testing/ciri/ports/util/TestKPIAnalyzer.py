"""
Created on March 18, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from ciri.ports.util.KPIAnalyzer import MNRKPIAnalyzer
import unittest

class TestMNRKPIAnalyzer(unittest.TestCase):


    def testCreate(self):
        statCSVFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/kpi/stat.test.csv"
        mnrAnalyzer = MNRKPIAnalyzer.create(statCSVFilePath)
        self.assertEqual( mnrAnalyzer.df.shape[0], 999)

    def testComputeMNR(self):
        statCSVFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/kpi/stat.csv"
        mnrAnalyzer = MNRKPIAnalyzer.create(statCSVFilePath)

        """
        alpha: parameter for the 2-sided confidence interval
        e:  allowable error specified as a percentage of the mean

        In the paper by Chu et al, a 90% confidence interval and 5% allowable
          error were used.
        """
        commodityGroups = ["Bananas","Flowers","Mellons","Shirts","Ties"]
        mnrAnalyzer.computeTimeInSystem()
        
        mnr = mnrAnalyzer.computeMNR("pdt:timeInSystem", alpha, e)
        mnrAnalyzer.computeHist("pdt:timeInSystem", "retail.png")
        self.assertEqual( mnr, 227 )


if __name__ == '__main__':
    unittest.main()
    
