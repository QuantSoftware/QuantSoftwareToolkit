# # quickSim.py # # A simulator that quickly produces a fund history.
# # Drew Bratcher #

def quickSim(alloc,historic,start_cash):

    #imports
    from pylab import *
    from qstkutil import DataAccess as da
    from qstkutil import timeutil as tu
    from pandas import *

    #check each row in alloc
    for row in range(0,len(alloc.values[:,0])):
        if(abs(alloc.values[row,:].sum()-1)>.1):
            print alloc.values[row,:]
            print alloc.values[row,:].sum()
            print "warning, alloc row "+str(row)+" does not sum to one"
  
    #fix invalid days
    historic=historic.fill(method='backfill')
    
    #add cash column
    historic['_CASH'] = ones((len(historic.values[:,0]),1), dtype=int)
    
    closest=historic[historic.index<=alloc.index[0]]
    fund_ts=Series([start_cash], index=[closest.index[-1]])
    shares=alloc.values[0,:]*fund_ts.values[-1]/closest.values[-1,:]
    
    #compute all trades
    for i in range(1,len(alloc.values[:,0])):
        #get closest date(previous date)
        closest=historic[historic.index<=alloc.index[i]]
        #for loop to calculate fund daily (without rebalancing)
        for date in closest[closest.index>fund_ts.index[-1]].index:
            #compute and record total fund value (Sum(closest close * stocks))
            fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))
        #distribute fund in accordance with alloc
        shares=alloc.values[i,:]*fund_ts.values[-1]/closest.xs(closest.index[-1])

    #compute fund value for rest of historic data with final share distribution  (currently buggy for some reason...)
#    for date in historic[historic.index>alloc.index[-1]].index:
#        fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))  

    #return fund record
    return fund_ts
