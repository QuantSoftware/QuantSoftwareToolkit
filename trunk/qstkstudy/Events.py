import pandas 
from qstkutil import DataAccess as da
import numpy as np
import math
import qstkutil.dateutil as du
import datetime as dt
import qstkutil.DataAccess as da

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""
# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
closefield = "close"
volumefield = "volume" # adj_open, adj_close, adj_high, adj_low, close, volume
window = 10
def findEvents(symbols, startday,endday):
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	dataobj = da.DataAccess('Norgate')
	close = dataobj.get_data(timestamps, symbols, closefield)
	print close
	close = (close.fillna()).fillna(method='backfill')
	for symbol in symbols:
	    close[symbol][close[symbol]>= 1.0] = np.NAN
	    for i in range(1,len(close[symbol])):
	        if np.isnan(close[symbol][i-1]) and close[symbol][i] < 1.0 :#(i-1)th was > $1, and (i)th is <$1
             		close[symbol][i] = 1.0 #overwriting the price by the bit
	    close[symbol][close[symbol]< 1.0] = np.NAN
	return close

#print findEvents(['IBM','MTD'],[2008,1,1],[2010,1,1])['MTD']
def moneyRatioIndex(signed_moneyflow,window):
        MRI = []
        for i in range(0,len(signed_moneyflow)-window +1):
                slice = signed_moneyflow[i:i + window]
                PMF = 0 #Total Positive money flow
                NMF = 0.00000001 #Total Negative money flow. Div by Zero possibility.
                for money in slice:
                        if money > 0:   PMF +=money
                        else: NMF +=money
                mr = PMF/(-1.0*NMF)
                MRI.append(100 - 100/(1+mr))
        return MRI
def findMRIEvents(symbols, startdate,enddate):
	tsstart = tu.ymd2epoch(startdate[0],startdate[1],startdate[2])
	tsend = tu.ymd2epoch(enddate[0],enddate[1],enddate[2])
	volume = ps.getDataMatrixFromData(storename,volumefield,symbols,tsstart,tsend)
	close = ps.getDataMatrixFromData(storename,closefield,symbols,tsstart,tsend)
	close = (close.fillna()).fillna(method='backfill')
	volume = (volume.fillna()).fillna(method='backfill')
	moneyflow = close.copy() # Copy to retain the structure
	for symbol in symbols:
		moneyflow_result = close[symbol].values * volume[symbol].values
		close_parity_result = [math.copysign(1.0,x) for x in close[symbol].values[1:]-close[symbol].values[:-1]]
		signed_moneyflow_result = [x*y for x,y in zip(close_parity_result,moneyflow_result[1:])]
		MRI_result = moneyRatioIndex(signed_moneyflow_result,window)
		signal_result =[1 if x<=20 else -1 if x>=80 else np.nan for x in MRI_result]
		for j in range(0, len(moneyflow)):
			if j < len(signal_result):
				moneyflow[symbol].values[j] = signal_result[j]
			else:
				moneyflow[symbol].values[j] = np.nan
	return moneyflow
	
