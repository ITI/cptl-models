"""
Created on March 14, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  
All Rights Reserved
"""
from pyparsing import *
import json
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
    nodesBlock = Keyword("nodes") + Literal("{") + \
                      SkipTo(MatchFirst(Literal("}"))) + Literal("}")
    bandwidthBlock = Keyword("bandwidth") + Word(nums)
    linkContents = nodesBlock | bandwidthBlock
    
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
            for node, start, end in nodeBlocks:
                nName = node[1]
                nId = int(nName[1:])
                G.add_node(nId)
                G.nodes[nId]["name"] = nName

                if "imn:type" in node:
                    G.nodes[nId]["imn:type"] = node["imn:type"]
                if "imn:hostname" in node:
                    G.nodes[nId]["imn:hostname"] = node["imn:hostname"][1]
                if "imn:interface" in node:
                    G.nodes[nId]["imn:interface"] = node["imn:interface"][1]

            for edge, start, end in linkBlocks:
                eName = edge[1]
                sId = int(edge[5].split()[0][1:])
                tId = int(edge[5].split()[1][1:])
                G.add_edge(sId, tId, name=eName)
        return G

