"""
Created on April 17, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from ciri.ports.dao.TransportationNetworkDAO import MuxVizTransportationNetworkDAO
from jsonschema import validate
import json
import os
import unittest

class TestMuxVizTransportationNetworkDAO(unittest.TestCase):
    
    transportationNetworkInputFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/everglades/doc/PEV-May-2017/network-baseline.extended2.json"
    transportationNetworkSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/ciri-maritime-des/data/network.schema.v2.json"

    def testReadTransportationNetwork(self):
        tnDAO = MuxVizTransportationNetworkDAO()
        tnDAO.readNetwork(self.transportationNetworkInputFilePath)
        self.assertEqual( len(tnDAO.gTrans.nodes()), 133)

    def testGetExtendedEdges(self):
        tnDAO = MuxVizTransportationNetworkDAO()
        tnDAO.readNetwork(self.transportationNetworkInputFilePath)

        edgeList = tnDAO.getExtendedEdges()
        self.assertEqual( len(edgeList), len(tnDAO.gTrans.edges()) )

    def testGetNodes(self):
        tnDAO = MuxVizTransportationNetworkDAO()
        tnDAO.readNetwork(self.transportationNetworkInputFilePath)
        
        nodeList = tnDAO.getNodes()
        self.assertEqual( len(nodeList), len(tnDAO.gTrans.nodes()) )
        
    def testWriteNetwork(self):
        outputDirPath = "/tmp"
        tnDAO = MuxVizTransportationNetworkDAO()
        gTrans = tnDAO.readNetwork(self.transportationNetworkInputFilePath)

        configFileName = "transportation_config.txt"
        edgesFileName = "transportation_edges.txt"
        layersFileName = "transportation_layers.txt"
        nodesFileName = "transportation_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        self.assertFalse(os.path.exists(configFilePath))
        self.assertFalse(os.path.exists(edgesFilePath))
        self.assertFalse(os.path.exists(layersFilePath))
        self.assertFalse(os.path.exists(nodesFilePath))

        tnDAO.writeNetwork(outputDirPath)
        self.assertTrue(os.path.exists(configFilePath))
        self.assertTrue(os.path.exists(edgesFilePath))
        self.assertTrue(os.path.exists(layersFilePath))
        self.assertTrue(os.path.exists(nodesFilePath))

if __name__ == '__main__':
    unittest.main()
        


