"""
Created on July 25, 2020

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
import re
import sys

def usage():
    print("configMaker.py <template> <maxId> <outDir> <expName>")
    
def main(argv):
    if len(argv) != 4:
        usage()
        sys.exit(-1)
        
    templateFilePath = argv[0]
    maxId = int(argv[1])
    outputDirPath = argv[2]
    experimentName = argv[3]

    templateFile = open(templateFilePath, 'r')
    lines = templateFile.readlines()

    for expId in range(0,maxId+1):
        resultBuffer = []
        for line in lines:
            line = line.rstrip()
            if "export SCENARIO_REF" in line:
                searchRegex = f"{experimentName}\d+"
                replacement = f"{experimentName}{expId}"
                # hack of a line
                newLine = re.sub(f"nolhDisruptedBig\d+", f"{experimentName}{expId}",line)
                resultBuffer.append(newLine)
            else:
                resultBuffer.append(line)

        result = "\n".join(resultBuffer)
        outConfigPath = f"{outputDirPath}/exp{expId}.txt"
        with open(outConfigPath, 'w') as outConfigFile:
            outConfigFile.write(result)
            outConfigFile.close()

    
if __name__ == "__main__":
    main(sys.argv[1:])
    
