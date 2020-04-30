"""
Created on January 6, 2020

@author Gabriel A. Weaver

Copyright (c) 2020 University of Illinois at Urbana-Champaign.
All rights reserved
"""
from jsonschema import validate
import json
import os
import os.path
import shutil
import sys

def setDelayCost(teuArrival, prioritization):
    """
    Set the delay cost based on a prioritization function
    - for now, prioritize based on a few options
    """
    delayCost = 0

    if '' == teuArrival["commodityGroup"]:
        return delayCost
    
    commodityGroup = int(teuArrival["commodityGroup"])
    origin = teuArrival["origin"]

    if 1 == prioritization:
        delayCost = 0
    elif 2 == prioritization:
        # Prioritize by $ value per TEU
        if 61 == commodityGroup: # and "NICARAGUA" == origin:
            delayCost = 10
    elif 3 == prioritization:
        # Prioritize by TEU Volumes
        if 8 == commodityGroup:
            # and ("GUATEMALA" == origin or "HONDURAS" == origin):
            delayCost = 10
    elif 4 == prioritization:
        # Prioritize by Customs Value
        if 85 == commodityGroup and \
                ("DOMINICAN REPUBLIC" == origin):
            delayCost = 10
    return delayCost

def outputJSON(data, schemaData, outputPath):
    validate(data, schemaData)
    with open(outputPath, 'w') as outputFile:
        jsonData = json.dumps(data, indent=4)
        outputFile.write(jsonData)
    outputFile.close()

def createScheduleAndShipments(expDirPath, expFlowsParams):
    scheduleTemplateFilePath = expFlowsParams["scheduleTemplateFilePath"]
    scheduleSchemaFilePath = expFlowsParams["scheduleSchemaFilePath"]
    shipmentSchemaFilePath = expFlowsParams["shipmentSchemaFilePath"]

    scheduleTemplateData = None
    with open(scheduleTemplateFilePath) as scheduleTemplateFile:
        scheduleTemplateData = json.load(scheduleTemplateFile)
    scheduleTemplateFile.close()

    prioritization = expFlowsParams["prioritization"]
    ldtDays = expFlowsParams["ldt.days"]
    ldtMins = ldtDays * 1440
    simDuration = expFlowsParams["simDuration.weeks"]
    
    simEnd = round(simDuration * 7 * 1440)  # last minute of simulation
    arrivalsInInterval = filter(lambda x: x["time"] <= simEnd, scheduleTemplateData["shipments"])
    scheduleData = { "shipments": list(arrivalsInInterval) }
    scheduleData["disruptions"] = scheduleTemplateData["disruptions"]
    scheduleData["network"] = scheduleTemplateData["network"].replace("../../../", "../")
    scheduleData["start_time"] = scheduleTemplateData["start_time"]
    scheduleData["workday_end"] = scheduleTemplateData["workday_end"]
    scheduleData["workday_start"] = scheduleTemplateData["workday_start"]

    scheduleOutputPath = "/".join([expDirPath, "flows/schedule.json"])
    scheduleSchema = None
    with open(scheduleSchemaFilePath) as scheduleSchemaFile:
        scheduleSchema = json.load(scheduleSchemaFile)
    scheduleSchemaFile.close()

    # Validate and output shipments
    for vesselArrivalData in scheduleData["shipments"]:
        shipmentFile = vesselArrivalData["shipment_file"]
        parentDir = os.path.dirname(scheduleTemplateFilePath)
        shipmentFilePath = "/".join([parentDir, shipmentFile])
        shipmentData = None

        if not os.path.isfile(shipmentFilePath):
            print(f"File not found: {shipmentFilePath}")
            continue
        else:
            with open(shipmentFilePath) as shipmentFile:
                shipmentData = json.load(shipmentFile)
            shipmentFile.close()

        # set the LDT and the delay costs appropriately
        for teuArrival in shipmentData["commodities"]:
            teuArrival["LDT"] = teuArrival["EAT"] + ldtMins
            teuArrival["delay_cost"] = setDelayCost(teuArrival, prioritization)
        
        shipmentFileName = shipmentFilePath.split("/")[-1]
        shipmentOutputPath = "/".join([expDirPath, "flows/shipments", shipmentFileName])
        shipmentSchema = None
        with open(shipmentSchemaFilePath) as shipmentSchemaFile:
            shipmentSchema = json.load(shipmentSchemaFile)
        shipmentSchemaFile.close()
        outputJSON(shipmentData, shipmentSchema, shipmentOutputPath)
        
        # 2.  Update the schedule data with the generated output path
        #   we have to wait until after we do this as the template passes in
        #   the correct filepath
        for vesselArrival in scheduleData["shipments"]:
            fileName = vesselArrival["shipment_file"].split("/")[1]
            vesselArrival["shipment_file"] = "/".join(["shipments", fileName])
        outputJSON(scheduleData, scheduleSchema, scheduleOutputPath)    

