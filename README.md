#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
# Code:    Tree Analysis Example
# Author:  Matt Relich
# Created: 23/4/2014
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#


################################################################
#                          PREAMBLE                            #
################################################################

This is a simple example class to do a 'quick' analyis.  I 
put quick in quotes because it is quick in the sense that it
is easy to start analyzing, but the code seems to be a bit
slow.  This package could evolve in the future to do things
more effeciently (if possible) but at this time I don't really
know how to do that.

################################################################
#	   		   REMARKS                             #
################################################################

There are currently only three pieces of code that the user
needs to worry about.  They are all located in python/ directory
and are named (with annotation):

#
## EHESplitter.py
#

This piece of code is used to check the P and Q frames to see
if the EHE flag has been set.  Meaning, does this event pass
some basic Level2 filtering used in the EHE analysis.  If you 
want to check other streams, you will need to investigate
what the appropriate mask is.

#
## Tree.py
#

This is the user defined ROOT tree.  Right now, only a few 
variables are stored: NPE, NPE from best time window, the
cosine of two zenith angles calculated from different 
algorithms, and some timing info of when the event happened.
It is up to the user to add new variables to the tree that
are relevant to their analysis.  The examples given should
be enough to get started.  Feel free to add more methods
other than fillTree(frame), but BE CAREFUL.  If you add
more methods that will *set* new variables, they should
be added to the I3Tray AFTER fillTree is cadded.  The reason
is that fillTree will actually call tree.Fill() which will
put the assigned variables into the tree.  If you put your
methods after, then they will not be included with the 
appropriate event, and bad things will happen when you go 
back to analyze the output trees.

#
## TreeMaker.py
#

This more or less follows the standard idea of doing an analysis
on i3 files.  I have added the minimum content to the code. This 
means currently the modules that are included:

I3Reader -- This is just what takes you through the p and q frames
timeInfo -- User method to keep track of when the events start and
	    when they end
counter  -- Method to count the number of EHE events
fillTree -- which is defined in Tree.py

################################################################
#                          HOW TO USE                          #
################################################################

There are three steps to use this package.  The first is to run
the setupdir.sh script found in the main directory.  This will
creat run, run/errLog, run/outLog.  The latter two are useful when
using condor system.

The second step is to make a filelist.txt that contain a list
of the FULL path to the file. TreeMaker.py will check to make 
sure it is a valid file (ie. it exists), so please make sure the
full path is used.  It is up to you how to divide the jobs up. If you 
have a batch system to run on, you can optimize for speed or convenience.
For example, more filelists means each job will take less time, but
it can be a headache dealing with 100s of output files.

I will mention here that all output rootfiles will be sent to the
rootfiles/ directory.  If you prefer to put them somewhere else, like
on some other disk on your machine simply remove rootfiles/ and link 
your directory you want to save them to:

rm -r rootfiles
mkdir /some/where/on/your/machine
ln -s /some/where/on/your/machine rootfiles

alternatively you can change in TreeMaker.py where the output goes.

The final step is to execute the script from run directory:
python ../python/TreeMaker.py filelist.txt 
or 
./../python/TreeMaker.py filelist.txt


################################################################
#                           MISC                               #
################################################################

I am new to python (more of a C++ person), so some things might 
need to be tweaked. Let me know if you see some better way to do 
something.  Also, you may need to change at the top of TreeMaker.py 
the path to python.  I am not really sure about this though.