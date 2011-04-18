#
# bollinger.py
#
# A module which contains a bollinger strategy.
#
#

#python imports
import cPickle
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import datetime as dt
import os

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du
import qstkutil.bollinger as boil

#simple version
def createStrat(adjclose, timestamps, lookback, highthresh, lowthresh):
	alloc=DataMatrix(index=[timestamps[0]],columns=adjclose.columns, data=[zeros(len(adjclose.columns))])
	bs=boil.calcbvals(adjclose, timestamps, adjclose.columns, lookback)
	for day in timestamps:
		vals=zeros(10, len(adjclose.columns))
		for stock in bs(day):
			if(stock>1):
				vals[0:10,stock]=-.05
			elif(stock<-1):
				vals[0:10,stock]=.05
		alloc.append(DataMatrix(index=[day],columns=adjclose.columns,data=[vals[0]]))
		vals.remove(0)
		vals.append(zeros(len(adjclose[day])))

#creates an allocation pkl based on bollinger strategy
def create(symbols, start, end, start_fund, lookback, spread, high, low, bet, duration, output):
	print "Running a Bollinger strategy..."

	# Get historic data for period
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(start,end,timeofday)
	dataobj = da.DataAccess('Norgate')
	historic = dataobj.get_data(timestamps, symbols, "close")
	
	#create allocation table
	
	
	#for each day
	for i in range(0,num_days):
		#compute returns
		#compute deviation over lookback
		#find best stocks to short and long
		#throw out any bets that have lasted the duration/other exit strategy
		#for number of high/low
		for k in range(0,high):
			#compute allocation to make appropriate bets
			print 'high'
		for k in range(0,low):
			#compute allocation...
			print 'low'
		#print allocation row
	#print table to file

if __name__ == "__main__":
	#Usage: python bollinger.py '1-1-2004' '1-1-2009' 'alloc.pkl'
	print "Running Bollinger strategy starting "+sys.argv[1]+" and ending "+sys.argv[2]+"."
	
	#Run S&P500 for thresholds 1 and -1 in simple version for lookback of 10 days
	symbols = list(np.loadtxt(os.environ['QS']+'/quicksim/strategies/S&P500.csv',dtype='str',delimiter=',',comments='#',skiprows=0))
	
	t=map(int,sys.argv[1].split('-'))
	startday = dt.datetime(t[2],t[0],t[1])
	t=map(int,sys.argv[2].split('-'))
	endday = dt.datetime(t[2],t[0],t[1])
	
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(startday,endday,timeofday)
	
	dataobj=da.DataAccess('Norgate')
	intersectsyms=list(set(dataobj.get_all_symbols())&set(symbols))
	badsyms=[]
	if size(intersectsyms)<size(symbols):
		badsyms=list(set(symbols)-set(intersectsyms))
		print "bad symms:"
		print badsyms
	for i in badsyms:
		index=symbols.index(i)
		symbols.pop(index)
	historic = dataobj.get_data(timestamps,symbols,"close")
	
	alloc=createStrat(historic,timestamps,10,1,-1)
	
	output=open(sys.argv[3],"wb")
	cPickle.dump(alloc,output)