def createTransportationGraph(expDirPath, expGraphParams):
    """
    in reality, we want to have a better reference convention for
      the graph params, but we this will do for now
    """
    graphTemplateFilePath = expGraphParams["templateFilePath"]
    transGraphSchemaFilePath = expGraphParams["schemaFilePath"]
    graphTemplateData = None
    with open(graphTemplateFilePath) as graphTemplateFile:
        graphTemplateData = json.load(graphTemplateFile)
    graphTemplateFile.close()

    dwellTime = expGraphParams["dwellTime.days"]
    gateServiceTime = expGraphParams["gateServiceTime.mins"]
    roadCapacity = expGraphParams["roadCapacity.teu"]
    craneRate = expGraphParams["craneRate.teu-hr"]

    # Pull out the container yards to set dwell time
    containerYards = filter(lambda x: x["rdf:type"] == "TO", graphTemplateData["nodes"])
    for containerYard in containerYards:
        containerYard["holding_time"] = round(dwellTime * 1440)
    
    # Pull out the gate service time to set 
    gates = filter(lambda x: x["rdf:type"] == "Gate", graphTemplateData["nodes"])
    for gate in gates:
        gate["service_time"] = gateServiceTime
        gate["cycle_time"] = round(float(gate["capacity"]) / gate["service_time"])
        
    # Set the road capacity for McIntosh Gate to McIntosh Intersection
    roads = filter(lambda x: x["rdf:type"] == "Gate-Intersection", graphTemplateData["links"])
    for road in roads:
        road["capacity"] = roadCapacity
        road["cycle_time"] = round(float(road["capacity"]) / road["travel_time"])
                                   
    # Set the crane rate for the Cranes
    cranes = filter(lambda x: x["rdf:type"] == "Berth-Dock", graphTemplateData["links"])
    for crane in cranes:
        crane["travel_time"] = round( 60.0 / craneRate, 1 )
        crane["cycle_time"] = round(float(crane["capacity"]) / crane["travel_time"])
                                   
    graphOutputPath = "/".join([expDirPath, "networks/transportation.gnsi"])    

    transGraphSchema = None
    with open(transGraphSchemaFilePath) as transGraphSchemaFile:
        transGraphSchema = json.load(transGraphSchemaFile)
    transGraphSchemaFile.close()

    outputJSON(graphTemplateData, transGraphSchema, graphOutputPath)

def getExperimentUrn(scenarioRef, experimentName, expIdx):
    experimentUrn = "urn:cite:" + scenarioRef.replace("-",":")
    experimentUrn = experimentUrn + "_" + experimentName + str(expIdx)
    return experimentUrn
    
def createExperimentDir(scenarioBase, outputBase, experimentName, scenarioRef, expIdx, expParams):
    expUrn = getExperimentUrn(scenarioRef, experimentName, expIdx)
    experimentDirName = expUrn.replace("urn:cite:", "").replace(":","-")
    dirPath = "/".join([outputBase, experimentDirName])

    if os.path.isdir(dirPath):
        return dirPath
    
    os.mkdir(dirPath)
    
    dirNames = ["config", "data"]
    for dirName in dirNames:
        srcDataPath = "/".join([scenarioBase, scenarioRef, dirName])
        destDataPath = "/".join([dirPath, dirName])
        shutil.copytree(srcDataPath, destDataPath)

        # Update DES I/O entries in inventory
        if "config" == dirName:
            inventoryFilePath = "/".join([destDataPath, "inventory.json"])
            jsonData = None
            with open(inventoryFilePath, 'r') as inventoryFile:
                jsonData = json.load(inventoryFile)
            inventoryFile.close()

            modifiedScenarioRef = scenarioRef
            scenarioUrn = "urn:cite:" + modifiedScenarioRef.replace("-",":")

            inventoryKeys = jsonData.keys()
            newData = {}
            delKeys = []
            for key in inventoryKeys:
                if scenarioUrn in key:
                    newKey = key.replace(scenarioUrn, expUrn)
                    newData[newKey] = jsonData[key]
                    delKeys.append(key)
            jsonData.update(newData)
            for key in delKeys:
                del jsonData[key]
            
            with open(inventoryFilePath, 'w') as inventoryFile:
                jsonDataStr = json.dumps(jsonData, indent=4)
                inventoryFile.write(jsonDataStr)
            inventoryFile.close()
        
    expParamsPath = "/".join([dirPath, "config/exp_params.json"])
    with open(expParamsPath, 'w') as expParamsFile:
        jsonData = json.dumps(expParams, indent=4)
        expParamsFile.write(jsonData)
    expParamsFile.close()
        
    # ./networks
    networkPath = "/".join([dirPath, "networks"])
    os.mkdir(networkPath)
    
    # ./flows
    flowsPath = "/".join([dirPath, "flows"])
    os.mkdir(flowsPath)

    # ./flows/shipments
    shipmentsPath = "/".join([flowsPath, "shipments"])
    os.mkdir(shipmentsPath)

    # ./results
    resultsPath = "/".join([dirPath, "results"])
    os.mkdir(resultsPath)
    
    return dirPath

