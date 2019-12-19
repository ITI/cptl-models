#!/Users/gweaver/anaconda3/bin/python
"""
Created on February 19, 2019

@author:   Gabriel A. Weaver

Copyright (c) 2019 University of Illinois at Urbana Champaign.  All rights reserved.
"""
from ciri.ports.dao.VesselScheduleDAO import CSVVesselScheduleDAO
from datetime import datetime, timedelta, tzinfo
import argparse


def main(args):
    """
    Generate the vessel schedule 
    """
    scheduleInputFilePath = args.input
    scheduleOutputFilePath = args.output
    networkFilePath = args.network
    startTime = args.start_time
    workdayStart = args.workday_start
    workdayEnd = args.workday_end
    
    vesselDAO = CSVVesselScheduleDAO(networkFilePath, startTime, workdayStart, workdayEnd)
    vesselDAO.csv2json(scheduleInputFilePath, scheduleOutputFilePath)

if __name__ == '__main__':
    """
    NB:  This code based on/copied from code done by Andrew @ HSTG 
    """
    parser = argparse.ArgumentParser(description="Generate a vessel schedule from CSV")
    parser.add_argument('-i', '--input', help='Input CSV filename', type=str, default=None, required=True)
    parser.add_argument('-o', '--output', help='Output JSON filename', type=str, default='Schedule.json',
                        required=False)
    parser.add_argument('-n', '--network', help='Network filename, e.g., network.json',
                        type=str, default='network.json', required=False)
    parser.add_argument('-st', '--start_time', help='Simulation start time, e.g., "2018-05-28 00:00:00-04:00"',
                        type=str,
                        default=None, required=False)
    parser.add_argument('-we', '--workday_end', help='Workday end time, e.g., "17:00"',
                        type=str, default='17:00', required=False)
    parser.add_argument('-ws', '--workday_start', help='Workday start time, e.g., "08:00"',
                        type=str, default='08:00', required=False)
    args = parser.parse_args()
    main(args)

