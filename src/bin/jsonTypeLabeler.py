"""
Created on March 15, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All Rights Reserved
"""
from networkx.readwrite import json_graph
import csv
import json
import networkx as nx
import sys

def usage():
    print("jsonTypeLabeler.py <networkFilePath> <queueingAttrPath> <outputFilePath>")
    sys.exit(-1)

def getTypeForEdge(edge):
    # Simple rule to determine edge type
    srcNodeName = edge[0]
    tgtNodeName = edge[1]

    srcType = getTypeForNode(srcNodeName)
    tgtType = getTypeForNode(tgtNodeName)

    if srcType == None or tgtType == None:
        result = None
    else:
        result = "-".join([srcType, tgtType])
    
    return result
    
def getTypeForNode(nodeName):
    # simple rule to determine node type
    result = None
    if "Berth" in nodeName:
        result = "Berth"
    elif "Dock" in nodeName:
        result = "Dock"
    elif "Gate" in nodeName:
        result = "Gate"
    elif "Intersection" in nodeName:
        result = "Intersection"
    elif ("MSC" == nodeName) or ("FIT" == nodeName) or\
         ("King Ocean" == nodeName) or ("Crowley" == nodeName):
        result = "TO"
    return result

        
def main(argv):
    networkFilePath = argv[0]
    queueingAttrPath = argv[1]

    # Load the graph
    networkFile = open(networkFilePath,"r")
    networkData = json.load(networkFile)
    gTrans = json_graph.node_link_graph(networkData)

    # Annotate the graph types
    for node in gTrans.nodes(data=True):
        nodeName = node[0]
        node[1]["rdf:type"] = getTypeForNode(nodeName)

    for edge in gTrans.edges(data=True):
        edge[2]["rdf:type"] = getTypeForEdge(edge)
    
    # Apply the parameters to the nodes
    queueingAttrFile = open(queueingAttrPath, "r")
    queueingAttrData = csv.DictReader(queueingAttrFile)

    nodes = gTrans.nodes(data=True)
    edges = gTrans.edges(data=True)
    for row in queueingAttrData:
        type = row["rdf:type"]
        serviceTime = float(row["service_time"])
        holdingTime = float(row["holding_time"])
        storage = int(row["storage"])
        capacity = int(row["capacity"])

        # see if it is a node type or edge type
        nodesList = list(filter(lambda x: x[1]["rdf:type"] == type, nodes))
        for node in nodesList:
            node[1]["service_time"] = float(serviceTime)
            node[1]["holding_time"] = float(holdingTime)
            node[1]["storage"] = int(storage)
            node[1]["capacity"] = int(capacity)

        edgesList = list(filter(lambda x: x[2]["rdf:type"] == type, edges))
        for edge in edgesList:
            edge[2]["travel_time"] = float(serviceTime)
            edge[2]["capacity"] = int(capacity)
            
    networkData = json_graph.node_link_data(gTrans)
    networkStr = json.dumps(networkData, indent=4)
    print(networkStr)
    
if __name__ == "__main__":
    main(sys.argv[1:])
        
    
    

