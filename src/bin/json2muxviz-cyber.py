"""
Created on April 25, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import MuxVizCommunicationsNetworkDAO

from networkx.readwrite import json_graph
import json
import networkx as nx
import sys

def usage():
    print("json2muxviz-cyber.py <jsonFilePath> <muxvizDirPath>")
    sys.exit(-1)

def main(argv):
    jsonFilePath = argv[0]
    muxvizDirPath = argv[1]

    cnDAO = MuxVizCommunicationsNetworkDAO()
    cnDAO.readNetwork(jsonFilePath)
    cnDAO.writeNetwork(muxvizDirPath)

if __name__ == "__main__":
    main(sys.argv[1:])


