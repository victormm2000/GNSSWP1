#!/usr/bin/env python

########################################################################
# SatFunctions.py:
# This script defines all internal functions of SatPerformance Module
#
#  Project:        SBPT
#  File:           SatFunctions.py
#  Date(YY/MM/DD): 20/07/11
#
#   Author: GNSS Academy
#   Copyright 2020 GNSS Academy
# 
# Internal dependencies:
#   COMMON
########################################################################
# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from collections import OrderedDict
#from COMMON import GnssConstants
from COMMON.GnssConstants import OMEGA_EARTH
from interfaces import SATSTAT_IDX
from math import sqrt
import numpy as np
from pandas import unique
from COMMON.Plots import generatePlot
import statistics

# Define SAT INFO FILE Columns
SatIdx = OrderedDict({})
SatIdx["SoD"]=0
SatIdx["DOY"]=1
SatIdx["PRN"]=2
SatIdx["SAT-X"]=3
SatIdx["SAT-Y"]=4
SatIdx["SAT-Z"]=5
SatIdx["MONSTAT"]=6
SatIdx["SRESTAT"]=7
SatIdx["SREx"]=8
SatIdx["SREy"]=9
SatIdx["SREz"]=10
SatIdx["SREb1"]=11
SatIdx["SREW"]=12
SatIdx["SFLT-W"]=13
SatIdx["UDREI"]=14
SatIdx["FC"]=15
SatIdx["AF0"]=16
SatIdx["AF1"]=17
SatIdx["LTCx"]=18
SatIdx["LTCy"]=19
SatIdx["LTCz"]=20
SatIdx["NRIMS"]=21
SatIdx["RDOP"]=22

# Define SAT STATISTICS file Columns
SatStatsIdx = OrderedDict({})
SatStatsIdx["PRN"]=0
SatStatsIdx["MON"]=1
SatStatsIdx["RIMS-MIN"]=2
SatStatsIdx["RIMS-MAX"]=3
SatStatsIdx["RMS-SRAalongtrack"]=4 # 6 before, changed to
SatStatsIdx["RMS-SREcrosstrack"]=5 # 5 before, changed to
SatStatsIdx["RMS-SREradialcomp"]=6 # 4 before, changed to
SatStatsIdx["RMS-SREclockcomp"]=7
SatStatsIdx["RMS-SREWorbit@WUL"]=8
SatStatsIdx["MAX-SREWorbit@WUL"]=9
SatStatsIdx["MAX-SFLT"]=10
SatStatsIdx["MIN-SFLT"]=11 # 20 before, changed to 11
SatStatsIdx["MAX-SIW"]=12 # 11 before, changed to 11
SatStatsIdx["MAX-FCbfastcorrections"]=13 # 16 before, changed to 13
SatStatsIdx["MAX-LTCclockAF0"]=14 # 15 before, changed to 14
SatStatsIdx["MAX-LTCxcomp"]=15
SatStatsIdx["MAX-LTCycomp"]=16
SatStatsIdx["MAX-LTCzcomp"]=17
#SatStatsIdx["MAX-FCbfastcorrections"]=17 #EGNOS V3 FAST CORRECTIONS (NULL IN V2)
SatStatsIdx["NMImisleadinginfo"]=18 #SI higher than 1 +=01
SatStatsIdx["NTRANS"]=19#    nº transmitions Monitored-NotMonitored or Don't Use
# FUNCTION: Display Message
#-----------------------------------------------------------------------
def displayUsage():
    sys.stderr.write("ERROR: Please provide SAT.dat file (satellite instantaneous\n\
information file) as a unique argument\n")

AllEpochs = {"ENTGPS": []}

# FUNCTION: Split line
#-----------------------------------------------------------------------
def splitLine(Line):
    LineSplit = Line.split()

    return LineSplit

# FUNCTION: Read Sat Info Epoch
#-----------------------------------------------------------------------

