#!/Users/gweaver/anaconda3/bin/python
"""
  Copyright (c) 2019, Gabriel A. Weaver
  University of Illinois at Urbana-Champaign
  All Rights Reserved
"""
import ast
import csv
import getopt
import json
import sys

def usage():
    print("networkTranscoder.py -i <inputfile> -o <outputfile>")


class NetworkTranscoder():

    nodeFieldNames = [ "capacity", "cargo_categories", "cost", "extended_time_period",\
                           "extended_time_rate", "holding_time", "id", "latitude",\
                           "longitude", "nbr_containers", "service_time", "storage",\
                           "transportation_methods" ]

    edgeFieldNames = [ "capacity", "cargo_categories", "cost", "extended_time_period",\
                           "extended_time_rate", "latitude", "longitude", "name",\
                           "nbr_containers", "source", "target", "travel_time",\
                           "type", "transportation_methods", "key" ]

    intNodeFieldNames = [ "capacity", "cost", "extended_time_period", \
                              "holding_time", "nbr_containers", "storage" ]
    floatNodeFieldNames = [ "extended_time_rate", "service_time", "latitude", "longitude" ]
    arrayNodeFieldNames = [ "cargo_categories", "transportation_methods" ]

    intEdgeFieldNames = [ "capacity", "cost", "extended_time_period",\
                              "nbr_containers", "key" ]
    floatEdgeFieldNames = [ "extended_time_rate", "travel_time", "latitude", "longitude" ] 
    arrayEdgeFieldNames = [ "cargo_categories", "transportation_methods" ]    

    def csv2json(self, inputFileBase, outputFile):
        nodeInputFileName = ".".join([inputFileBase, "nodes", "csv"])
        edgeInputFileName = ".".join([inputFileBase, "edges", "csv"])
        
        G = {}
        G["directed"] = True
        G["multigraph"] = True
        G["graph"] = {}
        G["nodes"] = []
        G["links"] = []

        # Read in the CSV files
        with open(nodeInputFileName) as nodeInputFile:
            nodeReader = csv.DictReader(nodeInputFile)
            for row in nodeReader:
                for intNodeFieldName in self.intNodeFieldNames:
                    row[intNodeFieldName] = int(float( row[intNodeFieldName] ))
                for floatNodeFieldName in self.floatNodeFieldNames:
                    row[floatNodeFieldName] = float( row[floatNodeFieldName] )
                for arrayNodeFieldName in self.arrayNodeFieldNames:
                    row[arrayNodeFieldName] = ast.literal_eval( row[arrayNodeFieldName] )

                G["nodes"].append(row)
        
        with open(edgeInputFileName) as edgeInputFile:
            edgeReader = csv.DictReader(edgeInputFile)
            for edge in edgeReader:
                for intEdgeFieldName in self.intEdgeFieldNames:
                    edge[intEdgeFieldName] = int(float( edge[intEdgeFieldName]))
                for floatEdgeFieldName in self.floatEdgeFieldNames:
                    edge[floatEdgeFieldName] = float( edge[floatEdgeFieldName] )
                for arrayEdgeFieldName in self.arrayNodeFieldNames:
                    edge[arrayEdgeFieldName] = ast.literal_eval( edge[arrayEdgeFieldName] )

                G["links"].append(edge)
                
        with open(outputFile, 'w') as jsonOutputFile:
            json.dump(G, jsonOutputFile, indent=4)


    def json2csv(self, inputFile, outputFileBase):

        fieldNames = None
        # Read in the JSON file
        with open(inputFile) as jsonData:
            d = json.load(jsonData)
            jsonData.close()
            
        nodeOutputFileName = ".".join([outputFileBase, "nodes", "csv"])
        edgeOutputFileName = ".".join([outputFileBase, "edges", "csv"])

        with open(nodeOutputFileName, 'w') as nodeOutputFile:
            nodeWriter = csv.DictWriter(nodeOutputFile, fieldnames=self.nodeFieldNames,\
                                            quoting=csv.QUOTE_NONNUMERIC)
            nodeWriter.writeheader()
            for node in d["nodes"]:
                nodeWriter.writerow(node)
        
        with open(edgeOutputFileName, 'w') as edgeOutputFile:
            edgeWriter = csv.DictWriter(edgeOutputFile, fieldnames=self.edgeFieldNames,\
                                            quoting=csv.QUOTE_NONNUMERIC)
            edgeWriter.writeheader()
            for edge in d["links"]:
                edgeWriter.writerow(edge)

        
            
def main(argv):
    """
    Transcode the network file from one format into another
    """
    
    direction = argv[0]
    inputFile = argv[1]
    outputFile = argv[2]

    print("input file is ", inputFile)
    print("output file is ", outputFile)

    nc = NetworkTranscoder()
    
    if "json2csv" == direction:
        nc.json2csv(inputFile, outputFile)
    elif "csv2json" == direction:
        nc.csv2json(inputFile, outputFile)
    else:
        raise Exception("Unrecognized Transcoding Function.  Supported functions include 'json2csv', 'csv2json'", direction)

if __name__ == "__main__":
    main(sys.argv[1:])
