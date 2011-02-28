#
# example.py
#
# An example script which makes use of the quickSim module.
#
# @author: Drew Bratcher
# @contact: dbratcher@gatech.edu
#

from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quickSim as simulator
import matplotlib.pyplot as plt
import datetime as dt

#sample allocation table setup    
dates= [dt.date(2008,1,2),
        dt.date(2008,1,21),
        dt.date(2008,2,1),
        dt.date(2008,3,1),
        dt.date(2008,4,1),
        dt.date(2008,5,1),
        dt.date(2008,6,1),
        dt.date(2008,7,1),
        dt.date(2008,8,1),
        dt.date(2008,9,1),
        dt.date(2008,10,1),
        dt.date(2008,11,1),
        dt.date(2008,12,1)]

vals={
    'XOM' :   [.2, .2, .2, .2, .2, .3, .4, .3, .2, .1, .3, .2, .1],
    'IBM' :   [.3, .3, .3, .3, .3, .1, .4, .3, .2, .1, .3, .2, .1],
    'GLD' :   [.3, .3, .3, .3, .3, .3, .2, .4, .6, .8, .4, .6, .8],
    '_CASH' : [.2, .2, .2, .2, .2, .3, .0, .0, .0, .0, .0, .0, .0],}

sample_alloc = DataMatrix(vals, index=dates)    

#sample_historic setup
# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = tu.ymd2epoch(2008,1,2)
tsend = tu.ymd2epoch(2008,12,31)
symbols = sample_alloc.cols()
symbols.pop()

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume
sample_historic = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)

funds=simulator.quickSim(sample_alloc,sample_historic,1000)

#plot funds
plt.clf()
plt.plot(funds.index,funds.values)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
