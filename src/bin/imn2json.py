"""
Created on March 15, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import IMNCommunicationsNetworkDAO
import json
import networkx as nx
import sys

def usage():
    print("imn2json.py <imnFilePath> <jsonFilePath>")
    sys.exit(-1)
    
def main(argv):
    imnFilePath = argv[0]
    jsonFilePath = argv[1]
    
    cnDAO = IMNCommunicationsNetworkDAO.create(imnFilePath)
    G = cnDAO.getNetwork(imnFilePath)
    gData = nx.node_link_data(G)
    with open(jsonFilePath, 'w') as outfile:
        json.dump(gData, outfile, indent=4)

if __name__ == "__main__":
    main(sys.argv[1:])
    
