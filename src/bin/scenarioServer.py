"""
Created on June 21, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from edu.illinois.iti.servers import ScenarioServerWrapper
import sys

def usage():
    print("scenarioServer.py <serverName> <serverIP> <serverPort> <scenarioDir>")
    sys.exit(-1)

def main(argv):
    serverName = argv[0]
    serverIP = argv[1]
    serverPort = argv[2]
    scenarioDir = argv[3]
    
    scenarioServer = ScenarioServerWrapper.create(serverName, serverIP, serverPort, scenarioDir)
    scenarioServer.start(debugOn=True)

if __name__ == '__main__':
    main(sys.argv[1:])

    
