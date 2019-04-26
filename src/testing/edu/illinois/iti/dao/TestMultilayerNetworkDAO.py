"""
Created on April 25, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from edu.illinois.iti.dao.MultilayerNetworkDAO import JSONMultilayerNetworkDAO, MuxVizMultilayerNetworkDAO
from jsonschema import validate
from networkx.readwrite import json_graph
import json
import networkx as nx
import os 
import unittest

class TestJSONMultilayerNetworkDAO(unittest.TestCase):

    scenarioDirPrefix = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/build/data/everglades/"    
    multilayerNetworkInventoryFilePath = scenarioDirPrefix + "multilayer/multilayer.inventory.json"

    def testReadNetwork(self):
        mnDAO = JSONMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath, self.scenarioDirPrefix)
        self.assertEqual( len(mnDAO.getNetworkNames()), 3)

        gTrans = mnDAO.getNetwork("PEV Southport")
        self.assertEqual( len(gTrans.nodes()), 133 )
        
        gCyber = mnDAO.getNetwork("Crowley")
        self.assertEqual( len(gCyber.nodes()), 7 )
        
        gTransCyber = mnDAO.getNetwork("Interconnect")
        self.assertEqual( len(gTransCyber.nodes()), 5)
        self.assertEqual( len(gTransCyber.edges()), 3 )

    def testMergeNetworks(self):
        networkName1 = "PEV Southport"
        networkName2 = "Crowley"
        icNetworkNames = ["Interconnect"]
 
        mnDAO = JSONMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath, self.scenarioDirPrefix)
        gMultilayer = mnDAO.mergeNetworks(networkName1, networkName2, icNetworkNames)
        self.assertEqual( len(gMultilayer.nodes()), 140 )

class TestMuxVizMultilayerNetworkDAO(unittest.TestCase):
    
    multilayerNetworkFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/build/data/everglades/multilayer/PEV.merged.json"

    def testReadNetworks(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkFilePath)
        self.assertEqual( len(mnDAO.gMulti.nodes()), 140 )
        
    def testGetLayer(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkFilePath)
        self.assertEqual(mnDAO.getLayer(nodeIdx=0), 2)
        self.assertEqual(mnDAO.getLayer(nodeIdx=6), 2)
        self.assertEqual(mnDAO.getLayer(nodeIdx=7), 1)

    def testGetExtendedEdges(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkFilePath)

        edgeList = mnDAO.getExtendedEdges()
        self.assertEqual( len(edgeList), len(mnDAO.gMulti.edges()) )

    def testGetNodes(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkFilePath)

        nodeList = mnDAO.getNodes()
        self.assertEqual( 166, len(mnDAO.gMulti.edges()) )

    def testWriteNetwork(self):
        outputDirPath = "/tmp"
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkFilePath)
        
        configFileName = "PEV Southport,Crowley_config.txt"
        edgesFileName = "PEV Southport,Crowley_edges.txt"
        layersFileName = "PEV Southport,Crowley_layers.txt"
        nodesFileName = "PEV Southport,Crowley_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        #self.assertFalse(os.path.exists(configFilePath))
        #self.assertFalse(os.path.exists(edgesFilePath))
        #self.assertFalse(os.path.exists(layersFilePath))
        #self.assertFalse(os.path.exists(nodesFilePath))

        mnDAO.writeNetwork(outputDirPath)
        self.assertTrue(os.path.exists(configFilePath))
        self.assertTrue(os.path.exists(edgesFilePath))
        self.assertTrue(os.path.exists(layersFilePath))
        self.assertTrue(os.path.exists(nodesFilePath))

if __name__ == '__main__':
    unittest.main()
