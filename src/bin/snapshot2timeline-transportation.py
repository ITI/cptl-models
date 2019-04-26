"""
Created on April 25, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from ciri.ports.dao.SnapshotDAO import SQLiteSnapshotDAO
import sys

def usage():
    print("snapshot2timeline-transportation.py <networkFilePath> <snapshotFilePath> <timeStep> <muxvizDirPath>")
    sys.exit(-1)

def main(argv):
    networkFilePath = argv[0]
    snapshotFilePath = argv[1]
    timeStep = int(argv[2])
    muxvizDirPath = argv[3]
    
    snapshotPcs = snapshotFilePath.split("/")
    snapshotName = snapshotPcs[ len(snapshotPcs) - 1 ]
    snapshotName = snapshotName.replace(".sqlite", ".timeline.txt")
    outputFilePath = "/".join( [muxvizDirPath, snapshotName] )

    ssDAO = SQLiteSnapshotDAO.create(networkFilePath, snapshotFilePath, timeStep)
    ssDAO.writeSnapshot(outputFilePath, type="MV_TIMELINE")

if __name__ == "__main__":
    main(sys.argv[1:])