def readSatInfoEpoch(f): #pasa por todas las linias del brdc0140.19n?? en el while que hace? leer una epoca del satinfo
    EpochInfo = []
    
    # Read one line
    Line = f.readline()
    if(not Line):
        return []
    LineSplit = splitLine(Line)
    Sod = LineSplit[SatIdx["SoD"]]
    SodNext = Sod

    while SodNext == Sod:
        EpochInfo.append(LineSplit)
        Pointer = f.tell()
        Line = f.readline()
        LineSplit = splitLine(Line)
        try: 
            SodNext = LineSplit[SatIdx["SoD"]]

        except:
            return EpochInfo

    f.seek(Pointer)

    return EpochInfo

# FUNCTION: Initialized Output Statistics
#-----------------------------------------------------------------------

def initializeOutputs(Outputs):
    
    # Loop over GPS and Galileo Satellites
    for Const in ['G', 'E']:
        
        # Loop over all satellites of each constellation !! Que hace el SatLabel!!
        for Prn in range(1,33):
            SatLabel = Const + "%02d" % Prn
            
            Outputs[SatLabel] = OrderedDict({}) # que hace aqui el Outputs[SatLabel] y este for simplemente crea un Outputs[satlabel] con el mismo formato que ordereddict({})
            for var in SatStatsIdx.keys():
                
                if (var == "PRN"):
                    Outputs[SatLabel][var] = SatLabel                
                elif (var == "RIMS-MIN"):
                    Outputs[SatLabel][var] = 1e12 #1e12 entiendo
                elif (var == "MIN-SFLT"):
                    Outputs[SatLabel][var] = 1e12
                elif (var == "NTRANS"):
                    Outputs[SatLabel][var] = 0
                elif (var == "MAX-LTCxcomp"):
                    Outputs[SatLabel][var] = -1e12
                elif (var == "MAX-LTCycomp"):
                    Outputs[SatLabel][var] = -1e12
                elif (var == "MAX-LTCzcomp"):
                    Outputs[SatLabel][var] = -1e12
                elif (var == "MAX-FCbfastcorrections"):
                    Outputs[SatLabel][var] = -1e12
                elif (var == "MAX-FCbfastcorrec"):
                    Outputs[SatLabel][var] = -1e12


                else:
                    Outputs[SatLabel][var] = 0.0 #define todas las otras en valor float?

# FUNCTION: Initialize Intermediate Outputs
#-----------------------------------------------------------------------

def initializeInterOutputs(InterOutputs):
    
    # Loop over GPS and Galileo Satellites
    for Const in ['G', 'E']:
        
        for Prn in range(1,33): #te hace un loop por todas las linias del brdc NAV file y te define las variables como 0
            
            SatLabel = Const + "%02d" % Prn #que significa este SatLabel??
            InterOutputs[SatLabel] = OrderedDict({})
            InterOutputs[SatLabel]["NSAMPS"] = 0
            InterOutputs[SatLabel]["SODPREV"] = 0
            InterOutputs[SatLabel]["SODInstant"] = 0
            InterOutputs[SatLabel]["MONPREV"] = 0
            InterOutputs[SatLabel]["MONcurrentstep"] = 0
            InterOutputs[SatLabel]["SREb1"] = []
            InterOutputs[SatLabel]["SREbSUM2"] = 0.0
            InterOutputs[SatLabel]["SREaSUM2"] = 0.0
            InterOutputs[SatLabel]["SREcSUM2"] = 0.0
            InterOutputs[SatLabel]["SRErSUM2"] = 0.0
            InterOutputs[SatLabel]["SRESTAT"] = 0
            InterOutputs[SatLabel]["SREr"] = [] # cuidado con esto: esta como [] para la función de calculateENTGPS offset. Si cambio esto por EN OrderedDict, volverlo a cambiar por 0.0 
            InterOutputs[SatLabel]["SREa"] = 0.0
            InterOutputs[SatLabel]["SREc"] = 0.0
            InterOutputs[SatLabel]["SREACRSAMPS"] = 0
            InterOutputs[SatLabel]["SREWSUM2"] = 0
            InterOutputs[SatLabel]["SREWSAMPS"] = 0
            InterOutputs[SatLabel]["XPREV"] = 0
            InterOutputs[SatLabel]["YPREV"] = 0
            InterOutputs[SatLabel]["ZPREV"] = 0
            InterOutputs[SatLabel]["SiSat"] = 0
            #InterOutputs[SatLabel]["SATVEL"] =  0
            InterOutputs[SatLabel]["SREarray"] = np.zeros(3)
            InterOutputs[SatLabel]["ActualPosSat"] = np.zeros(3)
            InterOutputs[SatLabel]["SREr_list"] = []



    InterOutputs["ENT-GPS"] = 0
    

    return #pq esta puesto, creo que para acabar la funcion de una manera mas ordenada

