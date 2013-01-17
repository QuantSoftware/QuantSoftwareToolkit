'''
Created on Sep 23, 2010

@author: Shreyas Joshi
@contact: shreyasj at gatech.edu
'''

import sys
#import os
import datetime as dt
import time as t
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import timeutil as tu

# Set the list of stocks for us to look at
symbols= list()
symbols = list(np.loadtxt('example-syms.csv',dtype='str',delimiter=',',
	comments='#',skiprows=0))
symbols.append("IBM")
#symbols.append("BLAH")  # uncomment this line to see what happens

# Set the directories from which we will read data
QSDATA = os.environ.get('QSDATA')
listOfPaths=list()
listOfPaths.append(QSDATA + "/Processed/Norgate/Equities/US_NASDAQ/")
listOfPaths.append(QSDATA + "/Processed/Norgate/Equities/US_NYSE/")
listOfPaths.append(QSDATA + "/Processed/Norgate/Equities/US_NYSE Arca/")

# Set start and end boundary times.  They must be specified in Unix Epoch
start_bound = tu.ymd2epoch(2008,1,1)
end_bound = tu.ymd2epoch(2010,1,1)

# Create the data object. Once the dates are set, this object can not give you 
# data from outside this range even though it might be present in the hdf file
data= da.DataAccess(True, listOfPaths, "/StrategyData", "StrategyData",
	False, symbols, start_bound, end_bound)

# Find the actual first and last timestamps
timestamps = data.getTimestampArray() 
start_time = timestamps[0]
end_time = timestamps[-1]

print "first timestamp:" + str(tu.epoch2date(start_bound)) + " mapped to " + str(tu.epoch2date(start_time))
print "last  timestamp:" + str(tu.epoch2date(end_bound)) + " mapped to " + str(tu.epoch2date(end_time))

# Now get the matrix of data
adj_close = data.getMatrixBetweenTS(symbols, "adj_close", start_time, end_time)

print "The adjusted closing prices are: "
print adj_close

# 1D numpy array with the timestamps. A typecast to list will convert this to a list.
timestamps = data.getTimestampArray() 
dates = []
for ts in timestamps:
    dates.append(tu.epoch2date(ts))
symbols= data.getListOfSymbols()

# Normalize the prices
normdat = adj_close/adj_close[0,:]

# Plot the closing prices
plt.clf()
for i in range(0,size(normdat[0,:])):
        plt.plot(dates,normdat[:,i])
plt.legend(symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.draw()
savefig("fig1.pdf", format='pdf')

print "A list of the symbols we read in: "
print symbols
