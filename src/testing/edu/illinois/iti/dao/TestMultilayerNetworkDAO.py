"""
Created on April 25, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from jsonschema import validate
from networkx.readwrite import json_graph
import json
import networkx as nx
import os 
import unittest

class TestJSONMultilayerNetworkDAO(unittest.TestCase):
    
    multilayerNetworkInventoryFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/everglades/multilayer/multilayer.inventory.json"

    def testReadNetwork(self):
        mnDAO = JSONMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath)
        self.assertEqual( len(mnDAO.getNetworkNames()), 3)

        gTrans = mnDAO.getNetwork("PEV Southport")
        self.assertEqual( gTrans.number_of_nodes(), 130 )
        
        gCyber = mnDAO.getNetwork("Crowley")
        self.assertEqual( gCyber.number_of_nodes(), 7 )
        
        gTransCyber = mnDAO.getNetwork("Interconnect")
        self.assertEqual( gTransCyber.number_of_nodes(), 0)
        self.assertEqual( gTransCyber.edges(), 3 )

        START HERE





class TestMuxVizMultilayerNetworkDAO(unittest.TestCase):
    
    multilayerNetworkInventoryFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/everglades/multilayer/multilayer.inventory.json"

    def testReadNetworks(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath)
        self.assertEqual( len(mnDAO.gMulti.nodes()), 133 )
        
    def testGetExtendedEdges(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath)

        edgeList = mnDAO.getExtendedEdges()
        self.assertEqual( len(edgeList), len(mnDAO.gMulti.edges()) )

    def testGetNodes(self):
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath)

        nodeList = mnDAO.getNodes()
        self.assertEqual( len(nodeList), len(mnDAO.gMulti.edges()) )

    def testWriteNetwork(self):
        outputDirPath = "/tmp"
        mnDAO = MuxVizMultilayerNetworkDAO.create(self.multilayerNetworkInventoryFilePath)
        
        configFileName = "PEV Multilayer_config.txt"
        edgesFileName = "PEV Multilayer_edges.txt"
        layersFileName = "PEV Multilayer_layers.txt"
        nodesFileName = "PEV Multilayer_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        self.assertFalse(os.path.exists(configFilePath))
        self.assertFalse(os.path.exists(edgesFilePath))
        self.assertFalse(os.path.exists(layersFilePath))
        self.assertFalse(os.path.exists(nodesFilePath))

        mnDAO.writeNetwork(outputDirPath)
        self.assertTrue(os.path.exists(configFilePath))
        self.assertTrue(os.path.exists(edgesFilePath))
        self.assertTrue(os.path.exists(layersFilePath))
        self.assertTrue(os.path.exists(nodesFilePath))

if __name__ == '__main__':
    unittest.main()
