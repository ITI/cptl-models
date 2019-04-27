"""
Created on April 26, 2019

@author:  Gabriel A. Weaver

Copyright (c) 2019 Unveristy of Illinois at Urbana Champaign
All rights reserved
"""
from networkx.readwrite import json_graph
import csv
import json
import networkx as nx

class JSONMultilayerNetworkDAO():
    """
    Class used to instantiate a multilayer network from several
      node-link JSON files
    """

    networkName = None
    networkInventory = None

    @staticmethod
    def create(multilayerNetworkInventoryFilePath, scenarioDirPrefix):
        mnDAO = JSONMultilayerNetworkDAO()

        with open(multilayerNetworkInventoryFilePath) as invFile:
            invData = json.load(invFile)
        invFile.close()

        mnDAO.networkName = invData["name"]
        mnDAO.networkInventory = {}

        for networkDict in invData["networks"]:
            networkName = networkDict["name"]
            networkType = networkDict["type"]
            schemaFilePath = scenarioDirPrefix + networkDict["schema"]
            networkFilePath = scenarioDirPrefix + networkDict["network"]

            with open(networkFilePath) as networkFile:
                graphData = json.load(networkFile)
            networkFile.close()

            nodeNames = list(map(lambda x: x["id"], graphData["nodes"]))
            for edge in graphData["links"]:
                edge["source"] = nodeNames.index( edge["source"] )
                edge["target"] = nodeNames.index( edge["target"] )
            G = json_graph.node_link_graph(graphData)

            G.graph["name"] = networkName
            G.graph["type"] = networkType
            mnDAO.networkInventory[networkName] = G

        return mnDAO
    
    def getNetworkNames(self):
        return self.networkInventory.keys()

    def getNetwork(self, networkName):
        if not (networkName in self.networkInventory):
            raise Exception("Key not found in inventory: " + networkName)
        return self.networkInventory[networkName]

    def mergeNetworks(self, network1Name, network2Name, icNetworkNames):
        """
        Given two networks, merge them using the interconnect network.
        """
        graph1 = self.networkInventory[network1Name]
        graph2 = self.networkInventory[network2Name]
        
        
        F = nx.compose(graph1, graph2)
        F.graph["name"] = ",".join( [graph1.graph["name"], graph2.graph["name"]] )
        F.graph["type"] = ",".join( [graph1.graph["type"], graph2.graph["type"]] )

        # now want to add in edges
        for icNetworkName in icNetworkNames:
            graphI = self.networkInventory[icNetworkName]
            for edge in graphI.edges_iter(data=True):
                sourceId = edge[0]
                targetId = edge[1]
                F.add_edge( sourceId, targetId, attr_dict=edge[2] )
        return F
            
    def writeNetwork(self, G, outputFilePath):
        # Convert graph to string identifiers
        gData = json_graph.node_link_data(G)

        nodeNames = list( map(lambda x: x[0], G.nodes(data=True)) )
        for edge in gData["links"]:
            sIdx = edge["source"]
            tIdx = edge["target"]
            
            sName = nodeNames[sIdx]
            tName = nodeNames[tIdx]
            edge["source"] = sName
            edge["target"] = tName
        gStr = json.dumps(gData, indent=4)
        with open(outputFilePath, 'w') as outputFile:
            outputFile.write(gStr)
        outputFile.close()
        return

class MuxVizMultilayerNetworkDAO():
    """
    Currently a transcoder class to read in a multilayer network 
      and serialize it to a MuxViz network format.
    """
    gMulti = None
    nodeNames = None

    @staticmethod
    def create(networkFilePath):
        mnDAO = MuxVizMultilayerNetworkDAO()
        mnDAO.readNetwork(networkFilePath)
        return mnDAO

    def readNetwork(self, networkFilePath):
        with open(networkFilePath) as networkFile:
            graphData = json.load(networkFile)
        networkFile.close()

        self.nodeNames = list(map(lambda x: x["id"], graphData["nodes"]))
        for edge in graphData["links"]:
            edge["source"] = self.nodeNames.index( edge["source"] )
            edge["target"] = self.nodeNames.index( edge["target"] )
        self.gMulti = json_graph.node_link_graph(graphData)
        
    # Config
    def writeConfig(self, configFilePath, configContents):
        with open(configFilePath, 'w') as configOutFile:
            configOutFile.write(configContents)
        configOutFile.close()

    def getLayer(self, nodeIdx):
        """
        This code should be refactored
        """
        node = self.gMulti.nodes(data=True)[nodeIdx]
        layerNames = self.gMulti.graph["type"].split(",")

        layerName = None
        if "imn:hostname" in node[1]:
            layerName="Communications"
        else:
            layerName="Transportation"

        layerIdx = layerNames.index(layerName) + 1
        return layerIdx

    # Extended Edges
    def getExtendedEdges(self):
        entries = []

        edgeWeight = "1"
        for edge in self.gMulti.edges_iter(data=True):
            sourceNode = self.nodeNames.index( edge[0] ) 
            sourceLayer = self.getLayer(sourceNode)
            destNode = self.nodeNames.index( edge[1] ) 
            destLayer = self.getLayer(destNode)
            
            entry = " ".join([str(sourceNode + 1), str(sourceLayer), str(destNode + 1), str(destLayer), edgeWeight])
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
        layerNames = self.gMulti.graph["name"].split(",")
        content = []
        for idx, layerName in enumerate(layerNames):
            layerName = layerName.replace(" ", "_")
            content.append(" ".join([ str(idx + 1), layerName]))

        layersContent.append(header)
        layersContent.append("\n".join(content))
        return layersContent
    
    def writeLayers(self, layersFilePath):
        layersContent = self.getLayers()
        with open(layersFilePath, 'w') as layersOutFile:
            layersOutFile.write("\n".join(layersContent))
        layersOutFile.close()

    # Nodes
    def getNodes(self):
        nodes = []
        for node in self.gMulti.nodes_iter(data=True):
            nodeID = str(self.nodeNames.index( node[0] ) + 1)
            nodeLabel = node[0].replace(" ", "_")
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
        
        graphName = self.gMulti.graph["name"]
        configFileName = graphName + "_config.txt"
        edgesFileName = graphName + "_edges.txt"
        layersFileName = graphName + "_layers.txt"
        nodesFileName = graphName + "_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        # 0. export the non-edge colored network config
        configContents = ";".join( [edgesFilePath, layersFilePath, nodesFilePath] )
        self.writeConfig(configFilePath, configContents)

        # 1. export the extended edges list
        self.writeExtendedEdges(edgesFilePath)

        # 2. export the layers information
        self.writeLayers(layersFilePath)

        # 3. export the nodes information
        self.writeNodes(nodesFilePath)
    

