"""
Created on March 14, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import IMNCommunicationsNetworkDAO
import json
import networkx as nx
import unittest

class TestIMNCommunicationsNetworkDAO(unittest.TestCase):

    def setUp(self):
        self.imnFilePath = "data/testing/simple.imn"
        self.cnDAO = IMNCommunicationsNetworkDAO.create(self.imnFilePath)

    def test_init(self):
        self.assertEqual(self.cnDAO.networkFilePath, self.imnFilePath)

    def test_get_entity_occurrences(self):
        expectedCounts = {}
        expectedCounts["imn:type"] = 3
        expectedCounts["imn:hostname"] = 3
        expectedCounts["imn:interface"] = 2
        expectedCounts["imn:network-config"] = 3
        expectedCounts["imn:canvas"] = 4
        expectedCounts["imn:iconcoords"] = 3
        expectedCounts["imn:labelcoords"] = 3
        expectedCounts["imn:config"] = 1
        expectedCounts["imn:custom-config"] = 1
        expectedCounts["imn:services"] = 1
        expectedCounts["imn:interface-peer"] = 4
        expectedCounts["imn:mirror"] = 1
        expectedCounts["imn:nodeStart"] = 3
        expectedCounts["imn:node"] = 3
        expectedCounts["imn:nodes"] = 2
        expectedCounts["imn:bandwidth"] = 2
        expectedCounts["imn:link"] = 2
        
        with open(self.cnDAO.networkFilePath, "r") as networkFile:
            networkFileLines = "".join(networkFile.readlines())

            entityTypes = self.cnDAO.getEntityTypes()
            for entityType in entityTypes:
                entityOccurrences = self.cnDAO.getEntityOccurrences(networkFileLines, entityType)
                # comment this out or tee the entityOccurrences iterator
                #print(entityType)
                #for r, start, end in entityOccurrences:
                #    print("\t Found {0} at [{1}:{2}]", r, start, end )            
                actualOccurrenceCount = sum(1 for x in entityOccurrences)         
                expectedOccurrenceCount = expectedCounts[entityType] 
                self.assertEqual( actualOccurrenceCount, expectedOccurrenceCount, entityType )

    def test_get_network(self):
        G = self.cnDAO.getNetwork(self.cnDAO.networkFilePath)
        self.assertEqual(G.number_of_nodes(), 3)
        self.assertEqual(G.number_of_edges(), 2)

        gData = nx.node_link_data(G)
        gStr = json.dumps(gData, indent=4)
        print(gStr)

if __name__ == '__main__':
    unittest.main()

    
        
