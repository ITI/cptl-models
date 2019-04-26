"""
Created on April 27, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from edu.illinois.iti.dao.MultilayerNetworkDAO import JSONMultilayerNetworkDAO
import os
import sys

def usage():
    print("json2multilayer.py <networkInventoryFilePath> <networkName1> <networkName2> <icNetworkName> <outputFilePath>")
    sys.exit(-1)

def main(argv):
    networkInventoryFilePath = argv[0]
    networkName1 = argv[1]
    networkName2 = argv[2]
    icNetworkName = argv[3]
    outputFilePath = argv[4]
    
    scenarioDirPrefix = os.getcwd() + "/build/data/everglades/"

    mnDAO = JSONMultilayerNetworkDAO.create(networkInventoryFilePath, \
                                                scenarioDirPrefix)
    icNetworkNames = [ icNetworkName ]
    gMultilayer = mnDAO.mergeNetworks(networkName1, networkName2, icNetworkNames)
    mnDAO.writeNetwork(gMultilayer, outputFilePath)

if __name__ == "__main__":
    main(sys.argv[1:])
