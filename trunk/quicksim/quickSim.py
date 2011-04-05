# 
# quickSim.py 
# 
# A module that contains simulators that quickly produce a fund history.
# 
#

#python imports
from pylab import *
from pandas import *
import os
import matplotlib.pyplot as plt
import time
import cPickle
import sys
import calendar
import datetime as dt

#qstk imports
import qstkutil.tsutil as tsu
import qstkutil.dateutil as du
import qstkutil.DataAccess as da

def quickSim(alloc,historic,start_cash):
	"""
	@summary Quickly back tests an allocation for certain historical data, using a starting fund value
	@param alloc: DataMatrix containing timestamps to test as indices and Symbols to test as columns, with _CASH symbol as the last column
	@param start_cash: integer specifing initial fund value
	@return funds: TimeSeries with fund values for each day in the back test
	@rtype TimeSeries
	"""
	
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
	
	#compute all trade
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

def alloc_backtest(alloc,start):
	"""
	@summary: Back tests an allocation from a pickle file. Uses a starting portfolio value of start.
	@param alloc: Name of allocation pickle file. Pickle file contains a DataMatrix with timestamps as indexes
	and stock symbols as columns, with the last column being the _CASH symbol, indicating how much
	of the allocation is in cash.
	@param start: integer specifying the starting value of the portfolio
	@return funds: List of fund values indicating the value of the portfolio throughout the back test.
	@rtype timeseries
	"""
	
	#read in alloc table from command line arguements
	alloc_input_file=open(alloc,"rb")
	alloc=cPickle.load(alloc_input_file)
	
	# Get the data from the data store
	dataobj=da.DataAccess('Norgate')
	historic = dataobj.get_data(list(alloc.index), list(alloc.cols()[0:-1]), "close")
	
	#backtest
	funds=quickSim(alloc,historic,int(start))
	
	return funds

def strat_backtest(strat,start,end,num,diff,startval):
	"""
	@summary: Back tests a strategy defined in a python script that takes in a start
	and end date along with a starting value. 
	@param strat: filename of python script strategy
	@param start: starting date in a datetime object
	@param end: ending date in a datetime object
	@param num: number of tests to perform
	@param diff: offset in days of the tests
	@param startval: starting value of fund during back tests
	@return fundsmatrix: Datamatrix of fund values returned from each test
	@rtype datanatrix
	"""
	fundsmatrix=[]
	startdates=du.getNextNNYSEdays(start,num,dt.timedelta(hours=16))
	enddates=du.getNextNNYSEdays(end,num,dt.timedelta(hours=16))
	for i in range(0,len(enddates)):
		os.system('python '+strat+' '+startdates[i].strftime("%m-%d-%Y")+' '+enddates[i].strftime("%m-%d-%Y")+' temp_alloc.pkl')
		funds=alloc_backtest('temp_alloc.pkl',startval)
		fundsmatrix.append(funds)
	return fundsmatrix
    
if __name__ == "__main__":
    #
	# CmdlnQuickSim
	#
	# A function which runs a quick sim on an allocation provided via command line,
	# along with a starting cash value
	# 
	# sample call:
	# python quickSim.py -a 'alloc_file.pkl' 1000 'fund_output.pkl'
	#
	# python quickSim.py -s 'strategy.py' '2/2/2007' '2/2/2009' 10 1 1000 'fund_output.pkl' 
	#
	# Drew Bratcher
	#

	if(sys.argv[1]=='-a'):
		funds=alloc_backtest(sys.argv[2],sys.argv[3])
		output=open(sys.argv[4],"rb")
		cPickle.dump(funds,output)
	elif(sys.argv[1]=='-s'):
		t = map(int, sys.argv[3].split('-'))
		startday= dt.datetime(t[2],t[0],t[1])
		t = map(int, sys.argv[4].split('-'))
		endday = dt.datetime(t[2],t[0],t[1])
		fundsmatrix=strat_backtest(sys.argv[2],startday,endday,int(sys.argv[5]),sys.argv[6],sys.argv[7])
		output=open(sys.argv[8],"w")
		cPickle.dump(fundsmatrix,output)
	else:
		print 'invalid command line call'
		print 'use python quickSim.py -a alloc_pkl start_value output_pkl'
		print 'or python quickSim.py -s strategy start_date end_date number_of_tests test_offset_in_days start_value output_pkl'
