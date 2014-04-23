#!/usr/bin/env python

##################################################################
# This is basically a TTree wrapper class to be able to interact #
# with the icetray environment. The goal is to have a convenient #
# place to specify the variables you want in your tree and then  #
# build methods around filling those variables.  The user can    #
# either *only* use the fill(frame) method given below, or can   #
# add more complicated methods that she/he likes.                #
##################################################################

# Import things for root that you need
from ROOT import TTree, TBranch, TMath
import numpy as n

# Import things from icecube that are needed

#------------------------------#
# Specify output tree name here
# this is what will appear in
# the .root output file
#------------------------------#

treeName = "tree"
tree     = TTree(treeName, "Output Tree for simple analysis")

#------------------------------#
# Specify the variables to put
# into your tree here.
#------------------------------#
    
m_NPE          = n.zeros(1,dtype=float)  # Total best NPE
m_NPEbtw       = n.zeros(1,dtype=float)  # Total best NPE from best time window
m_coszen_SPE12 = n.zeros(1,dtype=float)  # Cos(Zenith) from SPE12
m_coszen_ImpLF = n.zeros(1,dtype=float)  # Cos(Zenith) from ImpLF
m_daqtime      = n.zeros(1,dtype=int)

#------------------------------#
# Assign the branches here
# IMPORTANT: If you don't assign 
# your variables from above, they 
# won't appear in your tree
#------------------------------#

tree.Branch("NPE",          m_NPE,          "NPE/D")
tree.Branch("NPEbtw",       m_NPEbtw,       "NPEbtw/D")
tree.Branch("coszen_SPE12", m_coszen_SPE12, "COSZENSPE12/D")
tree.Branch("coszen_ImpLF", m_coszen_ImpLF, "COSZENIMPLF/D")
tree.Branch("daqtime",      m_daqtime,      "DAQTIME/I")

#------------------------------#
# Add Fill Method that is 
# kind of generic. Can add more
# methods to do more useful
# things.
#------------------------------#
def fillTree(frame):

    global tree, m_NPE, m_NPEbtw, m_daqtime
    global m_coszen_SPE12, m_coszen_ImpLF

    # Make sure all necessary frames are here
    if 'SPEFit12EHE' not in frame:
        return False
    if 'EHEOpheliaParticleSRT_ImpLF' not in frame:
        return False
    if 'EHEPortiaEventSummary' not in frame:
        return False
    if 'I3EventHeader' not in frame:
        return False
    
    # Get the NPE info
    m_NPE[0]    = frame['EHEPortiaEventSummary'].GetTotalBestNPE()
    m_NPEbtw[0] = frame['EHEPortiaEventSummary'].GetTotalBestNPEbtw()

    # Get angular info
    m_coszen_SPE12[0] = TMath.Cos( frame['SPEFit12EHE'].dir.zenith )
    m_coszen_ImpLF[0] = TMath.Cos( frame['EHEOpheliaParticleSRT_ImpLF'].dir.zenith )

    # Get time
    m_daqtime[0] = frame['I3EventHeader'].start_time.utc_daq_time

    # Now call fill on the tree so 
    # it will save the information
    tree.Fill()

    # end fillTree