# FUNCTION: Project a vector into a given direction
def projectVector(Vector, Direction):
    
    
    # Compute the Unitary Vector
    UnitaryVector = Direction / np.linalg.norm(Direction)

    return Vector.dot(UnitaryVector)

# FUNCTION: Estimate SRE-Along/Cross/Radial
#-----------------------------------------------------------------------

def computeSreAcr(DeltaT, PosPrev, Pos, Sre):
        

    # Compute Velocity computation deriving the position
    SatVel = (Pos-PosPrev) / DeltaT
    
    # Add Earth's Rotation Effect on the Reference frame
    vector_omegaearth= np.array([0.0, 0.0, OMEGA_EARTH])
    SatVel = SatVel + np.cross(vector_omegaearth,Pos)
    # Compute unitary vectors
    UnitaryVectorVel = SatVel / np.linalg.norm(SatVel)
    UnitaryVectorrad = Pos / np.linalg.norm(Pos)
    #UnitaryVectorcross = np.cross(UnitaryVectorrad,UnitaryVectorVel)
    UnitaryVectorcross = np.cross(UnitaryVectorVel,UnitaryVectorrad)
    #UnitaryVectorcross = UnitaryVectorcross/ np.linalg.norm(UnitaryVectorcross)
    UnitaryVectoralong = np.cross(UnitaryVectorcross,UnitaryVectorrad)

    # Compute SRE in ACR frame by projecting the SRE in XYZ
    SreA = projectVector(Sre,UnitaryVectoralong)
    #SreC = projectVector(Sre,UnitaryVectorcross)
    SreC = np.dot(Sre, UnitaryVectorcross)
    SreR = projectVector(Sre,UnitaryVectorrad)

    return float(SreA), float(SreC), float(SreR)
