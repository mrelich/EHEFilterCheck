#!/usr/bin/env python

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
# This script will have two methods in order to isolate #
# the physics frames for in ice data (ie. not ice top)  #
# and make sure the EHE flag has been set.              #
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

from icecube import icetray, dataclasses

# Be sure to specify the year here
# that your data corresponds to
year = str(13)

#---------------------------------#
# Method to pick EHE Stream
#---------------------------------#
def isEHEPStream(frame):
    if frame.Stop == icetray.I3Frame.Physics and frame.Has('FilterMask'):
        if frame['FilterMask'].get('EHEFilter_'+year).condition_passed:
            return True
        else:
            return False

    # Condition not satisfied
    return False

#---------------------------------#
# Method to check Q Frame if EHE
# stream is good
#---------------------------------#
def isEHEQStream(frame):
    if frame.Stop == icetray.I3Frame.DAQ and frame.Has('FilterMask'):
        if frame['FilterMask'].get('EHEFilter_'+year).condition_passed:
            return True
        else:
            return False

    # Condition not satisfied
    return False
    

#---------------------------------#
# Method to split a frame
#---------------------------------#
def which_split(frame, split_name=None, split_names=None):
    if split_name is None and split_names is None:
        raise RuntimeError("need to set either split_name or split_names")
    elif split_name is not None and split_names is not None:
        raise RuntimeError("cannot specify both split_name and split_names")
    
    splits_list = split_names
    if split_name is not None:
        splits_list = [split_name]
    
    if frame.Stop == icetray.I3Frame.Physics:
        if frame['I3EventHeader'].sub_event_stream in splits_list:
            return True
        else:
            return False
    
    # If we are here then frame is not physics
    # return false
    return False
