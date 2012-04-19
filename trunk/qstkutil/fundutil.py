import qstkutil.tsutil as tsu

def getWinningDays(fund_ts):
	"""
	@summary Returns percentage of winning days in fund time series
	@param fund_ts: pandas time series of daily fund values
	@return Percentage of winning days over fund time series
	"""
	return tsu.getWinningDays(tsu.daily(fund_ts))

def getMaxDrawDown(fund_ts):
	"""
	@summary Returns max draw down of fund time series (in percentage)
	@param fund_ts: pandas time series of daily fund values
	@return Max draw down of fund time series
	"""
	return tsu.getMaxDrawDown(tsu.daily(fund_ts))

def getSortinoRatio(fund_ts):
	"""
	@summary Returns daily computed Sortino ratio of fund time series
	@param fund_ts: pandas time series of daily fund values
	@return Sortino ratio of fund time series
	"""
	return tsu.getSortinoRatio(tsu.daily(fund_ts))

def getSharpeRatio(fund_ts):
	"""
	@summary Returns daily computed Sharpe ratio of fund time series
	@param fund_ts: pandas time series of daily fund values
	@return  Sharpe ratio of  fund time series
	"""
	return tsu.getSharpeRatio(tsu.daily(fund_ts))



