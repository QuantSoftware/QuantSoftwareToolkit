#!/bin/bash
#
# Configuration script to set QuantSoftware enviroment variables
#
# Tucker Balch
#

#
# In most cases you should only have to change these variables.
# The rest are taken care of automatically.  However, if you run
# in to problems, double check again here.
#
export QS=$HOME/QSTK
export QSDATA=$HOME/QSData

# Which machine are we on?
export HOSTNAME=`hostname`

export QSDATAPROCESSED=$QSDATA/Processed
export QSDATATMP=$QSDATA/Tmp
export QSBIN=$QS/Bin

export PYTHONPATH=$PYTHONPATH:$QS:$QSBIN

# expand the PATH
export PATH=$PATH:$QSBIN

# Info regarding remote hosting of the system.
# This is where, for instance we might place a copy of
# the system for remote execution, or for the website.

export REMOTEUSER=tb34
export REMOTEHOST=gekko.cc.gatech.edu
export REMOTEHOME=/nethome/$REMOTEUSER

