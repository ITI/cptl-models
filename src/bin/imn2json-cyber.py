"""
Created on March 15, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import IMNCommunicationsNetworkDAO
from networkx.readwrite import json_graph
import json
import networkx as nx
import sys

def usage():
    print("imn2json.py <imnFilePath> <geocodeFilePath> <jsonFilePath>")
    sys.exit(-1)
    
def main(argv):
    imnFilePath = argv[0]
    geocodeFilePath = argv[1]
    jsonFilePath = argv[2]
    
    print(imnFilePath)
    print(geocodeFilePath)
    print(jsonFilePath)

    cnDAO = IMNCommunicationsNetworkDAO.create(imnFilePath)
    gCyber = cnDAO.getNetwork(imnFilePath)
    gCyberGeocoded = cnDAO.geocodeNetwork(gCyber, geocodeFilePath)
    cnDAO.writeNetwork(gCyberGeocoded, jsonFilePath)

if __name__ == "__main__":
    main(sys.argv[1:])
    
