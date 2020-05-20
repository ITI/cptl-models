"""
Created on May 12, 2020

@author Gabriel A. Weaver

Copyright (c) 2019-2020 University of Illinois at Urbana Champaign
All Rights Reserved
"""
import json
import os
import sys

def main(argv):
    routesFilePath = argv[0]
    outputFilePath = argv[1]

    jsonRoutes = None
    with open(routesFilePath) as routesFile:
        jsonRoutes = json.load(routesFile)
    routesFile.close()

    for idx, commodity in enumerate(jsonRoutes["commodities"]):
        path = commodity["path"]
        times = commodity["preferredDepartureTimes"]

        # Get index for all elements with IN.
        inElements = list(filter(lambda i: "::IN" in path[i], range(len(path)) ))
        # Remove those from path, times arrays
        for idx in sorted(inElements, reverse=True):
            del path[idx]
            del times[idx]

        # Replace all OUT with clear
        path = list(map(lambda x: x.replace("::OUT", ""), path))
        commodity["path"] = path
        commodity["preferredDepartureTimes"] = times

    with open(outputFilePath, 'w') as outputFile:
        outputStr = json.dumps(jsonRoutes, indent=4)
        outputFile.write(outputStr)
    outputFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
    
        
        
