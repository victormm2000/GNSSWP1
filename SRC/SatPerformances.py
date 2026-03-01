#!/usr/bin/env python

########################################################################
# SatPerformances.py:
# This function is the Main Function of SAT Module
#
#  Project:        SBPT
#  File:           SatPerformances.py
#  Date(YY/MM/DD): 20/07/11
#
#   Author: GNSS Academy
#   Copyright 2020 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
# Usage:
# i.e: SatPerformances.py $SCEN_PATH
# 
# Internal dependencies:
#   SatFunctions.py
#   COMMON
########################################################################


# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
import sys, os
from collections import OrderedDict
from yaml import dump
from SatFunctions import computeSatStats
from COMMON.Dates import convertYearMonthDay2JulianDay
from COMMON.Dates import convertJulianDay2YearMonthDay
from COMMON.Dates import convertYearMonthDay2Doy
from interfaces import SATSTAT_IDX
import SatFunctions
from pandas import read_csv
#----------------------------------------------------------------------
# INTERNAL FUNCTIONS
#----------------------------------------------------------------------

def displayUsage():
    sys.stderr.write("ERROR: Please provide path to SCENARIO as a unique argument\n")

# Function to read the configuration file
def readConf(CfgFile):
    Conf = OrderedDict({})
    with open(CfgFile, 'r') as f:
        # Read file
        Lines = f.readlines()

        # Read each configuration parameter which is compound of a key and a value
        for Line in Lines:
            if "#" in Line: continue
            if not Line.strip(): continue
            LineSplit = Line.split('=')
            try:
                LineSplit = list(filter(None, LineSplit))
                Conf[LineSplit[0].strip()] = LineSplit[1].strip()

            except:
                sys.stderr.write("ERROR: Bad line in conf: %s\n" % Line)

    return Conf

def processConf(Conf):
    ConfCopy = Conf.copy()
    for Key in ConfCopy:
        Value = ConfCopy[Key]
        if Key == "INI_DATE" or Key == "END_DATE":
            ParamSplit = Value.split('/')

            # Compute Julian Day
            Conf[Key + "_JD"] = \
                int(round(
                    convertYearMonthDay2JulianDay(
                        int(ParamSplit[2]),
                        int(ParamSplit[1]),
                        int(ParamSplit[0]))
                    )
                )

    return Conf

#######################################################
# MAIN BODY
#######################################################

# Check Input Arguments
if len(sys.argv) != 2:
    displayUsage()
    sys.exit()

# Extract the arguments
Scen = sys.argv[1]

# Select the conf file name
CfgFile = Scen + '/CFG/satperformances.cfg'

# Read conf file
Conf = readConf(CfgFile)

# Get SATSTAT file full path
SatStatFile = Scen + '/OUT/SAT/' + Conf["SATSTAT_FILE"]

# Read conf file
Conf = readConf(CfgFile)
#print(dump(Conf))

# Process Configuration Parameters
Conf = processConf(Conf)

# Print 
print('------------------------------------')
print('--> RUNNING SAT-PERFORMANCE ANALYSIS:')
print('------------------------------------')

# Loop over Julian Days in simulation
#-----------------------------------------------------------------------
for Jd in range(Conf["INI_DATE_JD"], Conf["END_DATE_JD"] + 1):

    # Compute Year, Month and Day in order to build input file name
    Year, Month, Day = convertJulianDay2YearMonthDay(Jd)
    
    # Estimate the Day of Year DOY
    Doy = convertYearMonthDay2Doy(Year, Month, Day)

    # Define the full path and name to the SAT INFO file to read
    SatFile = Scen + \
        '/OUT/SAT/' + 'SAT_INFO_Y%02dD%03d_G123_%ss.dat' % \
            (Year % 100, Doy, Conf["TSTEP"])

    # Define the name of the ENT-GPS instantaneous file
    EntGpsFile = Scen + \
        '/OUT/SAT/' + 'ENTGPS_Y%02dD%03d_G123_%ss.dat' % \
            (Year % 100, Doy, Conf["TSTEP"])

    # Define the name of the Output file Statistics
    SatStatsFile = SatFile.replace("INFO", "STAT")

    # Display Message
    print('\n*** Processing Day of Year: ', Doy, '...***')

    # Display Message
    print('1. Processing file:', SatFile)
    
    # Compute Satellite Statistics  FILE
    computeSatStats(SatFile, EntGpsFile, SatStatsFile)
    
    # Display Creation message
    print('2. Created files:', SatStatsFile, EntGpsFile)
    
    # Display Reading Message
    print('3. Reading file:', SatStatsFile)
    
    
    # Read Statistics file
    #Results = readConf(SatStatFile)

    # Display Generating figures Message
    print('4. Generating Figures...\n')
    
    # Generate Satellite Performances figures
    # Plot Satellite Visibility figures
    if(Conf["PLOT_SATMON"] == '1'):
        # Read the cols we need from Results file
        SatStatData = read_csv(SatStatFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[SATSTAT_IDX["PRN"],SATSTAT_IDX["MON"]])
        
        print( 'Plot Satellite Monitoring Periods ...')

        # Configure plot and call plot generation function
        SatFunctions.plotSatMon(SatStatData)  

print('------------------------------------')
print('--> END OF SAT-PERFORMANCE ANALYSIS:')
print('------------------------------------')

print('Check figures at the Output folder SAT/figures/')


#######################################################
#END OF SAT PERFORMANCES MODULE
#######################################################
