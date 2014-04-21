#!/usr/bin/env python

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
# So it turns out that ehe package doesn't have latest #
# recopulse package, and the standard icerec project   #
# doesn't have tree maker... So I will just do the     #
# analysis without making the tree and just make the   #
# histograms                                           #
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#

#----------------------------------#
# import icecube things
#----------------------------------#
from I3Tray import *
from icecube import DomTools, icetray, dataio, trigger_splitter, BadDomList, portia
from icecube.icetray import I3PacketModule
from icecube.BadDomList import bad_dom_list_static
import os, sys
import glob
import numpy as n
from optparse import OptionParser

from ROOT import TFile, TH1F, TMath, TParameter, TTree

#                                                                                                  
## EHE User methods                                                                                
#                                                                                                  
from EHEFilter import *

#----------------------------------#
# Stick with same user options
#----------------------------------#
def multiarg(option, opt_str, value, parser):
    assert value is None
    value = []
    def floatable(str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    for arg in parser.rargs:
        if arg[:2] == "--" and len(arg) > 2:
            break
        if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
            break
        value.append(arg)
    del parser.rargs[:len(value)]
    setattr(parser.values,option.dest,value)

parser = OptionParser()

parser.add_option("-i", "--input", action="callback", callback=multiarg, default="", dest="INPUT",\
help="Input i3 data file")

#
## Get parsed arguments
#

(options, args) = parser.parse_args()
inputFName = options.INPUT[0]
inFile     = open(inputFName,"r")
fileList = []
for f in inFile:
    fileList.append(f.split("\n")[0])

# Take the input file name and save
# ROOT file in same format
outName = inputFName.split("/")[2]
outName = outName.split(".")[0]
outrootfile = "../rootfiles/"+outName+".root"
print outrootfile
#----------------------------------#
# Load Libraries
#----------------------------------#

load("libophelia")
load("dataclasses")
load("SeededRTCleaning")
load("libportia")

#----------------------------------#
# Specify variables
#----------------------------------#

tray = I3Tray()

#----------------------------------#
# Define ROOT File and histograms
#----------------------------------#

def hist(name,nbins,xmin,xmax):
    h = TH1F(name,name,nbins,xmin,xmax)
    return h

# Output file
rootfile = TFile(outrootfile,"recreate")

# delta T histogram
h_dt = hist("deltaT_DAQ",10000,0,10)

# Physics histograms
h_coszen_SPE12 = hist("coszeb_SPE12",20,-1,1)
h_coszen_ImpLF = hist("coszen_ImpLF",20,-1,1)
h_logNPE       = hist("logNPE",100,0,10)

#----------------------------------#
# Make a tree
#----------------------------------#
tree = TTree("tree","EHE Filter Check Tree")

#
## Set branches
#

#Variables
m_NPE    = n.zeros(1,dtype=float)
m_NPEbtw = n.zeros(1,dtype=float)
m_time   = n.zeros(1,dtype=float)
m_coszen_SPE12 = n.zeros(1,dtype=float)
m_coszen_ImpLF = n.zeros(1,dtype=float)

tree.Branch("NPE", m_NPE, "NPE/D")
tree.Branch("NPEbtw", m_NPEbtw, "NPEbtw/D")
tree.Branch("DAQtime", m_time, "Timing/D")
tree.Branch("coszen_SPE12", m_coszen_SPE12,"COSZENSPE12/D")
tree.Branch("coszen_ImpLF", m_coszen_ImpLF,"COSZENIMPLF/D")

#----------------------------------#
# Define plotting modules
#----------------------------------#

#
## Timing histogram
#
initialTime  = -999.
previousTime = -999. 
def timingInfo(frame):
    if 'I3EventHeader' not in frame:
        return False
    
    global initialTime, previousTime, m_time

    # Get UTC Time
    start_time = frame['I3EventHeader'].start_time
    daq_time   = start_time.utc_daq_time
    
    # Fill hists and store variables
    if initialTime < 0:
        initialTime = daq_time
    if previousTime < 0:
        h_dt.Fill(0)
    else:
        h_dt.Fill(daq_time - previousTime)

    previousTime = daq_time
    m_time[0] = daq_time

    return True

#
## Physics histograms
#
def physicsInfo(frame):

    global m_NPE, m_NPEbtw, m_coszen_SPE12, m_coszen_ImpLF

    # Make sure all necessary frames are here
    if 'SPEFit12EHE' not in frame:
        return False
    if 'EHEOpheliaParticleSRT_ImpLF' not in frame:
        return False
    if 'EHEPortiaEventSummary' not in frame:
        return False

    # Get the three variables
    zen_SPE12 = frame['SPEFit12EHE'].dir.zenith
    zen_ImpLF = frame['EHEOpheliaParticleSRT_ImpLF'].dir.zenith
    npe       = frame['EHEPortiaEventSummary'].GetTotalBestNPEbtw()

    h_coszen_SPE12.Fill(TMath.Cos(zen_SPE12))
    h_coszen_ImpLF.Fill(TMath.Cos(zen_ImpLF))
    h_logNPE.Fill(TMath.Log10(npe))

    
    m_NPEbtw[0] = npe
    m_NPE[0]    = frame['EHEPortiaEventSummary'].GetTotalBestNPE()
    m_coszen_SPE12[0] = TMath.Cos(zen_SPE12)
    m_coszen_ImpLF[0] = TMath.Cos(zen_ImpLF)
    
def fillTree(frame):
    global tree
    tree.Fill()
    return True

#----------------------------------#
# Add Modules
#----------------------------------#

#
## I3 Reader
#

tray.AddModule( "I3Reader", "Reader",
                Filenamelist = fileList)

#                                                                                                  
## Print info                                                                                      
#                                                                                                  
counter = 0
def CountEvent(frame):
    if not which_split(frame, split_name='InIceSplit'):
        return False
    if not isEHEPStream(frame):
        return False

    global counter
    if counter % 100 == 0:
        print "Have " + str(counter) + " EHE Event"
    counter += 1
    return True

tray.AddModule(CountEvent,"counter")
tray.AddModule(physicsInfo,"physInfo")
tray.AddModule(timingInfo,"timingInfo")
tray.AddModule(fillTree,"treefiller")
#                                                                                                  
## Clean up                                                                                        
#                                                                                                  

tray.AddModule("TrashCan","itterashai")

#----------------------------------#
# Run
#----------------------------------#
tray.Execute()
tray.Finish()


#----------------------------------#
# Add some additional information as
# a TParameter
#----------------------------------#
total_time = previousTime - initialTime
tot_time = TParameter('double')("livetime",total_time)
tot_time.Write()

#----------------------------------#
# Printout some final info
#----------------------------------#
print "Total EHE events: ", counter
print "Total time: ", total_time


rootfile.Write()
rootfile.Close()
