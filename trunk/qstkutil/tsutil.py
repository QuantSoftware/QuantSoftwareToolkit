import cPickle
import math
import datetime as dt
import numpy as np
from pylab import *
from pandas import *
from qstkutil import dateutil
from math import sqrt
from copy import deepcopy

def daily(funds):
	nd=deepcopy(funds)
	nd[0]=0
	for i in range(1,len(funds)):
		nd[i]=funds[i]/funds[i-1]-1
	return(nd)

def monthly(funds):
	funds2=[]
	years=dateutil.getYears(funds)
	for year in years:
		months=dateutil.getMonths(funds,year)
		for month in months:
			funds2.append(funds[dateutil.getFirstDay(funds,year,month)])
	return(daily(funds2))

def averageMonthly(funds):
	rets=daily(funds)
	x=0
	years=dateutil.getYears(funds)
	averages=[]
	for year in years:
		months=dateutil.getMonths(funds,year)
		for month in months:
			avg=0
			count=0
			days=dateutil.getDays(funds,year,month)
			for day in days:
				avg+=rets[x]
				x+=1
				count+=1
			averages.append(float(avg)/count)
	return(averages)	

def fillforward(nd):
	"""
	@summary Removes NaNs from a 2D array by scanning forward in the 
	1st dimension.  If a cell is NaN, the value above it is carried forward.
	@param nd: the array to fill forward
	@return the array is revised in place
	"""
	for col in range(nd.shape[1]):
		for row in range(1,nd.shape[0]):
			if math.isnan(nd[row,col]):
				nd[row,col] = nd[row-1,col]

def fillbackward(nd):
	"""
	@summary Removes NaNs from a 2D array by scanning backward in the 
	1st dimension.  If a cell is NaN, the value above it is carried backward.
	@param nd: the array to fill backward
	@return the array is revised in place
	"""
	for col in range(nd.shape[1]):
		for row in range(nd.shape[0]-2,-1,-1):
			if math.isnan(nd[row,col]):
				nd[row,col] = nd[row+1,col]

def returnize0(nd):
	"""
	@summary Computes stepwise (usually daily) returns relative to 0, where
	0 implies no change in value.
	@return the array is revised in place
	"""
	nd[1:,:] = (nd[1:,:]/nd[0:-1]) - 1
	nd[0,:] = np.zeros(nd.shape[1])

def returnize1(nd):
	"""
	@summary Computes stepwise (usually daily) returns relative to 1, where
	1 implies no change in value.
	@param nd: the array to fill backward
	@return the array is revised in place
	"""
	nd[1:,:] = (nd[1:,:]/nd[0:-1])
	nd[0,:] = np.ones(nd.shape[1])

def getRatio(funds):
	d=daily(funds)
	avg=float(sum(d))/len(d)
	std=0
	for a in d:
		std=std+float((float(a-avg))**2)
	std=sqrt(float(std)/(len(d)-1))
	return(avg/std)

def getYearRatio(funds,year):
	funds2=[]
	for date in funds.index:
		if(date.year==year):
			funds2.append(funds[date])
	return(getRatio(funds2))

def getSharpeRatio( naRets, fFreeReturn=0.00 ):
	"""
	@summary Returns the daily Sharpe ratio of the returns.
	@param naRets: 1d numpy array or list of daily returns
	@param fFreeReturn: risk free returns, default is 3%
	@return Annualized rate of return, not converted to percent
	"""
	
	fDev = np.std( naRets - 1 )
	fMean = np.mean( naRets - 1 )
	
	''' Convert to yearly standard deviation '''
	fSharpe = (fMean * 252 - fFreeReturn) / ( fDev * sqrt(252) )
	
	#print fDev, fMean, fSharpe

	return fSharpe

def getRorAnnual( naRets ):
	"""
	@summary Returns the rate of return annualized.  Assumes len(naRets) is number of days.
	@param naRets: 1d numpy array or list of daily returns
	@return Annualized rate of return, not converted to percent
	"""

	''' Calculate final value of investment of 1.0 '''
	fInv = 1.0
	for fReturn in naRets:
		fInv = fInv * fReturn
	
	fRorYtd = fInv - 1.0	
	
	print ' RorYTD =', fInv, 'Over days:', len(naRets)
	
	return ( (1.0 + fRorYtd)**( 1.0/(len(naRets)/365.0) ) ) - 1.0

def getPeriodicRets( dmPrice, sOffset ):
	"""
	@summary Reindexes a DataMatrix price array and returns the new periodic returns.
	@param dmPrice: DataMatrix of stock prices
	@param sOffset: Offset string to use, choose from _offsetMap in pandas/core/datetools.py
	                e.g. 'EOM', 'WEEKDAY', 'W@FRI', 'A@JAN'.  Or use a pandas DateOffset.
	"""	
	
	''' Could possibly use DataMatrix.asfreq here '''
	''' Use pandas DateRange to create the dates we want, use 4:00 '''
	drNewRange = DateRange(dmPrice.index[0], dmPrice.index[-1], timeRule=sOffset) + DateOffset(hours=16)
	
	dmPrice = dmPrice.reindex( drNewRange )  

	returnize1( dmPrice.values )
	
	''' Do not leave return of 1.0 for first time period: not accurate '''
	return dmPrice[1:]

