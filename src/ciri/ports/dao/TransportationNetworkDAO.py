"""
Created on April 17, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign
All rights reserved
"""
from jsonschema import validate
from networkx.readwrite import json_graph
import json
import networkx as nx

class MuxVizTransportationNetworkDAO():
    """
    Currently a transcoder class to read in a transportation 
      network and serialize it to a MuxViz network format.
    """
    gTrans = None
    nodeNames = None

    @staticmethod
    def create(networkFilePath):
        tnDAO = MuxVizTransportationNetworkDAO()
        
        tnDAO.readNetwork(networkFilePath)
        return tnDAO

    def readNetwork(self, networkFilePath):
        with open(networkFilePath) as networkFile:
            graphData = json.load(networkFile)
        networkFile.close()

        self.nodeNames = list(map(lambda x: x["id"], graphData["nodes"]))
        for edge in graphData["links"]:
            edge["source"] = self.nodeNames.index( edge["source"] )
            edge["target"] = self.nodeNames.index( edge["target"] )
        self.gTrans = json_graph.node_link_graph(graphData)
        
    # Config
    def writeConfig(self, configFilePath, configContents):
        with open(configFilePath, 'w') as configOutFile:
            configOutFile.write(configContents)
        configOutFile.close()

    # Extended Edges
    def getExtendedEdges(self):
        layer = 1
        entries = []

        edgeWeight = "1"
        for edge in self.gTrans.edges_iter(data=True):
            sourceNode = str( self.nodeNames.index( edge[0] ) + 1 )
            sourceLayer = str(layer)
            destNode = str( self.nodeNames.index( edge[1] )  + 1)
            destLayer = str(layer)
            
            entry = " ".join([sourceNode, sourceLayer, destNode, destLayer, edgeWeight])
            entries.append(entry)
        return entries

    def writeExtendedEdges(self, edgesFilePath):
        entries = self.getExtendedEdges()
        with open(edgesFilePath, 'w') as edgesOutFile:
            edgesOutFile.write("\n".join(entries))
        edgesOutFile.close()
        
    # Layers
    def getLayers(self):
        layersContent = []
        header = "layerID layerLabel"
        content = "1 Transportation"
        layersContent.append(header)
        layersContent.append(content)
        return layersContent
    
    def writeLayers(self, layersFilePath):
        layersContent = self.getLayers()
        with open(layersFilePath, 'w') as layersOutFile:
            layersOutFile.write("\n".join(layersContent))
        layersOutFile.close()

    # Nodes
    def getNodes(self):
        nodes = []
        for node in self.gTrans.nodes_iter(data=True):
            nodeID = str(self.nodeNames.index( node[0] ) + 1)
            nodeLabel = node[0].replace(" ","_")
            nodeLat = str(node[1]["latitude"])
            nodeLong = str(node[1]["longitude"])
            nodeEntry = " ".join([nodeID, nodeLabel, nodeLat, nodeLong])
            nodes.append(nodeEntry)
        return nodes
        
    def writeNodes(self, nodesFilePath):
        nodesContent = self.getNodes()
        headers = ["nodeID", "nodeLabel", "nodeLat", "nodeLong"]
        nodesContent.insert(0, " ".join(headers) )
        with open(nodesFilePath, 'w') as nodesOutFile:
            nodesOutFile.write("\n".join(nodesContent))
        nodesOutFile.close()

    def writeNetwork(self, outputDirPath):
        
        configFileName = "transportation_config.txt"
        edgesFileName = "transportation_edges.txt"
        layersFileName = "transportation_layers.txt"
        nodesFileName = "transportation_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        # 0. export the non-edge colored network config
        configContents = ";".join( [edgesFilePath, "Transportation", nodesFilePath] )
        self.writeConfig(configFilePath, configContents)

        # 1. export the extended edges list
        self.writeExtendedEdges(edgesFilePath)

        # 2. export the layers information
        self.writeLayers(layersFilePath)

        # 3. export the nodes information
        self.writeNodes(nodesFilePath)
    
