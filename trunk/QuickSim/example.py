#
# quickSim.py
#
# A simulator that quickly produces a fund history.
#
# Drew Bratcher
#

#sample_alloc setup
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quickSim as simulator
import matplotlib.pyplot as plt
    
dates= [tu.ymd2epoch(2008,1,2),
        tu.ymd2epoch(2008,1,21),
        tu.ymd2epoch(2008,2,1),
        tu.ymd2epoch(2008,3,1),
        tu.ymd2epoch(2008,4,1),
        tu.ymd2epoch(2008,5,1),
        tu.ymd2epoch(2008,6,1),
        tu.ymd2epoch(2008,7,1),
        tu.ymd2epoch(2008,8,1),
        tu.ymd2epoch(2008,9,1),
        tu.ymd2epoch(2008,10,1),
        tu.ymd2epoch(2008,11,1),
        tu.ymd2epoch(2008,12,1)]

vals={
    'XOM' :   [.2, .2, .2, .2, .2, .3, .4, .3, .2, .1, .3, .2, .1],
    'IBM' :   [.3, .3, .3, .3, .3, .1, .4, .3, .2, .1, .3, .2, .1],
    'GLD' :   [.3, .3, .3, .3, .3, .3, .2, .4, .6, .8, .4, .6, .8],
    '_CASH' : [.2, .2, .2, .2, .2, .3, .0, .0, .0, .0, .0, .0, .0],}

sample_alloc = DataMatrix(vals, index=dates)    

#sample_historic setup
# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = sample_alloc.index[0]
tsend = sample_alloc.index[-1]
symbols = sample_alloc.cols()
symbols.pop()

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume
sample_historic = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)

funds=simulator.quickSim(sample_alloc,sample_historic,1000)

plt.clf()
plt.plot(funds.index,funds.values)
set_xticklabels(size='xx-small')
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