"""

En el código proporcionado, no se está considerando la posición anterior del satélite de manera directa
en los cálculos del vector unitario radial porque la variable PosPrev (posición anterior) se utiliza solo
para calcular la velocidad del satélite (SatVel), pero no influye en la dirección del vector unitario radial.
Esto se debe a que el vector radial se calcula directamente utilizando la posición actual del satélite (Pos).

Si quieres considerar un efecto más fino o un cambio en la dirección radial de acuerdo a la posición anterior,
tendrías que revisar cómo los cambios en la trayectoria afectan el cálculo de los vectores unitarios, aunque
para este tipo de cálculo (por ejemplo, en órbitas circulares o elípticas) la dirección radial se mantiene 
relativamente constante en cada paso de tiempo.

"""
"""
Calcula el offset ENT-GPS para cada satélite en un epoch específico utilizando la mediana de las diferencias entre SREb1 y SREr para cada satélite.
    Parámetros:
    - EpochInfo: Información de los satélites de este epoch.
    - InterOutputs: Contenedor de los resultados intermedios de todos los satélites.
    Devuelve:
    - ENT-GPS Offset calculado (mediana de la diferencia entre SREb1 y SREr por satélite). 
"""
def calculateEntGpsOffset(EpochInfo, InterOutputs):
       
    #ENTGPS_values = []  # Lista para almacenar los valores de ENTGPS calculados
    diff_values = []
    for SatInfo in EpochInfo:
        sat = SatInfo[SatIdx["PRN"]]  # Extraemos el PRN (número de satélite)
        if (SatInfo[SatIdx["MONSTAT"]] == '1'and SatInfo[SatIdx["SRESTAT"]] == '1'):
        # Verificar que el satélite tenga valores de SREb1 y SREr
            # Obtener los valores de SREr y SREb1 para el satélite
            SREr_values = InterOutputs[sat]["SREr"]
            SREb1_values = InterOutputs[sat]["SREb1"]
            # Calcular la diferencia entre SREb1 y SREr directamente (asumiendo que ambas listas tienen la misma longitud)                
            for line in range(len(SREb1_values)):
                diff_values.append(SREb1_values[line] - SREr_values[line])  # Restar SREb1[i] - SREr[i]
    # Si tenemos valores de ENTGPS, devolver la mediana de los resultados por satélite
    return np.median(diff_values)  # Mediana global de los valores ENTGPS. Aqui tengo 2 calculos de medianas. Entender exatctamente la secuencia del for de diff_values.append

"""
def calculateEntGpsOffset(EpochInfo, InterOutputs):
    diff_values = []
    for SatInfo in EpochInfo:
        sat = SatInfo[SatIdx["PRN"]]  # Extraemos el PRN (número de satélite)
        if(SatInfo[SatIdx["MONSTAT"]] == '1'):
        # Verificar que el satélite tenga valores de SREb1 y SREr
            if(SatInfo[SatIdx["SRESTAT"]] == '1'):
                #Obtener los valores de SREr y SREb1 para el satélite
                SREr_values = InterOutputs[sat]["SREr"]

                SREb1_values = InterOutputs[sat]["SREb1"]

            # Calcular la diferencia entre SREb1 y SREr directamente (asumiendo que ambas listas tienen la misma longitud)                
                for line in range(len(SREb1_values)):
                    diff_values.append(SREb1_values[line] - SREr_values[line])  # Restar SREb1[i] - SREr[i]
    # Si tenemos valores de ENTGPS, devolver la mediana de los resultados por satélite
    return np.median(diff_values)  # Mediana global de los valores ENTGPS. Aq
"""
"""
def calculateSREbRMS(EpochInfo, InterOutputs):
    for SatInfo in EpochInfo:
        sat = SatInfo[SatIdx["PRN"]]
        
        if SatInfo[SatIdx["MONSTAT"]] == '1' and SatInfo[SatIdx["SRESTAT"]] == '1':
            SREr_values = InterOutputs[sat]["SREr"]
            SREb1_values = InterOutputs[sat]["SREb1"]
            
            # Inicializar lista de diferencias para este satélite
            diff_values = []
            
            # Calcular la diferencia entre SREb1 y SREr
            for i in range(len(SREb1_values)):
                diff_values.append(SREb1_values[i] - SREr_values[i])
            
            # Calcular el ENTGPS (mediana de las diferencias)
            SRE_diff_median = np.median(diff_values)
            
            # Calcular los valores de SREb (SREb1 - ENTGPS)
            SREb_values = np.array(SREb1_values) - SRE_diff_median
            
            # Sumar el cuadrado de SREb para el cálculo posterior del RMS
            InterOutputs[sat]["SREbSUM2"] += np.sum(SREb_values**2)
            
    
    return InterOutputs
"""

# FUNCTION: Update Statistics Information
#-----------------------------------------------------------------------

