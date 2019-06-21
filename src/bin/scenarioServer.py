"""
Created on June 21, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from edu.illinois.iti.servers import ScenarioServerWrapper
import sys

def usage():
    print("scenarioServer.py <serverName> <serverPort> <scenarioDir>")
    sys.exit(-1)

def main(argv):
    serverName = argv[0]
    serverPort = argv[1]
    scenarioDir = argv[2]
    
    scenarioServer = ScenarioServerWrapper.create(serverName, "127.0.0.1", serverPort, scenarioDir)
    scenarioServer.start(debugOn=True)

if __name__ == '__main__':
    main(sys.argv[1:])

    
