"""
Created on March 14, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import IMNCommunicationsNetworkDAO, MuxVizCommunicationsNetworkDAO
from networkx.readwrite import json_graph
import json
import networkx as nx
import os
import unittest

class TestIMNCommunicationsNetworkDAO(unittest.TestCase):

    def setUp(self):
        self.imnFilePath = "data/testing/simple.imn"
        self.cnDAO = IMNCommunicationsNetworkDAO.create(self.imnFilePath)

        self.pevGeocodeFilePath = "data/everglades/cyber/PEV.geocoding.csv"
        self.pevFilePath = "data/everglades/cyber/PEV.imn"

        self.cnDAO2 = IMNCommunicationsNetworkDAO.create(self.pevFilePath)
        

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

        gData = json_graph.node_link_data(G)
        gStr = json.dumps(gData, indent=4)

        G2 = self.cnDAO2.getNetwork(self.cnDAO2.networkFilePath)
        self.assertEqual(G2.number_of_nodes(), 7)
        self.assertEqual(G2.number_of_edges(), 6)
        gData2 = json_graph.node_link_data(G2)
        gStr2 = json.dumps(gData2, indent=4)

    def test_geocode_network(self):
        gCyber = self.cnDAO2.getNetwork(self.cnDAO2.networkFilePath)
        gCyberGeocoded = self.cnDAO2.geocodeNetwork(gCyber, self.pevGeocodeFilePath)
        gData = json_graph.node_link_data(gCyber)
        gStr = json.dumps(gData, indent=4)
        print(gStr)

class TestMuxVizCommunicationsNetworkDAO(unittest.TestCase):
    
    communicationsNetworkInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/everglades/cyber/PEV.communicationsv2.json"
    communicationsNetworkSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/network.communications.schema.json"

    def testReadCommunicationsNetwork(self):
        cnDAO = MuxVizCommunicationsNetworkDAO()
        cnDAO.readNetwork(self.communicationsNetworkInputFilePath)
        self.assertEqual( len(cnDAO.gCyber.nodes()), 7)
        
    def testGetExtendedEdges(self):
        cnDAO = MuxVizCommunicationsNetworkDAO()
        cnDAO.readNetwork(self.communicationsNetworkInputFilePath)
        
        edgeList = cnDAO.getExtendedEdges()
        self.assertEqual( len(edgeList), len(cnDAO.gCyber.edges()) )

    def testGetNodes(self):
        cnDAO = MuxVizCommunicationsNetworkDAO()
        cnDAO.readNetwork(self.communicationsNetworkInputFilePath)

        nodeList = cnDAO.getNodes()
        self.assertEqual( len(nodeList), len(cnDAO.gCyber.nodes()) )

    def testWriteNetwork(self):
        outputDirPath = "/tmp"
        cnDAO = MuxVizCommunicationsNetworkDAO()
        gCyber = cnDAO.readNetwork(self.communicationsNetworkInputFilePath)
        
        configFileName = "communications_config.txt"
        edgesFileName = "communications_edges.txt"
        layersFileName = "communications_layers.txt"
        nodesFileName = "communications_nodes.txt"
        
        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )
        
        self.assertFalse(os.path.exists(configFilePath))
        self.assertFalse(os.path.exists(edgesFilePath))
        self.assertFalse(os.path.exists(layersFilePath))
        self.assertFalse(os.path.exists(nodesFilePath))

        cnDAO.writeNetwork(outputDirPath)
        self.assertTrue(os.path.exists(configFilePath))
        self.assertTrue(os.path.exists(edgesFilePath))
        self.assertTrue(os.path.exists(layersFilePath))
        self.assertTrue(os.path.exists(nodesFilePath))

"""class TestPCAPNetworkDAO(unittest.TestCase):

    def setUp(self):
        self.pcapFilePath = "data/testing/sample.pcap"
        self.pnDAO = PCAPNetworkDAO(self.pcapFilePath)

    def test_get_network(self):
        G = self.cnDAO.getNetwork()
        self.assertEqual( G.number_of_nodes(), 3)
        self.assertEqual( G.number_of_edges(), 2)
"""

if __name__ == '__main__':
    unittest.main()

    
        
