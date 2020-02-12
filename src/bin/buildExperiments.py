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

    namePcs = teuArrival["name"].split(":")
    if namePcs[1] == '':
        # cannot prioritize by commodity type if not known
        #print(f"No commodity found {teuArrival['name']}")
        return delayCost
    
    commodityGroup = int(namePcs[1])
    origin = teuArrival["origin"]

    if 1 == prioritization:
        delayCost = 0
    elif 2 == prioritization:
        # Prioritize by $ value per TEU
        if 61 == commodityGroup and "NICARAGUA" == origin:
            delayCost = 10
    elif 3 == prioritization:
        # Prioritize by TEU Volumes
        if 8 == commodityGroup and \
                ("GUATEMALA" == origin or "HONDURAS" == origin):
            delayCost = 10
    else:
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

    # Set the road capacity for McIntosh Gate to McIntosh Intersection
    roads = filter(lambda x: x["rdf:type"] == "Gate-Intersection", graphTemplateData["links"])
    for road in roads:
        road["capacity"] = roadCapacity

    # Set the crane rate for the Cranes
    cranes = filter(lambda x: x["rdf:type"] == "Berth-Dock", graphTemplateData["links"])
    for crane in cranes:
        crane["travel_time"] = round( 60.0 / craneRate, 1 )

    graphOutputPath = "/".join([expDirPath, "networks/transportation.gnsi"])    

    transGraphSchema = None
    with open(transGraphSchemaFilePath) as transGraphSchemaFile:
        transGraphSchema = json.load(transGraphSchemaFile)
    transGraphSchemaFile.close()

    outputJSON(graphTemplateData, transGraphSchema, graphOutputPath)

def createExperimentDir(outputBase, expIdx, expParams):
    dirPath = "/".join([outputBase, expIdx])
    if os.path.isdir(dirPath):
        return dirPath
    
    os.mkdir(dirPath)
    
    expParamsPath = "/".join([dirPath, "exp_params.json"])
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

    return dirPath

def usage():
    print("buildExperiments.py <scenarioBase> <experimentName> <outputBase> <month> <action>")

def main(argv):
    """
    Given an experiment parameters file, generate and run.
    """
    if len(argv) != 5:
        usage()
        sys.exit(-1)

    scenarioBase = argv[0]
    experimentFileName = argv[1]
    outputBase = argv[2]
    month = argv[3]
    action = argv[4]

    graphTemplateFilePath =\
        "/".join([scenarioBase, "networks/transportation.gnsi"])
    scheduleTemplateAllFilePath =\
        "/".join([scenarioBase, f"flows/PEV-FY2018/{month}/schedule.filtered.json"])
    experimentFilePath =\
        "/".join([scenarioBase, f"experiments/{experimentFileName}.txt"])

    transGraphSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/network.schema.v2.json"
    shipmentSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/shipment.schema.v2.json"
    scheduleSchemaFilePath = "/Users/gweaver/Documents/Repositories/ITI/cptl-models/data/schema/schedule.schema.v2.json"

    if "GENERATE" == action:
        os.mkdir(outputBase)
        with open(experimentFilePath) as experimentFile:
            for expIdx, line in enumerate(experimentFile):
                for shipper in ["", "Crowley", "MSC", "King Ocean", "FIT"]:
                    expId = str(expIdx)
                    scheduleTemplateFilePath = scheduleTemplateAllFilePath

                    if "" != shipper:
                        expId = ".".join([str(expIdx), shipper])
                        scheduleTemplateFilePath = scheduleTemplateAllFilePath.replace("schedule.filtered.json", \
                                                                                           f"schedule.filtered.{shipper}.json")

                    linePcs = line.split()
                
                    expParams = {}
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

                    expDirPath = createExperimentDir(outputBase, expId, expParams)
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
