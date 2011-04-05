#
# tutorial4.py
#
# @summary: An example which creates a monthly allocation table
# from 2004 to 2009. It then dumps the allocation table to a pickle
# file named allocations.pkl
#
# @author: Drew Bratcher
#

#python imports
import time as t
import cPickle
import os
import datetime as dt
from pylab import *
from pandas import *
import matplotlib.pyplot as plt


#qstk imports
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from qstkutil import pseries as ps
import quicksim as simulator

#sample_historic setup
# Get first 20 S&P Symbols 
symbols = list(np.loadtxt(os.environ['QS']+"/quicksim/strategies/S&P500.csv",dtype='str',delimiter=',',comments='#',skiprows=0))
symbols = symbols[0:19]

#Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = dt.datetime(2004,1,1)
tsend = dt.datetime(2009,12,31)
timeofday = dt.timedelta(hours=16)
timestamps=du.getNYSEdays(tsstart,tsend,timeofday)

# Get the data from the data store
dataobj=da.DataAccess('Norgate')
historic = dataobj.get_data(timestamps,symbols,"close")

# Compute allocations
alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
for date in range(0, len(historic.index)):
	if(historic.index[date].day==1):
		alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
alloc[symbols[0]] = .1
alloc['_CASH'] = .1

#output alloc table to a pickle file
output=open("allocations.pkl","wb")
cPickle.dump(alloc, output)
