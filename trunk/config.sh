#!/bin/bash
#
###########
# Configuration script to set QuantSoftware enviroment variables.
# Edit the first few uncommented lines below, then copy this file 
# to localconfig.sh. Be sure to "source localconfig.sh" each time 
# you use QSTK
#
# Tucker Balch
#

###########
# In most cases you should only have to change the lines regarding
# QS and QSDATA.The rest are taken care of automatically.  However, 
# if you run in to problems, double check again here.
#

# Where is your installation of QSTK? If you followed instructions on
# on the wiki, this line should be correct:
export QS=$HOME/QSTK/trunk

# Where is your data. To use the default data that comes with the
# distribution, use the first line (default).  If you are using the 
# machines at GT use the second line (with hzr71)
#export QSDATA=$QS/QSData
export QSDATA=/hzr71/research/QSData

###########
# You probably should not need to revise any of the lines below.
# 

# Which machine are we on?
export HOSTNAME=`hostname`

export QSDATAPROCESSED=/hzr71/research/QSData/Processed
export QSDATATMP=$QSDATA/Tmp
export QSBIN=$QS/Bin

export PYTHONPATH=$PYTHONPATH:$QS:$QSBIN

# expand the PATH
export PATH=$PATH:$QSBIN

# location to store scratch files
export QSSCRATCH=/tmp

# Info regarding remote hosting of the system.
# This is where, for instance we might place a copy of
# the system for remote execution, or for the website.

export REMOTEUSER=tb34
export REMOTEHOST=gekko.cc.gatech.edu
export REMOTEHOME=/nethome/$REMOTEUSER