def updateEpochStats(SatInfo, InterOutputs, Outputs):
        
    # Extract PRN Column
    sat = SatInfo[SatIdx["PRN"]]
    

    # Add Number of samples
    InterOutputs[sat]["NSAMPS"] = InterOutputs[sat]["NSAMPS"] + 1
    # Ignore the first Epoch in the Statistics due to Velocity 
    if (int(SatInfo[SatIdx["SoD"]]) > 0.0):
        ### IF SATELLITE IS MONITORED:
        if(SatInfo[SatIdx["MONSTAT"]] == '1'):

            # Add Satellite Monitoring if Satellite is Monitored
            Outputs[sat]["MON"] = Outputs[sat]["MON"] + 1
            
            ### IF SRE_STATUS IS OK:
            if(SatInfo[SatIdx["SRESTAT"]] == '1'):
                
                # Update number of samples Monitored & SRE OK
                InterOutputs[sat]["SREWSAMPS"] = InterOutputs[sat]["SREWSAMPS"] + 1

                InterOutputs[sat]["SREACRSAMPS"] = InterOutputs[sat]["SREACRSAMPS"] + 1
                


                # Update the Minimum Number of RIMS in view        
                if( int(SatInfo[SatIdx["NRIMS"]]) < Outputs[sat]["RIMS-MIN"]):
                    Outputs[sat]["RIMS-MIN"] = int(SatInfo[SatIdx["NRIMS"]])

                # Update the Maximum Number of RIMS in view
                if( int(SatInfo[SatIdx["NRIMS"]]) > Outputs[sat]["RIMS-MAX"]):
                    Outputs[sat]["RIMS-MAX"] = int(SatInfo[SatIdx["NRIMS"]])

                # Compute Si per satellite
                InterOutputs[sat]["SiSat"] = float(SatInfo[SatIdx["SREW"]])/ (5.33 * float(SatInfo[SatIdx["SFLT-W"]])) # Calculo SI para cada instante y satelite
                # Update number of misleading information per satellite
                if  ( InterOutputs[sat]["SiSat"] > 1):
                    Outputs[sat]["NMImisleadinginfo"] += 1
                # Update MAX SI (Safety Index)
                if ( InterOutputs[sat]["SiSat"] > Outputs[sat]["MAX-SIW"]): # Si el valor es mas grande que uno inicial para ese satelite, sobreescribir el valor por el calculado
                    Outputs[sat]["MAX-SIW"] = InterOutputs[sat]["SiSat"]         
    
                # Update the Maximum Satellite Orbit Error @ WUL
                if ( float(SatInfo[SatIdx["SREW"]]) > Outputs[sat]["MAX-SREWorbit@WUL"]):
                    Outputs[sat]["MAX-SREWorbit@WUL"] = float(SatInfo[SatIdx["SREW"]])
                
                # Update the Maximum Sigma FLT @ WUL during the day
                if ( float(SatInfo[SatIdx["SFLT-W"]]) > Outputs[sat]["MAX-SFLT"]):
                    Outputs[sat]["MAX-SFLT"] = float(SatInfo[SatIdx["SFLT-W"]])

                # Update the Minimum Sigma FLT @ WUL during the day            
                if ( float(SatInfo[SatIdx["SFLT-W"]]) < Outputs[sat]["MIN-SFLT"]):
                    Outputs[sat]["MIN-SFLT"] = float(SatInfo[SatIdx["SFLT-W"]])

                # Update the Maximum Satellite Position LTS correction X-Comp 
                if (abs(float(SatInfo[SatIdx["LTCx"]]))> Outputs[sat]["MAX-LTCxcomp"]):
                    Outputs[sat]["MAX-LTCxcomp"] = abs(float(SatInfo[SatIdx["LTCx"]]))

                # Update the Maximum Satellite Position LTS correction Y-Comp 
                if (abs(float(SatInfo[SatIdx["LTCy"]]))> Outputs[sat]["MAX-LTCycomp"]):
                    Outputs[sat]["MAX-LTCycomp"] = abs(float(SatInfo[SatIdx["LTCy"]]))

                # Update the Maximum Satellite Position LTS correction Z-Comp 
                if (abs(float(SatInfo[SatIdx["LTCz"]]))> Outputs[sat]["MAX-LTCzcomp"]):
                    Outputs[sat]["MAX-LTCzcomp"] = abs(float(SatInfo[SatIdx["LTCz"]]))

                # Update the Maximum Value of the Satellite LTC -Clock AF0 We are implementing an EGNOS V2 Algorythm No tengo claro que vaya en esta parte del if
                if ( abs(float(SatInfo[SatIdx["AF0"]])) > Outputs[sat]["MAX-LTCclockAF0"]):
                    Outputs[sat]["MAX-LTCclockAF0"] = abs(float(SatInfo[SatIdx["AF0"]]))
                # Update Sat Fast Corrections: CHECK lines and implementation  
                if (abs(float(SatInfo[SatIdx["FC"]])) > Outputs[sat]["MAX-FCbfastcorrections"]):
                    Outputs[sat]["MAX-FCbfastcorrections"] = abs(float(SatInfo[SatIdx["FC"]]))
                
                # Sacar ActualPosSat, SODInstant,SODPREV y SREarray
                
                InterOutputs[sat]["ActualPosSat"] = np.array([float(SatInfo[SatIdx["SAT-X"]]),float(SatInfo[SatIdx["SAT-Y"]]),float(SatInfo[SatIdx["SAT-Z"]])]) #- InterOutputs[sat]["PosPrev"]
                InterOutputs[sat]["SODInstant"] = float(SatInfo[SatIdx["SoD"]]) - float(InterOutputs[sat]["SODPREV"])
                InterOutputs[sat]["SODPREV"] = float(SatInfo[SatIdx["SoD"]])

                InterOutputs[sat]["SREarray"] = np.array([SatInfo[SatIdx["SREx"]], SatInfo[SatIdx["SREy"]],SatInfo[SatIdx["SREz"]]])
                # Sacar SREarray convertirlo a float 
                SREarray = np.array(InterOutputs[sat]["SREarray"], dtype=np.float64)
                #Llamar a función para sacar SREs
                SREa, SREc, SREr = computeSreAcr(InterOutputs[sat]["SODInstant"], InterOutputs[sat]["PosPrev"], InterOutputs[sat]["ActualPosSat"], SREarray)

                InterOutputs[sat]["SREr"].append(float(SREr))
                
                #Calcular por epoch el SREb--> SREclock ESTA LINIA ES IMPRESCINDIBLE PARA CALCULAR ENTGPS
                InterOutputs[sat]["SREb1"].append(float(SatInfo[SatIdx["SREb1"]]))
               
                SREbSUM2 = float(SatInfo[SatIdx["SREb1"]]) - (float(SatInfo[SatIdx["SREb1"]]) - float(SREr))

                #Calcular SREr,a,y c: SREarray * Ur multiplicacion de vectores con np.dot y hacerlo en sumatorio
                InterOutputs[sat]["SRErSUM2"] += float(SREr)**2
                InterOutputs[sat]["SREcSUM2"] += float(SREc)**2
                InterOutputs[sat]["SREaSUM2"] += float(SREa)**2

                #Actualizar PosPrev
                InterOutputs[sat]["PosPrev"] = InterOutputs[sat]["ActualPosSat"]

                InterOutputs[sat]["SREbSUM2"] += SREbSUM2**2            

            #End of if(SatInfo[SatIdx["SRESTAT"]] == '1'):

        #End of if(SatInfo[SatIdx["MONSTAT"]] == '1'):
    
        # Update NTRANS between M->NM or M->DU
        else:
            if ( InterOutputs[sat]["MONPREV"] == 1):
                Outputs[sat]["NTRANS"] += 1

  

    
    else:
        InterOutputs[sat]["XPREV"] = float(SatInfo[SatIdx["SAT-X"]])
        InterOutputs[sat]["YPREV"] = float(SatInfo[SatIdx["SAT-Y"]])
        InterOutputs[sat]["ZPREV"] = float(SatInfo[SatIdx["SAT-Z"]])
        InterOutputs[sat]["PosPrev"] = np.array([InterOutputs[sat]["XPREV"],InterOutputs[sat]["YPREV"],InterOutputs[sat]["ZPREV"]])
        InterOutputs[sat]["SODPREV"] = float(SatInfo[SatIdx["SoD"]])
        

    # KEEP CURRENT INFORMATION FOR NEXT EPOCH esto lo hace siempre
    
    # Keep Current Monitoring Status
    InterOutputs[sat]["MONPREV"] = int(SatInfo[SatIdx["MONSTAT"]])
    
    # RMS of SREW @ WUL during the day: first calcul
    InterOutputs[sat]["SREWSUM2"] += float(SatInfo[SatIdx["SREW"]])**2

             
