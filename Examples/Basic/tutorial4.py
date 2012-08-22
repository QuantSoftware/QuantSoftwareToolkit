'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on September, 12, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''

#python imports
import cPickle
import os
import datetime as dt
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import random

#qstk imports
from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du

# Get first 20 S&P Symbols 
symbols = list(np.loadtxt(os.environ['QS']+"/quicksim/strategies/S&P500.csv",dtype='str',delimiter=',',comments='#',skiprows=0))
symbols = symbols[0:20]
symbols.append('_CASH')

#Set start and end boundary times.
tsstart = dt.datetime(2004,1,1)
tsend = dt.datetime(2009,12,31)
timeofday = dt.timedelta(hours=16)
timestamps=du.getNYSEdays(tsstart,tsend,timeofday)

# Create First Allocation Row
vals=[]
for i in range(21):
	vals.append(random.randint(0,1000))

# Normalize
for i in range(21):
	vals[i]=vals[i]/sum(vals)

# Create Allocation DataFrame
alloc=DataFrame(index=[tsstart], columns=symbols, data=[vals]) 

# Add a row for each new month
last=tsstart
for day in timestamps:
	if(last.month!=day.month):
		# Create Random Allocation
		vals=[]
		for i in range(21):
			vals.append(random.randint(0,1000))
		# Normalize
		for i in range(21):
			vals[i]=vals[i]/sum(vals)
		# Append new row
		alloc=alloc.append(DataFrame(index=[day], columns=symbols, data=[vals]))
	last=day


#output alloc table to a pickle file
output=open("allocations.pkl","wb")
cPickle.dump(alloc, output)
