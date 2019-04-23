"""
Created on March 14, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  
All Rights Reserved
"""
from edu.illinois.iti.dao.CommunicationsNetworkDAO import IMNCommunicationsNetworkDAO
import networkx as nx
import unittest

    

class TestIMNCommunicationsNetworkDAO(unittest.TestCase):

    def setUp(self):
        self.imnFilePath = "data/testing/simple.imn"

        self.cnDAO = IMNCommunicationsNetworkDAO(self.imnFilePath)

    def test_init(self):
        self.assertEqual(self.cnDAO.networkFilePath, self.networkFilePath)

    def test_get_network(self):
        G = self.cnDAO.getNetwork()
        self.assertEqual( G.number_of_nodes(), 3)
        self.assertEqual( G.number_of_edges(), 2)

if __name__ == '__main__':
    unittest.main()

    
        