# END OF FUNCTION: def updateEpochStats(SatInfo, InterOutputs, Outputs):


# FUNCTION: Compute the final Statistics
#-----------------------------------------------------------------------
def computeFinalStatistics(InterOutputs, Outputs):
    for sat in Outputs.keys():

        # Estimate the Monitoring Percentage
        if(InterOutputs[sat]["NSAMPS"] != 0):

            # Monitoring percentage = Monitored epochs / Total epochs
            Outputs[sat]["MON"] = Outputs[sat]["MON"] * 100.0 / InterOutputs[sat]["NSAMPS"]

            # RMS of SREW @ WUL during the day: last calcul
            Outputs[sat]["RMS-SREWorbit@WUL"]= sqrt(InterOutputs[sat]["SREWSUM2"]/ InterOutputs[sat]["SREWSAMPS"])

            # RMS of SREradial component during the day
            Outputs[sat]["RMS-SREradialcomp"] = sqrt(InterOutputs[sat]["SRErSUM2"]/InterOutputs[sat]["SREACRSAMPS"])
            # RMS of SREcrosstrack component during the day
            Outputs[sat]["RMS-SREcrosstrack"] = sqrt(InterOutputs[sat]["SREcSUM2"]/InterOutputs[sat]["SREACRSAMPS"])
            # RMS of SREalong component during the day
            Outputs[sat]["RMS-SRAalongtrack"] = sqrt(InterOutputs[sat]["SREaSUM2"]/InterOutputs[sat]["SREACRSAMPS"])
            
            Outputs[sat]["RMS-SREclockcomp"] = sqrt(InterOutputs[sat]["SREbSUM2"] / InterOutputs[sat]["SREACRSAMPS"])
                               
