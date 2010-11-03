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

# alloc is a datamatrix
# historic is a datamatrix
# alloc and historic have the same start and end dates
# alloc has as many columns as symbols in historic + 1 column for cash

def sim(alloc,historic,start_cash):

    #imports
    from pylab import *
    from qstkutil import DataAccess as da
    from qstkutil import timeutil as tu
    from pandas import *

    #check each row in alloc
    for row in range(0,len(alloc.values[:,0])):
        if(alloc.values[row,:].sum()!=1):
            print alloc.values[row,:]
            print alloc.values[row,:].sum()
            print "warning, alloc row "+row+" does not sum to one"
  
    #fix invalid days
    historic=historic.fill(method='backfill')
    
    #add cash column
    historic['_CASH'] = ones((len(historic.values[:,0]),1), dtype=int)
    
    closest=historic[historic.index<=tu.epoch2date(alloc.index[0])]
    fund_ts=Series([start_cash], index=[closest.index[-1]])
    shares=alloc.values[0,:]*fund_ts.values[-1]/closest.values[-1,:]
    
    #compute all trades
    for i in range(1,len(alloc.values[:,0])):
        #get closest date(previous date)
        closest=historic[historic.index<=tu.epoch2date(alloc.index[i])]
        #for loop to calculate fund daily (without rebalancing)
        for date in closest[closest.index>fund_ts.index[-1]].index:
            #compute and record total fund value (Sum(closest close * stocks))
            fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))
        #distribute fund in accordance with alloc
        shares=alloc.values[i,:]*fund_ts.values[-1]/closest.xs(closest.index[-1])

    #compute fund value for rest of historic data with final share distribution 
    for date in historic[historic.index>tu.epoch2date(alloc.index[-1])].index:
        fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))  

    #print fund record
    print "Funds:"
    print fund_ts


#add sanity checks (warnings)
#dont allow negatives for now
