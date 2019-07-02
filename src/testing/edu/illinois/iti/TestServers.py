"""
Created on April 18, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from edu.illinois.iti.servers import ScenarioServerAction, ScenarioServerClient, ScenarioServerWrapper
import os
import os.path
import unittest

"""
class TestScenarioServerWrapper(unittest.TestCase):

    dataDir = "/home/euclid/Documents/cptl-models/data/test-scenarios/"
    serverName = "testserver"
    serverIP = "127.0.0.1"
    serverPort = "8080"
    scenarioServer = None
    
    def setUp(self):
        self.scenarioServer = ScenarioServerWrapper.create(self.serverName,\
                                                           self.serverIP,\
                                                           self.serverPort,\
                                                           self.dataDir)
        self.scenarioServer.start(debugOn=True)

    def testGetScenarios(self):
        inventoryFile = "inventory.json"
        scenarioInv = self.scenarioServer.getScenarios(inventoryFile)
        self.assertEqual(len(scenarioInv), 1)
        self.assertTrue("pev-testv1" in scenarioInv.keys())

    def testGetScenario(self):
        scenarioId = "pev-testv1"
        scenarioDesc = self.scenarioServer.getScenarioDescription(scenarioId)
        self.assertEqual(len(scenarioDesc["networks"]), 3)
        self.assertEqual(len(scenarioDesc["flows"]), 1)

    def testGetNetwork(self):
        networkId = "trans-southport-v1"
        networkDesc = self.scenarioServer.getNetwork(networkId)
        self.assertEqual(len(networkDesc["links"], 5))
"""

class TestScenarioServerClient(unittest.TestCase):

    """
    A wrapper function for requests to the scenario server
    """
    serverIP = "192.168.2.1"
    serverPort = "1336"

    # These tests assume 
    def testGetScenarios(self):
        scenarioClient = ScenarioServerClient.create(self.serverIP, self.serverPort)
        invFileName = "inventory.json"
        jsonData = scenarioClient.getScenarios(invFileName)
        self.assertEqual(len(jsonData.keys()), 1)

    def testGetScenarioDescription(self):
        scenarioClient = ScenarioServerClient.create(self.serverIP, self.serverPort)
        scenarioId= "pevtest-v1"
        jsonData = scenarioClient.getScenarioDescription(scenarioId)
        self.assertEqual(len(jsonData["networks"]), 3)

    def testGetNetworkDescription(self):
        scenarioClient = ScenarioServerClient.create(self.serverIP, self.serverPort)
        scenarioId= "pevtest-v1"
        networkId = "trans-cyber-v1"
        jsonData = scenarioClient.getNetworkDescription(scenarioId, networkId)
        self.assertEqual(len(jsonData["links"]), 1)

        
if __name__ == '__main__':
    unittest.main()
