"""
Created on March 14, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  
All Rights Reserved
"""
from pyparsing import *
import json
from networkx.readwrite import json_graph
import networkx as nx
import pyshark

class IMNCommunicationsNetworkDAO():

    """
    Class used to instantiate a Communications network 
      topology from a Core IMN file
    """

    networkFilePath = None

    #-- Grammar for the IMN file

    #---- nodes
    typeBlock = Keyword("type") + Word(alphanums).setResultsName("imn:type")
    modelBlock = Keyword("model") + Word(alphanums)

    interfaceBlock = Keyword("interface") + Word(alphanums) + \
                     SkipTo(MatchFirst(Literal("!"))) + Literal("!")
    hostnameBlock = Keyword("hostname") + Word(alphanums + "-") + Literal("!")
    
    networkConfigContents = hostnameBlock.setResultsName("imn:hostname") | interfaceBlock.setResultsName("imn:interface")
    networkConfigBlock = Keyword("network-config") + Literal("{") + \
                         OneOrMore(networkConfigContents) + Literal("}")
    canvasBlock = Keyword("canvas") + Word(alphanums)
    iconCoordsBlock = Keyword("iconcoords") + Literal("{") + \
                      SkipTo(MatchFirst(Literal("}"))) + Literal("}")
    labelCoordsBlock = Keyword("labelcoords") + Literal("{") + \
                      SkipTo(MatchFirst(Literal("}"))) + Literal("}")

    configBlock = White() + Keyword("config") + Literal("{") + \
                  SkipTo(MatchFirst(Literal("}"))) + Literal("}")                

    customConfigBlock = Keyword("custom-config") + Literal("{") + \
                        SkipTo(MatchFirst(configBlock)) + configBlock + Literal("}")

    servicesBlock = Keyword("services") + Literal("{") + \
                        SkipTo(MatchFirst(Literal("}"))) + Literal("}")
                        
    interfacePeerBlock = Keyword("interface-peer") + Literal("{") + \
                      SkipTo(MatchFirst(Literal("}"))) + Literal("}")

    mirrorBlock = Keyword("mirror") + Word("n" + nums)
    
    nodeContents = typeBlock | modelBlock | networkConfigBlock | \
                   canvasBlock | iconCoordsBlock | labelCoordsBlock | \
                   customConfigBlock | servicesBlock | \
                   interfacePeerBlock | mirrorBlock
    
    nodeName = Word("n" + nums).setResultsName("nodeName")
    nodeStart = Keyword("node") + nodeName + Literal("{") 
    nodeEnd = LineStart() + Literal("}")
    nodeBlock = nodeStart + OneOrMore(nodeContents) + nodeEnd

    #---- links
    colorBlock = Keyword("color") + Word(alphas)
    nodesBlock = Keyword("nodes") + Literal("{") + \
                      SkipTo(MatchFirst(Literal("}"))).setResultsName("imn:LinkNodes") + Literal("}")
    bandwidthBlock = Keyword("bandwidth") + Word(nums)
    linkContents = nodesBlock | bandwidthBlock | colorBlock
    
    linkName = Word("l" + nums).setResultsName("linkName")
    linkStart = Keyword("link") + linkName + Literal("{")
    linkEnd = LineStart() + Literal("}")
    linkBlock = linkStart + OneOrMore(linkContents) + linkEnd
    
    #-- Methods
    @staticmethod
    def create(networkFilePath):
        cnDAO = IMNCommunicationsNetworkDAO()
        cnDAO.networkFilePath = networkFilePath
        return cnDAO

    def getEntityTypes(self):
        entityTypes = []
        entityTypes.append("imn:type")
        entityTypes.append("imn:hostname")
        entityTypes.append("imn:interface")
        entityTypes.append("imn:network-config")
        entityTypes.append("imn:canvas")
        entityTypes.append("imn:iconcoords")
        entityTypes.append("imn:labelcoords")
        entityTypes.append("imn:config")
        entityTypes.append("imn:custom-config")
        entityTypes.append("imn:services")
        entityTypes.append("imn:interface-peer")
        entityTypes.append("imn:mirror")
        entityTypes.append("imn:nodeStart")
        entityTypes.append("imn:node")
        entityTypes.append("imn:nodes")
        entityTypes.append("imn:bandwidth")
        entityTypes.append("imn:link")
        return entityTypes
    
    def getEntityOccurrences(self, networkFileLines, entityType):
        result = None
        if "imn:type" == entityType:
            typeBlocks = self.typeBlock.scanString(networkFileLines)
            result = typeBlocks
        elif "imn:hostname" == entityType:
            hostnameBlocks = self.hostnameBlock.scanString(networkFileLines)
            result = hostnameBlocks
        elif "imn:interface" == entityType:
            interfaceBlocks = self.interfaceBlock.scanString(networkFileLines)
            result = interfaceBlocks
        elif "imn:network-config" == entityType:
            networkConfigBlocks = \
                                  self.networkConfigBlock.scanString(networkFileLines)
            result = networkConfigBlocks
        elif "imn:canvas" == entityType:
            canvasBlocks = \
                           self.canvasBlock.scanString(networkFileLines)
            result = canvasBlocks
        elif "imn:iconcoords" == entityType:
            iconCoordsBlocks = \
                               self.iconCoordsBlock.scanString(networkFileLines)
            result = iconCoordsBlocks
        elif "imn:labelcoords" == entityType:
            labelCoordsBlocks = \
                                self.labelCoordsBlock.scanString(networkFileLines)
            result = labelCoordsBlocks
        elif "imn:config" == entityType:
            configBlocks = \
                           self.configBlock.scanString(networkFileLines)
            result = configBlocks
        elif "imn:custom-config" == entityType:
            customConfigBlocks = \
                                 self.customConfigBlock.scanString(networkFileLines)
            result = customConfigBlocks
        elif "imn:services" == entityType:
            servicesBlocks = \
                             self.servicesBlock.scanString(networkFileLines)
            result = servicesBlocks
        elif "imn:interface-peer" == entityType:
            interfacePeerBlocks = \
                                  self.interfacePeerBlock.scanString(networkFileLines)
            result = interfacePeerBlocks
        elif "imn:mirror" == entityType:
            mirrorBlocks = \
                           self.mirrorBlock.scanString(networkFileLines)
            result = mirrorBlocks
        elif "imn:node" == entityType:
            nodeBlocks = self.nodeBlock.scanString(networkFileLines)
            result = nodeBlocks
        elif "imn:nodeStart" == entityType:
            nodeStartBlocks = self.nodeStart.scanString(networkFileLines)
            result = nodeStartBlocks
        elif "imn:nodes" == entityType:
            nodesBlocks = self.nodesBlock.scanString(networkFileLines)
            result = nodesBlocks
        elif "imn:bandwidth" == entityType:
            bandwidthBlocks = self.bandwidthBlock.scanString(networkFileLines)
            result = bandwidthBlocks
        elif "imn:link" == entityType:
            linkBlocks = self.linkBlock.scanString(networkFileLines)
            result = linkBlocks
            
        return result
        
    def getNetwork(self, networkFilePath):
        G = nx.DiGraph()
        with open(networkFilePath, "r") as networkFile:
            networkFileLines = "".join(networkFile.readlines())
            nodeBlocks = self.getEntityOccurrences(networkFileLines, \
                                                   "imn:node")
            linkBlocks = self.getEntityOccurrences(networkFileLines, \
                                                   "imn:link")
            nIdx = 0
            for node, start, end in nodeBlocks:
                nName = node[1]
                G.add_node(nIdx)
                G.nodes(data=True)[nIdx][1]["name"] = nName

                if "imn:type" in node:
                    G.nodes(data=True)[nIdx][1]["imn:type"] = node["imn:type"]
                if "imn:hostname" in node:
                    G.nodes(data=True)[nIdx][1]["imn:hostname"] = node["imn:hostname"][1]
                if "imn:interface" in node:
                    G.nodes(data=True)[nIdx][1]["imn:interface"] = node["imn:interface"][1]
                nIdx += 1

            nodeNames = list(map(lambda x: x[1]["name"], G.nodes(data=True)))
            for edge, start, end in linkBlocks:
                eName = edge[1]
                linkNodes = edge["imn:LinkNodes"].split()
                sName = linkNodes[0]
                tName = linkNodes[1]

                sIdx = nodeNames.index(sName)
                tIdx = nodeNames.index(tName)
                G.add_edge(sIdx, tIdx, name=eName)
        return G

