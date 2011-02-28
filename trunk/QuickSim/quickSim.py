# 
# quickSim.py 
# 
# A module that contains simulators that quickly produce a fund history.
# 
# Drew Bratcher 
#

from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *

import quickSim as simulator
import matplotlib.pyplot as plt
import time as t
import cPickle
import sys
import calendar

def quickSim(alloc,historic,start_cash):

    #original quick simulator
    #not designed to handle shorts

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
    cash_values=DataMatrix([shares*closest.values[-1,:]],index=[closest.index[-1]])
    
    #compute all trades
    for i in range(1,len(alloc.values[:,0])):
        #get closest date(previous date)
        closest=historic[historic.index<=alloc.index[i]]
        #for loop to calculate fund daily (without rebalancing)
        for date in closest[closest.index>fund_ts.index[-1]].index:
        	#compute and record total fund value (Sum(closest close * stocks))
            fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))
            cash_values=cash_values.append(DataMatrix([shares*closest.xs(date)],index=[date]))
        #distribute fund in accordance with alloc
        shares=alloc.values[i,:]*fund_ts.values[-1]/closest.xs(closest.index[-1])

    #compute fund value for rest of historic data with final share distribution
    for date in historic[historic.index>alloc.index[-1]].index:
    	if date in closest.index :
        	fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))  

    #return fund record
    return fund_ts
    
def computeShort(arr):
	tally=0
	for i in range(0,len(arr)-1):
		if arr[i]<0:
			tally=tally+arr[i]
	return abs(tally)

def computeLong(arr,fundval):
	tally=0
	for i in range(0,len(arr)-1):
		if arr[i]>0:
			tally=tally+arr[i]
	return tally
	
def computeLeverage(arr,fundval):
	if fundval==0:
		return 0
	return (computeLong(arr,fundval)-computeShort(arr))/fundval
	
def shortingQuickSim(alloc,historic,start_cash,leverage):
    #shortingQuickSim
    #
    #designed to handle shorts
    #keeps track of leverage keeping it within paramaterized value
    #
	#ignore alloc cash column
	del alloc['_CASH']
	#fix invalid days
	historic=historic.fill(method='backfill') 
    
    #compute first trade
	closest=historic[historic.index<=alloc.index[0]]
	fund_ts=Series([start_cash], index=[closest.index[-1]])
	shares=alloc.values[0,:]*fund_ts.values[-1]/closest.values[-1,:]
	cash_values=DataMatrix([shares*closest.values[-1,:]],index=[closest.index[-1]])
    
    #compute all trades
	for i in range(1,len(alloc.values[:,0])):
		#check leverage
		this_leverage=computeLeverage(alloc.values[0,:])
		if this_leverage>leverage:
			print 'Warning, leverage of ',this_leverage,' reached, exceeds leverage limit of ',leverage,'\n'
		#get closest date(previous date)
		closest=historic[historic.index<=alloc.index[i]]
		#for loop to calculate fund daily (without rebalancing)
		for date in closest[closest.index>fund_ts.index[-1]].index:
        	#compute and record total fund value (Sum(closest close * stocks))
			fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))
			cash_values=cash_values.append(DataMatrix([shares*closest.xs(date)],index=[date]))
        #distribute fund in accordance with alloc
		shares=alloc.values[i,:]*fund_ts.values[-1]/closest.xs(closest.index[-1])

    #compute fund value for rest of historic data with final share distribution
	for date in historic[historic.index>alloc.index[-1]].index:
		if date in closest.index :
			fund_ts=fund_ts.append(Series([(closest.xs(date)*shares).sum()],index=[date]))  

    #return fund record
	return fund_ts
    
    
if __name__ == "__main__":
    #
	# CmdlnQuickSim
	#
	# A function which runs a quick sim on an allocation provided via command line,
	# along with a starting cash value
	# 
	# sample call:
	# python quickSim.py 'alloc_file.pkl' 1000 'fund_output.pkl'
	#
	# Drew Bratcher
	#


	#read in alloc table from command line arguements
	alloc_input_file=open(sys.argv[1],"rb")
	alloc=cPickle.load(alloc_input_file)
	
	#setup historic table using command line arguements
	symbols = alloc.cols()
	symbols = symbols[0:-1];
	#Set start and end boundary times.  They must be specified in Unix Epoch
	t = map(int,str(alloc.index[0]).split('-'))
	tsstart=tu.ymd2epoch(t[0],t[1],t[2])
	t = map(int,str(alloc.index[-1]).split('-'))
	tsend = tu.ymd2epoch(t[0],t[1],t[2])
	
	# Get the data from the data store
	storename = "Norgate" # get data from our daily prices source
	fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume
	
	historic = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)
	
	funds=simulator.quickSim(alloc,historic,int(sys.argv[2]))
	
	print str(sys.argv[3])
	output=open(sys.argv[3],"wb")
	cPickle.dump(funds, output)
