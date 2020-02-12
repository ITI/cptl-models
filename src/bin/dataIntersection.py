"""
Created on December 13, 2019

@author Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.
All rights reserved
"""
from ciri.ports.dao.VesselArrivalDAO import VesselScheduleVesselArrivalEventDAO, VesselCommoditiesVesselArrivalEventDAO, VesselArrivalEventFusionDAO
import numpy as np
import sys

def getFusionResultForMonth(monthLabel, scheduleInputFilePath, commoditiesInputFilePath):
    vesselDAO = VesselArrivalEventFusionDAO.create(scheduleInputFilePath, commoditiesInputFilePath)
    
    scheduleVesselArrivalEvents = vesselDAO.scheduleVesselArrivalEventDAO.vesselArrivalEvents
    commoditiesVesselArrivalEvents = vesselDAO.commoditiesVesselArrivalEventDAO.vesselArrivalEvents

    dayEpsilon = 0
    fusionMethod = "SHIP_DATE"
    
    vesselDAO.matchedScheduleVesselArrivalEvents = np.zeros( len(scheduleVesselArrivalEvents) )
    vesselDAO.matchedCommoditiesVesselArrivalEvents = np.zeros( len(commoditiesVesselArrivalEvents) )
    vesselDAO.fuseVesselArrivalEvents(scheduleVesselArrivalEvents,\
                                          commoditiesVesselArrivalEvents,\
                                          dayEpsilon,\
                                          fusionMethod)

    unmatchedScheduleVesselArrivalEvents = vesselDAO.getUnmatchedVesselArrivalEvents("VesselSchedule")
    unmatchedCommoditiesVesselArrivalEvents = vesselDAO.getUnmatchedVesselArrivalEvents("Commodities")

    setName = "intersection"
    dfIntersection = vesselDAO.convertToPandasDataframe(setName)
    
    setName = "unmatched_schedule"
    dfUnmatchedVessels = vesselDAO.convertToPandasDataframe(setName)
    dfUnmatchedVessels = dfUnmatchedVessels[ dfUnmatchedVessels["cargoType"] == "CONTAINER" ]
    
    setName = "unmatched_commodities"
    dfUnmatchedCommodities = vesselDAO.convertToPandasDataframe(setName)

    numUnmatchedVesselsDf = dfUnmatchedVessels.shape[0]
    numUnmatchedVesselsEvents = len(list(filter(lambda x: x.cargoType == "CONTAINER", unmatchedScheduleVesselArrivalEvents)))
    try:
        assert( numUnmatchedVesselsDf == numUnmatchedVesselsEvents )
    except:
        print(f"{numUnmatchedVesselsDf} vs {numUnmatchedVesselsEvents}")
    
    pctUnmatchedScheduleVessels = dfUnmatchedVessels.shape[0] / float(len(scheduleVesselArrivalEvents))
    pctUnmatchedScheduleVessels = round(pctUnmatchedScheduleVessels, 2)

    assert( dfUnmatchedCommodities.shape[0] == len(unmatchedCommoditiesVesselArrivalEvents) )
    pctUnmatchedCommodsVessels = dfUnmatchedCommodities.shape[0] / float(len(commoditiesVesselArrivalEvents))
    pctUnmatchedCommodsVessels = round(pctUnmatchedCommodsVessels, 2)

    pctUnmatchedCommodsTEU = getTEU(unmatchedCommoditiesVesselArrivalEvents) / float(getTEU(commoditiesVesselArrivalEvents))
    pctUnmatchedCommodsTEU = round(pctUnmatchedCommodsTEU, 2)

    result = f"{monthLabel}\t{dfIntersection.shape[0]}\t{dfUnmatchedVessels.shape[0]}\t{dfUnmatchedCommodities.shape[0]}\t{pctUnmatchedScheduleVessels}\t{pctUnmatchedCommodsVessels}\t{pctUnmatchedCommodsTEU}"
    return result

def getTEU(vesselArrivalEvents):
    """
    This assumes that there are TEU counts in the vesselArrivalEvents
    """
    result = 0
    for va in vesselArrivalEvents:
        for commodityGroup in va.commodityTEU.keys():
            result += float(va.commodityTEU[commodityGroup][2])

    return result
    

def main(argv):
    scenarioBase = argv[0]
    outFilePath = argv[1]

    results = []
    results.append("\t".join(['monthLabel','intersection','unmatchedVessels','unmatchedCommods', '% unmatchedVessels', '% unmatchedCommmods']))
    for month in list(range(10,13)) + list(range(1,10)):
        print(month)
        monthLabel = month
        scheduleInputFilePath = "/".join([scenarioBase, "data/PEV-FY2018", f"{month}/VesselCalls.csv"])
        commoditiesInputFilePath = "/".join([scenarioBase, "data/PEV-FY2018", f"{month}/ImportedCommods.csv"])
        result = getFusionResultForMonth(monthLabel, scheduleInputFilePath, commoditiesInputFilePath)
        results.append(result)
        
    results.append("\n")
    with open(outFilePath, 'w') as outFile:
        outFile.write("\n".join(results))
    outFile.close()
    
if __name__ == "__main__":
    main(sys.argv[1:])

