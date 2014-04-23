#!/usr/bin/env python

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
# This script will create a TTree object stored in      #
# a rootfile.  It takes as input the full path to a     #
# .txt file that contains the full path to the i3 files #
# to be processed.  The tree variables to be stored     #
# are defined in Tree.py along with the methods to fill #
# them.                                                 #
# The user should not have to edit this file unless     #
# more methods are added in Tree.py                     #
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

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

from ROOT import TFile, TMath, TParameter, TTree

#
## EHE User Methods
#
from EHESplitter import *
from Tree import *

#----------------------------------#
# One user option is supported
#----------------------------------#
argv = sys.argv
if len(argv) != 2:
    print "In order to run script.py path/to/filelist.txt"
    print "You entered: "
    print argv
    sys.exit()

#
## Assume first argument is path to file
#
tofile = argv[1]
if not os.path.isfile(tofile):
    print "File doesn't exist."
    print tofile
    print "Enter valid path."
    sys.exit()
#
## Now set input
#

inputFile = open(tofile,"r")
fileList  = []
for f in inputFile:
    fileList.append(f.split("\n")[0])

#
## Now output
#
outName   = tofile
if "/" in tofile:
    outName = tofile.split("/")[-1]  # remove rest of path
outName = outName.split(".")[0]      # get rid of .txt

outrootfile = "../rootfiles/"+outName+".root"

#
## Have input info and output
#

print "Input:  ", tofile
print "Output: ", outrootfile

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
# Define Root File and Tree
#----------------------------------#

# Output file
rootfile = TFile(outrootfile,"recreate")

#----------------------------------#
# Define some user modules as needed
#----------------------------------#

#
## Want to save livetime
#
initialTime  = -999.
previousTime = -999. 
def timingInfo(frame):
    if 'I3EventHeader' not in frame:
        return False
    
    global initialTime, previousTime

    # Get UTC Time
    start_time = frame['I3EventHeader'].start_time
    daq_time   = start_time.utc_daq_time

    # Save times
    previousTime = daq_time

    return True

#
## Some event counter to let
## user know things progressing
#
counter = 0
def CountEvent(frame):
    if not which_split(frame, split_name='InIceSplit'):
        return False
    if not isEHEPStream(frame):
        return False

    global counter
    if counter % 100 == 0:
        print "Processed " + str(counter) + " EHE Events"
    counter += 1
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
## Add user Modules
#

# Count event must be first. It is what
# makes sure that the event is an EHE
# event!
tray.AddModule(CountEvent,"counter")

# Save some timing info to calculate 
# livetime. Not necessary, but nice
# to have
tray.AddModule(timingInfo,"timingInfo")

# Add method to fill the tree
tray.AddModule(fillTree, "treeFiller")

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


#----------------------------------#
# Write and close root file
#----------------------------------#
tree.Write()
rootfile.Write()
rootfile.Close()