def usage():
    print("buildExperiments.py <scenarioBase> <scenarioRef> <experimentName> <outputBase> <month> <action>")

def main(argv):
    """
    Given an experiment parameters file, generate and run.
    """
    if len(argv) != 6:
        usage()
        sys.exit(-1)

    scenarioBase = argv[0]
    scenarioRef = argv[1]
    experimentFileName = argv[2]
    outputBase = argv[3]
    month = argv[4]
    action = argv[5]

    graphTemplateFilePath =\
        "/".join([scenarioBase, scenarioRef, "networks/transportation.gnsi"])
    scheduleTemplateAllFilePath =\
        "/".join([scenarioBase, scenarioRef, f"flows/schedule.json"])
    experimentFilePath =\
        "/".join([scenarioBase, scenarioRef, f"data/experiments/{experimentFileName}.txt"])

    transGraphSchemaFilePath = "/home/share/Code/cptl-models/data/schema/network.schema.v2.json"
    shipmentSchemaFilePath = "/home/share/Code/cptl-models/data/schema/shipment.schema.v2.json"
    scheduleSchemaFilePath = "/home/share/Code/cptl-models/data/schema/schedule.schema.v2.json"

    if "GENERATE" == action:
        #        os.mkdir(outputBase)
        with open(experimentFilePath) as experimentFile:
            for expIdx, line in enumerate(experimentFile):
                for shipper in ["", "Crowley", "MSC", "King Ocean", "FIT"]:
                    expId = str(expIdx)
                    scheduleTemplateFilePath = scheduleTemplateAllFilePath

                    if "" != shipper:
                        expId = ".".join([str(expIdx), shipper])
                        scheduleTemplateFilePath = scheduleTemplateAllFilePath.replace("schedule.json", \
                                                                                           f"schedule.{shipper}.json")

                    linePcs = line.split()
                
                    expParams = {}
                    expParams["ref"] = "_".join([scenarioRef, f"{experimentFileName}_{expId}"])
                    expParams["graph.transportation"] = {}
                    expParams["flows"] = {}
                
                    expParams["graph.transportation"]["dwellTime.days"] = float(linePcs[0])
                    expParams["graph.transportation"]["gateServiceTime.mins"] = int(linePcs[1])
                    expParams["graph.transportation"]["roadCapacity.teu"] = int(linePcs[2])
                    expParams["graph.transportation"]["craneRate.teu-hr"] = int(linePcs[3])
                    expParams["graph.transportation"]["templateFilePath"] = graphTemplateFilePath
                    expParams["graph.transportation"]["schemaFilePath"] = transGraphSchemaFilePath
                
                    expParams["flows"]["prioritization"] = int(linePcs[4])
                    expParams["flows"]["ldt.days"] = int(linePcs[6])
                    expParams["flows"]["scheduleTemplateFilePath"] = scheduleTemplateFilePath
                    expParams["flows"]["scheduleSchemaFilePath"] = scheduleSchemaFilePath
                    expParams["flows"]["shipmentSchemaFilePath"] = shipmentSchemaFilePath
                    expParams["flows"]["simDuration.weeks"] = int(linePcs[5])

                    expDirPath = createExperimentDir(scenarioBase, outputBase, experimentFileName, scenarioRef, expId, expParams)
                    createTransportationGraph(expDirPath, expParams["graph.transportation"])
                    createScheduleAndShipments(expDirPath, expParams["flows"])
                    
    elif "RUN" == action:
        # 2.  Run the experiments with different parameters
        pass
    elif "CLEAN" == action:
        # 3.  Clean up the experiments
        shutil.rmtree(outputBase)

if __name__ == "__main__":
    main(sys.argv[1:])
