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

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du

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
