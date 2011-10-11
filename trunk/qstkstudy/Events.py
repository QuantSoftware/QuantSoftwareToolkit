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
# Available field names: open, close, high, low, close, actual_close, volume
closefield = "close"
volumefield = "volume"
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
