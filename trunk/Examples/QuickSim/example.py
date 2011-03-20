#
# example.py
#
# An example script which makes use of the quickSim module.
#
# @author: Drew Bratcher
# @contact: dbratcher@gatech.edu
#

from pylab import *
from pandas import *
import matplotlib.pyplot as plt
from qstkutil import DataAccess
from qstkutil import timeutil
from qstkutil import pseries
import quicksim
import datetime


#sample allocation table setup    
dates= [datetime.datetime(2008,1,2),
        datetime.datetime(2008,1,21),
        datetime.datetime(2008,2,1),
        datetime.datetime(2008,3,1),
        datetime.datetime(2008,4,1),
        datetime.datetime(2008,5,1),
        datetime.datetime(2008,6,1),
        datetime.datetime(2008,7,1),
        datetime.datetime(2008,8,1),
        datetime.datetime(2008,9,1),
        datetime.datetime(2008,10,1),
        datetime.datetime(2008,11,1),
        datetime.datetime(2008,12,1)]

vals={
    'AMN' :   [.2, .2, .2, .2, .2, .3, .4, .3, .2, .1, .3, .2, .1],
    'ATVI' :   [.3, .3, .3, .3, .3, .1, .4, .3, .2, .1, .3, .2, .1],
    'BBY' :   [.3, .3, .3, .3, .3, .3, .2, .4, .6, .8, .4, .6, .8],
    '_CASH' : [.2, .2, .2, .2, .2, .3, .0, .0, .0, .0, .0, .0, .0],}

sample_alloc = DataMatrix(vals, index=dates)    

#sample_historic setup
# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = datetime.datetime(2008,1,2)
tsend = datetime.datetime(2008,12,31)
num_days=(tsend-tsstart).days
ts_list=[ tsstart + datetime.timedelta(days=x) for x in range(0,num_days) ]
symbols = sample_alloc.cols()
symbols.pop()

# Get the data from the data store
da=DataAccess.DataAccess('norgate')
sample_historic = da.get_data(ts_list, symbols, "close")

funds=simulator.quickSim(sample_alloc,sample_historic,1000)

#plot funds
plt.clf()
plt.plot(funds.index,funds.values)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
