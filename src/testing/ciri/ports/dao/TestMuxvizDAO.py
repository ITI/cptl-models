"""
Created on April 22, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from ciri.ports.dao.MuxvizDAO import DESMuxvizDAO
import unittest

class TestDESMuxvizDAO(unittest.TestCase):

    self.networkFilePath = "data/everglades/doc/build/network-baseline.extended.json"
    self.desSQLDB = "/Users/gweaver/Desktop/demo.sqlite"

    def test_output_network(self):
        mvDAO = DESMuxvizDAO.create(self.networkFilePath, \
                                        self.desSQLDB)



        