def getReindexedRets( naRets, lPeriod ):
	"""
	@summary Reindexes returns using the cumulative product. E.g. if returns are 1.5 and 1.5, a period of 2 will
	         produce a 2-day return of 2.25.  Note, these must be returns centered around 1.
	@param naRets: Daily returns of the various stocks (using returnize1)
	@param lPeriod: New target period.
	@note: Note that this function does not track actual weeks or months, it only approximates with trading days.
	       You can use 5 for week, or 21 for month, etc.
	"""	
	naCumData = np.cumprod(naRets, axis=0)

	lNewRows =(naRets.shape[0]-1) / (lPeriod)
	''' We compress data into height / lPeriod + 1 new rows '''
	for i in range( lNewRows ):
		lCurInd = -1 - i*lPeriod
		''' Just hold new data in same array, new return is cumprod on day x / cumprod on day x-lPeriod '''
		naCumData[-1 - i,:] = naCumData[lCurInd,:] / naCumData[lCurInd - lPeriod,:] 
		''' Select new returns from end of cumulative array '''
	
	return naCumData[-lNewRows:, ]

		
def getOptPort( naRets, fTarget, lPeriod=1, naLower=None, naUpper=None, lNagDebug=0 ):
	"""
	@summary Returns the Markowitz optimum portfolio for a specific return.
	@param naRets: Daily returns of the various stocks (using returnize1)
	@param fTarget: Target return, i.e. 0.04 = 4% per period
	@param lPeriod: Period to compress the returns to, e.g. 7 = weekly
	@param naLower: List of floats which corresponds to lower portfolio% for each stock
	@param naUpper: List of floats which corresponds to upper portfolio% for each stock 
	@return tuple: (weights of portfolio, min possible return, max possible return)
	"""
	
	''' Attempt to import library '''
	try:
		pass
		import nagint as nag
	except ImportError:
		print 'Could not import NAG library, make sure nagint.so is in your python path'
		return ([], 0, 0)
	
	''' Get number of stocks '''
	lStocks = naRets.shape[1]
	
	''' If period != 1 we need to restructure the data '''
	if( lPeriod != 1 ):
		naRets = getReindexedRets( naRets, lPeriod)
	
	''' Calculate means and covariance '''
	naAvgRets = np.average( naRets, axis=0 )
	naCov = np.cov( naRets, rowvar=False )
	
	''' Special case for None == fTarget, simply return average returns and cov '''
	if( fTarget is None ):
		return naAvgRets, np.std(naRets, axis=0)
	
	''' Calculate upper and lower limits of variables as well as constraints '''
	if( naUpper is None ): 
		naUpper = np.ones( lStocks )  # max portfolio % is 1
	
	if( naLower is None ): 
		naLower = np.zeros( lStocks ) # min is 0, set negative for shorting
	''' Two extra constraints for linear conditions, result = desired return, and sum of weights = 1 '''
	naUpper = np.append( naUpper, [fTarget, 1.0] )
	naLower = np.append( naLower, [fTarget, 1.0] )
	
	''' Initial estimate of portfolio '''
	naInitial = [1.0/lStocks]*lStocks
	
	''' Set up constraints matrix, composed of expected returns in row one, unity row in row two '''
	naConstraints = np.vstack( (naAvgRets, np.ones(lStocks)) )

	''' Get portfolio weights, last entry in array is actually variance '''
	try:
		naReturn = nag.optPort( naConstraints, naLower, naUpper, naCov, naInitial, lNagDebug )
	except RuntimeError:
		print 'NAG Runtime error with target: %.02lf'%(fTarget)
		return ( naInitial, sqrt( naCov[0][0] ) )  #return semi-junk to not mess up the rest of the plot

	''' Calculate stdev of entire portfolio to return, what NAG returns is slightly different '''
	fPortDev = np.std( np.dot(naRets, naReturn[0,0:-1]) )
	
	''' Show difference between above stdev and sqrt NAG covariance, possibly not taking correlation into account '''
	#print fPortDev / sqrt(naReturn[0,-1]) 

	''' Return weights and stdDev of portfolio.  note again the last value of naReturn is NAG's reported variance '''
	return (naReturn[0,0:-1], fPortDev)


		
def stockFilter( dmPrice, dmVolume, fNonNan=0.9, fPriceVolume=1000*1000 ):
	"""
	@summary Returns the list of stocks filtered based on various criteria.
	@param dmPrice: DataMatrix of stock prices
	@param dmVolume: DataMatrix of stock volumes
	@param fNonNan: Optional non-nan percent, default is .9
	@param fPriceVolume: Optional price*volume, default is 1,000,000
	@return list of stocks which meet the criteria
	"""
	
	lsRetStocks = list( dmPrice.columns )

	print type(lsRetStocks)

	for sStock in dmPrice.columns:
		print sStock
		fValid = 0.0
		
		''' loop through all dates '''
		for dtDate in dmPrice.index:
			''' Count null (nan/inf/etc) values '''
			fPrice = dmPrice[sStock][dtDate]
			if( not isnull(fPrice) ):
				fValid = fValid + 1
				''' else test price volume '''
				fVol = dmVolume[sStock][dtDate]
				if( not isnull(fVol) and fVol * fPrice < fPriceVolume ):
					lsRetStocks.remove( sStock )
					break

		''' Remove if too many nan values '''
		if( fValid / len(dmPrice.index) < fNonNan and sStock in lsRetStocks ):
			lsRetStocks.remove( sStock )

	return lsRetStocks








