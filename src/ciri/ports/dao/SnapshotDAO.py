"""
Copyright (c) 2019, Gabriel A. Weaver
University of Illinois at Urbana-Champaign
All Rights Reserved
"""
from ciri.ports.dao.TransportationNetworkDAO import MuxVizTransportationNetworkDAO
from matplotlib import cm
import collections
import matplotlib
import sqlite3

class reg(object):
    d = None
    def __init__(self, cursor, row):
        self.d = {}
        for (attr, val) in zip((d[0] for d in cursor.description), row):
            self.d[attr] = val

TimelineEntry = collections.namedtuple('TimelineEntry', \
                                           'timeStep labelStep entity layerID nodeID color sizeFactor')
                                            
class SQLiteSnapshotDAO():

    gTrans = None
    snapshotFilePath = None
    timeStep = None

    @staticmethod
    def create(networkFilePath, snapshotFilePath, timeStep):
        tnDAO = MuxVizTransportationNetworkDAO()
        tnDAO.readNetwork(networkFilePath)

        ssDAO = SQLiteSnapshotDAO()
        ssDAO.snapshotFilePath = snapshotFilePath
        ssDAO.gTrans = tnDAO.gTrans

        ssDAO.timeStep = timeStep
        return ssDAO

    def getNodeColor(self, nTEU, entityName):

        # Use graph attributes to compute max and min TEU
        nodeNames = self.gTrans.nodes()
        nodeId = nodeNames.index( entityName )
        nodeDict = self.gTrans.nodes(data=True)[nodeId]
        
        nodeCapacity = nodeDict[1]["capacity"]   # TEU per minute
        maxTEU = nodeCapacity * self.timeStep
        colorPct= nTEU / float(maxTEU)

        rgb = cm.get_cmap("plasma")(colorPct)
        hexStr = matplotlib.colors.rgb2hex(rgb)
        return hexStr.replace("#","").upper()
    
    def getEdgeColor(self, nTEU, entityName):
        # Use graph attributes to compute max and min TEU
        edges = list( filter(lambda x: x[2]["name"] == entityName, self.gTrans.edges(data=True)) )
        if len(edges) > 1:
            print("More than one edge for " + sourceEntityName + ", " + targetEntityName)
        elif len(edges) == 0:
            print("No edge found for " + sourceEntityName + ", " + targetEntityName)

        edgeDict = edges[0]
        edgeCapacity = edgeDict[2]["capacity"] 
        maxTEU = edgeCapacity * self.timeStep

        colorPct= nTEU / float(maxTEU)

        rgb = cm.get_cmap("plasma")(colorPct)
        hexStr = matplotlib.colors.rgb2hex(rgb)
        return hexStr.replace("#","").upper()
        
    def getLayer(self, nodeIdx):
        """
        This code should be refactored, it is ugly
        It is also in MultlayerNetworkDAO
        """
        node = self.gTrans.nodes(data=True)[nodeIdx]
        layerNames = self.gTrans.graph["type"].split(",")

        layerName = None
        if "imn:hostname" in node[1]:
            layerName="Communications"
        else:
            layerName="Transportation"

        layerIdx = layerNames.index(layerName) + 1
        return layerIdx

    
    def writeSnapshot(self, outputFilePath, type):
        
        if "MV_TIMELINE" != type:
            raise Exception("Unrecognized type: " + type)
        
        conn = sqlite3.connect(self.snapshotFilePath)
        c = conn.cursor()

        timelineEntries = []

        nodeNames = list( self.gTrans.nodes() )
        edgeNames = list( map(lambda x: x[2]["name"], self.gTrans.edges(data=True)) )
        for row in c.execute("SELECT * FROM snapshot ORDER BY Time"):
            rowDict = reg(c, row)
            timeStep = int(rowDict.d["Time"] / 120)
            labelStep = "t" + str(timeStep) #rowDict.d["UtcTime"]
            entity = None
            entityId = None
            layerID = None 
            entityID = None
            color = None
            sizeFactor = 3
            
            entityNames = [*rowDict.d][5:]
            for entityName in entityNames:

                # Figure out whether the entity name is a node or edge
                isEdge = (" to " in entityName) or \
                    ("Offload" in entityName) or \
                    ("Onload" in entityName) or \
                    (("Seaway" in entityName) and ("In" in entityName)) or \
                    (("Seaway" in entityName) and ("Out" in entityName))

                if isEdge:
                    entity = "edge"
                    edgeId = edgeNames.index(entityName)
                    edgeEntry = self.gTrans.edges(data=True)[edgeId]
                    
                    srcName = edgeEntry[0]
                    tgtName = edgeEntry[1]
                    srcId = nodeNames.index( srcName )
                    tgtId = nodeNames.index( tgtName )
                    
                    entityId = "-".join([str(srcId + 1), str(tgtId + 1)])
                    layerId = self.getLayer(srcId)  
                    nTEU = rowDict.d[entityName]
                    color = self.getEdgeColor(nTEU, entityName)
                else:
                    entity = "node"
                    nodeId = nodeNames.index( entityName )
                    entityId = str(nodeId + 1)
                    layerId = self.getLayer( nodeId )
                    nTEU = rowDict.d[entityName]
                    color = self.getNodeColor(nTEU, entityName)
                    
                timelineEntry = TimelineEntry( timeStep = timeStep,\
                                                   labelStep = labelStep,\
                                                   entity = entity, \
                                                   layerID = 1, \
                                                   nodeID = entityId, \
                                                   color = color, \
                                                   sizeFactor = sizeFactor )
                timelineEntries.append(timelineEntry)
                
        # Please note that we need to think about edges that span two layers.
        #  I don't think we can animate those#
        with open(outputFilePath, 'w') as outputFile:
            outputFile.write(" ".join(["timeStep", "labelStep", "entity", "layerID", "nodeID", "color", "sizeFactor"]) + "\n" )
            for timelineEntry in timelineEntries:
                timelineEntryValues = "%d %s %s %d %s %s %d" % (timelineEntry.timeStep, \
                                                                    timelineEntry.labelStep, \
                                                                    timelineEntry.entity, \
                                                                    timelineEntry.layerID, \
                                                                    timelineEntry.nodeID, \
                                                                    timelineEntry.color, \
                                                                    timelineEntry.sizeFactor)
                outputFile.write(timelineEntryValues + "\n")
        outputFile.close()
            

