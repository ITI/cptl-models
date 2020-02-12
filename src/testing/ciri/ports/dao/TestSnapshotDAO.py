"""
Copyright (c) 2019, Gabriel A. Weaver
University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from ciri.ports.dao.SnapshotDAO import SQLiteSnapshotDAO
import unittest

class TestSnapshotDAO(unittest.TestCase):

    networkFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/build/data/everglades/transportation/network-baseline.extended2.json"
    snapshotFilePath = "/Volumes/Seagate Backup Plus Drive/Work/responseSurface/startDuration-McIntosh N 1-18-3.sqlite"

    def testGetLayer(self):
        ssDAO = SQLiteSnapshotDAO.create(self.networkFilePath, self.snapshotFilePath, 120)
        self.assertEqual(ssDAO.getLayer(nodeIdx=0), 1)
        self.assertEqual(ssDAO.getLayer(nodeIdx=6), 1)
        self.assertEqual(ssDAO.getLayer(nodeIdx=7), 1)

    def testConvertSnapshot(self):
        outputFilePath = "/tmp/infrastructure_timeline.txt"
        ssDAO = SQLiteSnapshotDAO.create(self.networkFilePath, self.snapshotFilePath, 120)
        ssDAO.writeSnapshot(outputFilePath, type="MV_TIMELINE")
        
if __name__ == '__main__':
    unittest.main()
