"""
Created on March 18, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign.  All rights reserved
"""
import math
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as st

"""
cat data/everglades/kpi/stat.csv | cut -f4 -d, | cut -d' ' -f1 | sort | uniq
"Commodity
Bananas
Flowers
Mellons
Shirts
Ties
"""

class MNRKPIAnalyzer():
    """
    A class designed to analyze Key Performance Indicators
      one particular type of analysis considered here is the
      Minimum Number of Runs.
    """
    @staticmethod
    def create(statFilePath):
        kAnalyzer = MNRKPIAnalyzer()
        kAnalyzer.df = pd.read_csv(statFilePath)
        return kAnalyzer

    def computeTimeInSystem(self):
        self.df["pdt:timeInSystem"] = self.df["End Time"] - self.df["Start Time"]
        
    def computeMNRAlgorithm1(self, measureKey, alpha, e):
        """
          Employ a 'one-step' algorithm in which "a fixed number of
           initial runs are performed to estimate the sample mean
           and standard deviation of a Measure of Performance" (Truong 2015).

           Utilized by Chu et al (2004)
           Cited by Tian et al, Truong et al (2015)

           The standard deviation of population is unknown.
           We are assuming here that the Measure of Performance is
             normally distributed.
        """        
        # sample standard mean and deviation
        std = self.df.loc[:,measureKey].std(axis=0)
        mean = self.df.loc[:,measureKey].mean(axis=0)
        
        # compute the percent point function of the t dist
        #  we do a two-sided test
        degreesOfFreedom = self.df.shape[0] - 1 
        t = 1.96 

        numer = t * std
        demom = mean * e

        mnr = math.ceil( math.pow( numer/denom ), 2.0 )

        return mnr

    def filterData(self, columnName, columnValues):
        rowsFilter = "|".join(columnValues)
        self.df = self.df.loc[ self.df[columnName].str.contains(rowsFilter)==True]        



    def computeHist(self, measureKey, outputFilePath):
        plt.hist(self.df.loc[:,measureKey], bins="auto")
        plt.title("Histogram for " + measureKey)
        plt.savefig(outputFilePath)

    def computeMNR(self, measureKey, alpha, e):
        """
        Given a set of data, compute the number of runs needed to 
          estimate the population mean and standard deviation of a 
          measure of performance.
          """
        # Filter to see if have an effect on MNR

        return self.computeMNRAlgorithm1(measureKey, alpha, e)

    
    
