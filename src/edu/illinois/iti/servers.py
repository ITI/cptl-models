from flask import Flask, jsonify, request, Response
import json

class ScenarioServerAction():

    dataDir = None
    
    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        result = self.action()
        return result
    
    def setDataDir(self, dataDir):
        self.dataDir = dataDir
    
    def getIndex(self):
        return Response("Scenario Server", status=200, headers={})

    def getScenarios(self, inventoryFilePath):
        with open(inventoryFilePath) as invFile:
            scenarioInv = json.load(invFile)
        invFile.close()
        return scenarioInv

    def getScenariosWrapper(self):
        invFileName = request.args.get("inv")
        if None == invFileName:
            invFileName = "inventory.json"
        inventoryFilePath = "/".join([self.dataDir, invFileName])
        scenarioInv = self.getScenarios(inventoryFilePath)
        return jsonify(scenarioInv)

    def getScenarioDescription(self, scenarioId):
        scenarioFilePath = "/".join([self.dataDir, scenarioId, "inventory.json"])
        with open(scenarioFilePath) as scenarioFile:
            scenarioDesc = json.load(scenarioFile)
        scenarioFile.close()
        return scenarioDesc
    
    def getScenarioDescriptionWrapper(self, scenarioId):
        scenarioDesc = self.getScenarioDescription(scenarioId)
        return jsonify(scenarioDesc)

    def getNetworkDescription(self, scenarioId, networkId):
        networkFileName = networkId + ".json"
        networkFilePath = "/".join([self.dataDir, scenarioId, "networks", networkFileName])
        with open(networkFilePath) as networkFile:
            networkDesc = json.load(networkFile)
        networkFile.close()
        return networkDesc
    
    def getNetworkDescriptionWrapper(self, scenarioId, networkId):
        networkDesc = self.getNetworkDescription(scenarioId, networkId)
        return jsonify(networkDesc)

    def getFlowArchiveWrapper(self, flowId):
        return Response("Not yet implemented", status=200, headers={})
    
class ScenarioServerWrapper():

    actions = None
    app = None
    dataDir = None
    serverName = None
    serverIP = None
    serverPort = None
    
    @staticmethod
    def create(serverName, serverIP, serverPort, dataDir):
        server = ScenarioServerWrapper()

        server.actions = ScenarioServerAction(action=None)
        server.actions.setDataDir(dataDir)
        server.app = Flask(serverName)
        server.dataDir = dataDir
        server.serverName = serverName
        server.serverIP = serverIP
        server.serverPort = serverPort

        return server

    def start(self, debugOn):
        self.add_endpoint(endpoint="/", endpointName="", handler=self.actions.getIndex)
        self.add_endpoint(endpoint="/cptl/api/v0.1/scenarios", endpointName="getScenarios", handler=self.actions.getScenariosWrapper)
        self.add_endpoint(endpoint="/cptl/api/v0.1/scenarios/<scenarioId>", endpointName="getScenarioDescription", handler=self.actions.getScenarioDescriptionWrapper)
        self.add_endpoint(endpoint="/cptl/api/v0.1/scenarios/<scenarioId>/networks/<networkId>", endpointName="getNetworkDescription", handler=self.actions.getNetworkDescriptionWrapper)
        self.add_endpoint(endpoint="/cptl/api/v0.1/scenarios/<scenarioId>/flows/<flowId>", endpointName="getFlowArchive", handler=self.actions.getFlowArchiveWrapper )
        self.app.run(debug=debugOn)

    def add_endpoint(self, endpoint=None, endpointName=None, handler=None):
        self.app.add_url_rule(endpoint, endpointName, handler)
