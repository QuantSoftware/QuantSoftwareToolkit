'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on 1/1/2011

@author: Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Example of creating a monthly allocation table..
'''
#
# MonthlyRebalancingExample.py
#
# An example which creates a monthly allocation table
# from 2004 to 2009 and uses the quickSim to produce a fund history.
#
# Drew Bratcher
#

# python imports
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import time as t
import cPickle
import datetime as dt
import os

# qstk imports
from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du
from quicksim import quickSim as qs

#sample_historic setup
# Get first 20 S&P Symbols 
symbols = list(np.loadtxt(os.environ['QS']+'/quicksim/strategies/S&P500.csv',dtype='str',delimiter=',',comments='#',skiprows=0))
symbols = symbols[0:19]

#Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = dt.datetime(2004,1,1)
tsend = dt.datetime(2009,12,31)
timeofday=dt.timedelta(hours=16)
timestamps=du.getNYSEdays(tsstart,tsend,timeofday)

# Get the data from the data store
dataobj=da.DataAccess('Norgate')
historic = dataobj.get_data(timestamps,symbols,"close")

# create alloc
alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
for date in range(0, len(historic.index)):
	if(historic.index[date].day==1):
		alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
alloc[symbols[0]] = .1
alloc['_CASH'] = .1

#output to pickle file
output=open("allocations.pkl","wb")
cPickle.dump(alloc, output)

#test allocation with quicksim
print alloc
print historic
funds=qs.quickSim(alloc,historic,1000)

#output to pickle file
output2=open("funds2.pkl","wb")
cPickle.dump(funds, output2)

#plot funds
plt.clf()
plt.plot(funds.index,funds.values)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
