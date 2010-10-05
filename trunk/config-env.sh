#!/bin/bash
#
# configuration script for QuantSoftware
#

# which machine are we on?
export HOSTNAME=`hostname`

# paths to various important directories
export QS=$HOME/QSTK

export QSDATA=$HOME/QSData
export QSDATARAW=$QSDATA/Raw
export QSDATAPROCESSED=$QSDATA/Processed
export QSDATATMP=$QSDATA/Tmp
export QSBIN=$QS/Bin

export PYTHONPATH=$PYTHONPATH:$QS

# expand the PATH
export PATH=$PATH:$QSBIN

# Info regarding remote hosting of the system.
# This is where, for instance we might place a copy of
# the system for remote execution, or for the website.

export REMOTEUSER=tb34
export REMOTEHOST=gekko.cc.gatech.edu
export REMOTEHOME=/nethome/$REMOTEUSER