# END OF FUNCTION: def computeFinalStatistics(InterOutputs, Outputs):


# FUNCTION: Function to compute the Satellite Statistics
#-----------------------------------------------------------------------

def computeSatStats(satFile, EntGpsFile, satStatsFile):
    
    # Initialize Variables
    EndOfFile = False
    EpochInfo = []

    # Open SAT INFO file
    with open(satFile, 'r') as fsat:
        
        # Read header line of Sat Information file
        fsat.readline()

        # Open ENT-GPS Offset output file
        with open(EntGpsFile, 'w') as fEntGps:

            # Write Header of Output files
            fEntGps.write("#SOD  ENT-GPS\n")
            
            # Open Output File Satellite Statistics file
            with open(satStatsFile, 'w') as fOut:
                
                # Write Header of Output files
                fOut.write("#PRN  MON minRIMS maxRIMS SREaRMS SREcRMS SRErRMS  SREbRMS  SREWRMS  SREWMAX  SFLTMAX  SFLTMIN    SIMAX    FCMAX   LTCbMAX   LTCxMAX  LTCyMAX  LTCzMAX  NMI  NTRANS\n")

                # Define and Initialize Variables            
                Outputs = OrderedDict({})
                InterOutputs = OrderedDict({})
                
                # Initialize Outputs
                initializeOutputs(Outputs)
                initializeInterOutputs(InterOutputs)

                # LOOP over all Epochs of SAT INFO file
                # ----------------------------------------------------------
                
                while not EndOfFile:
                    
                    # Read Only One Epoch
                    EpochInfo = readSatInfoEpoch(fsat)           
            
                    # If EpochInfor is not Null
                    if EpochInfo != []:
         
                        # Write ENT-GPS Offset file example
                        #fEntGps.write("%5s %10.5f\n" % \
                            #(
                                #EpochInfo[0][SatIdx["SoD"]],
                                #ENTGPS

                            #))

                        # Loop over all Satellites Information in Epoch
                        # --------------------------------------------------
                        for SatInfo in EpochInfo:
                            
                            # Update the Output Statistics
                            updateEpochStats(SatInfo, InterOutputs, Outputs)
                            
                        ENTGPS = calculateEntGpsOffset(EpochInfo, InterOutputs)
                        #InterOutputs = calculateSREbRMS(EpochInfo, InterOutputs)
                            
                        fEntGps.write("%5s %10.5f\n" % \
                            (
                                EpochInfo[0][SatIdx["SoD"]],
                                ENTGPS
                                

                            ))

                        #End of for SatInfo in EpochInfo:
                    
                    # end if EpochInfo != []:
                    else:
                        EndOfFile = True
                        
                    #End of if EpochInfo != []:
                    #InterOutputs = calculateSREbRMS(EpochInfo, InterOutputs)
                # End of while not EndOfFile:
                #print(InterOutputs[sat]["SREb1"])
                # Compute the final Statistics
                # ----------------------------------------------------------
                computeFinalStatistics(InterOutputs, Outputs)
                
                # Write Statistics File
                # ----------------------------------------------------------
                
                # Define Output file format
                Format = "%s %6.2f %4d %6d %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %4d %4d"
                FormatList = Format.split()

                for sat in Outputs.keys():
                    
                    # Remove 0% monitored satellites because we're not interested in them
                    if(Outputs[sat]["MON"] != 0):
                        
                        for i, result in enumerate(Outputs[sat]):
                            fOut.write(((FormatList[i] + " ") % Outputs[sat][result]))

                        fOut.write("\n")

                        # End of for i, result in enumerate(Outputs[sat]):
                    # End of if(Outputs[sat]["MON"] != 0):
                # End of for sat in Outputs.keys():
            # End of with open(satStatsFile, 'w') as fOut:
        # End of with open(EntGpsFile, 'w') as fEntGps:
    # End of with open(satFile, 'r') as f:

#End of def computeSatStats(satFile, satStatsFile):
def plotSatMon(SatStatData):
        PlotConf = {}
       
        PlotConf["Type"] = "bar"
        PlotConf["FigSize"] = (12,6)
        PlotConf["Title"] = "Satellite Monitoring percentage Y19D014 G123 50s"

        PlotConf["yLabel"] = "Mon %"
        PlotConf["yLim"] = [34, 50]

        PlotConf["xLabel"] = "GPS-PRN"
        PlotConf["Grid"] = 1 # no se lo que significa

        PlotConf["xData"] = {}
        PlotConf["yData"] = {}
        Label = 0

        PlotConf["xData"][Label] = sorted(unique(SatStatData[SATSTAT_IDX["PRN"]]))
        PlotConf["yData"][Label] = SatStatData[SATSTAT_IDX["MON"]]
        PlotConf["Path"] = sys.argv[1] + '/OUT/SAT/' + 'SATMONITORING_PERCENTAGE_Y19D014_G123_50s.png'
        generatePlot(PlotConf)    
########################################################################
#END OF SAT FUNCTIONS MODULE
########################################################################