class MuxVizCommunicationsNetworkDAO():
    """
    Currently a transcoder class to read in a communications
     network and serialize it to a MuxViz network format.
    """
    gCyber = None
    nodeNames = None

    @staticmethod
    def create(networkFilePath):
        cnDAO = MuxVizCommunicationsNetworkDAO()
        
        cnDAO.readNetwork(networkFilePath)
        return cnDAO

    def readNetwork(self, networkFilePath):
        with open(networkFilePath) as networkFile:
            graphData = json.load(networkFile)
        networkFile.close()

        self.nodeNames = list(map(lambda x: x["id"], graphData["nodes"]))
        for edge in graphData["links"]:
            edge["source"] = self.nodeNames.index( edge["source"] )
            edge["target"] = self.nodeNames.index( edge["target"] )
        self.gCyber = json_graph.node_link_graph(graphData)
        
    # Config
    def writeConfig(self, configFilePath, configContents):
        with open(configFilePath, 'w') as configOutFile:
            configOutFile.write(configContents)
        configOutFile.close()

    # Extended Edges
    def getExtendedEdges(self):
        layer = 1
        entries = []

        for edge in self.gCyber.edges_iter(data=True):
            sourceNode = str( self.nodeNames.index( edge[0] ) )
            sourceLayer = str(layer)
            destNode = str( self.nodeNames.index( edge[1] ) )
            destLayer = str(layer)
            
            entry = " ".join([sourceNode, sourceLayer, destNode, destLayer])
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
        content = "2 Cyber"
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
        for node in self.gCyber.nodes_iter(data=True):
            nodeID = str(self.nodeNames.index( node[0] ))
            nodeLabel = str(node[1]["name"])
            #nodeLat = str(node[1]["latitude"])
            #nodeLong = str(node[1]["longitude"])
            nodeEntry = " ".join([nodeID, nodeLabel])
            nodes.append(nodeEntry)
        return nodes
        
    def writeNodes(self, nodesFilePath):
        nodesContent = self.getNodes()
        headers = ["nodeID", "nodeLabel"]
        nodesContent.insert(0, " ".join(headers) )
        with open(nodesFilePath, 'w') as nodesOutFile:
            nodesOutFile.write("\n".join(nodesContent))
        nodesOutFile.close()

    def writeNetwork(self, outputDirPath):
        
        configFileName = "communications_config.txt"
        edgesFileName = "communications_edges.txt"
        layersFileName = "communications_layers.txt"
        nodesFileName = "communications_nodes.txt"

        configFilePath = "/".join( [outputDirPath, configFileName] )
        edgesFilePath = "/".join( [outputDirPath, edgesFileName] )
        layersFilePath = "/".join( [outputDirPath, layersFileName] )
        nodesFilePath = "/".join( [outputDirPath, nodesFileName] )

        # 0. export the non-edge colored network config
        configContents = ";".join( [edgesFilePath, "Cyber", nodesFilePath] )
        self.writeConfig(configFilePath, configContents)

        # 1. export the extended edges list
        self.writeExtendedEdges(edgesFilePath)

        # 2. export the layers information
        self.writeLayers(layersFilePath)

        # 3. export the nodes information
        self.writeNodes(nodesFilePath)
    

    
