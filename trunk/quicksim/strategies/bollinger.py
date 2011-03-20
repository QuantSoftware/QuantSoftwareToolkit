#imports
from qstkutil import DataAccess
import datetime

#creates an allocation pkl based on bollinger strategy
def create(symbols, start, end, start_fund, lookback, spread, high, low, bet, duration, output):
	print "Running a Bollinger strategy..."

	#get historic data for period
	da=DataAccess.DataAccess('norgate')
	date=start.split('-')
	tsstart=datetime.datetime(date[0],date[1],date[2])
	date=end.split('-')
	tsend=datetime.datetime(date[0],date[1],date[2])
	num_days=(tsend-tsstart).days
	ts_list=[ tsstart+datetime.timedelta(days=x) for x in range(0,num_days) ]
	da.get_data(ts_list, symbols, "close")	
	
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
