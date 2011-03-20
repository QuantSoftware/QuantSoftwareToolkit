#
# MonthlyRebalancingExample.py
#
# An example which creates a monthly allocation table
# from 2004 to 2009 and uses the quickSim to produce a fund history.
# It then dumps the allocation table to a picklefile format file named allocations.pkl
#
# Drew Bratcher
#

#sample_alloc setup
from pylab import *
from qstkutil import DataAccess
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quicksim as simulator
import matplotlib.pyplot as plt
import time as t
import cPickle
import datetime

#sample_historic setup
# Get first 20 S&P Symbols 
symbols = list(np.loadtxt('S&P500.csv',dtype='str',delimiter=',',comments='#',skiprows=0))
symbols = symbols[0:19]
#Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = datetime.datetime(2004,1,1)
tsend = datetime.datetime(2009,12,31)
num_days=(tsend-tsstart).days
ts_list=[ tsstart+datetime.timedelta(days=x) for x in range(0,num_days) ]

# Get the data from the data store
da=DataAccess.DataAccess()
historic = da.get_data(ts_list,symbols,"close")
alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
for date in range(0, len(historic.index)):
	if(historic.index[date].day==1):
		alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
alloc[symbols[0]] = .1
alloc['_CASH'] = .1
output=open("allocations.pkl","wb")
cPickle.dump(alloc, output)

funds=simulator.quickSim(alloc,historic,1000)
output2=open("funds2.pkl","wb")
cPickle.dump(funds, output2)

plt.clf()
plt.plot(funds.index,funds.values)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
