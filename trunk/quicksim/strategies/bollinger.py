#imports

#creates an allocation pkl based on bollinger strategy
def create(symbols, start, end, start_fund, lookback, spread, high, low, bet, duration):
	print "Running a Bollinger strategy..."
	#get historic data for period
	#create allocation table
	#for each day
	#	compute returns
	#	compute deviation over lookback
	#	find best stocks to short and long
	#	throw out any bets that have lasted the duration/other exit strategy
	#	for number of high/low
	#		compute allocation to make appropriate bets
	#	print allocation row
	#print table
