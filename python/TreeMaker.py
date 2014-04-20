#!/usr/bin/env/ python

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
# This filter will loop over EHE events and write all events  #
# that have the EHE flag set.  The tree can then be analyzed. #
# The initial goal is to check the test run.                  #
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

#----------------------------------#
# Import Icecube things
#----------------------------------#

from I3Tray import *
from icecube import DomTools, icetray, dataio, trigger_splitter, BadDomList
from icecube.icetray import I3PacketModule
from icecube.BadDomList import bad_dom_list_static
import os, sys
import glob
from optparse import OptionParser

#
## EHE User methods
#
from EHEFilter import *

#----------------------------------#
# Parse input options
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

parser.add_option("-i", "--input", action="callback", callback=multiarg, default="", dest="INPUT",help="Input i3 data file")

parser.add_option("--root",action="store",type="string",default="",dest="OUTPUTROOT",help="Output root file name")

#
## Get the parsed arguments
#

(options, args) = parser.parse_args()
inputFName = options.INPUT
fileList   = inputFName
outrootfile = options.OUTPUTROOT

# Maybe add error checking? see if path valid?

#----------------------------------#
# Load libraries
#----------------------------------#
load("libtree-maker")
load("libophelia")
load("dataclasses")
load("SeededRTCleaning")

#----------------------------------#
# Specify some variables
#----------------------------------#

tray = I3Tray()

#----------------------------------#
# Add Modules
#----------------------------------#

#
## I3 Reader
#
print fileList
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
        print "Have EHE Event"
    counter += 1
    return True

tray.AddModule(CountEvent,"counter")
#
## Tree maker
#

tray.AddModule("I3TreeMakerModule","tree-maker-split",
               outTreeName = "RealTree",
               outFileName = outrootfile,
               doJulietTree = False,
               doDetectorTree = True,
               inSplitDOMMapName = "splittedDOMMapSRT",
               doPulseChannelTree = False,
               fillFirstLastEventTime = True,
               InAtwdPortianame = "EHEBestPortiaPulseSRT",
               inFadcPortiaName = "EHEBestPortiaPulseSRT",
               inPortiaEventName = "EHEPortiaEventSummarySRT",
               doFirstguessTree = True,
               inFirstguessName = "EHEOpheliaSRT_ImpLF",
               inFirstguessNameBtw = "EHEOpheliaBTWSRT",
               doSpotTree = False,
               doEheStarTree = False,
               doStdParticleTree = True,
               inRecoParticleName = "SPEFit12EHE",
               inRecoParticleParameterName = "SPEFit12EHEFitParams",
               If = lambda f: which_split(f, split_name='InIceSplit') and isEHEPStream(f)
               )

#
## Clean up
#

tray.AddModule("TrashCan","itterashai")

#----------------------------------#
# Run
#----------------------------------#
tray.Execute()
tray.Finish()

print "Total EHE events: ", counter
