import qstkutil.dateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
import pandas

print pandas.__version__

#
# Prepare to read the data
#
symbols = ["AAPL","GLD","GOOG","SPY","XOM"]
startday = dt.datetime(2007,1,1)
endday = dt.datetime(2010,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

dataobj = da.DataAccess('Norgate')
voldata = dataobj.get_data(timestamps, symbols, "volume",verbose=True)
close = dataobj.get_data(timestamps, symbols, "close",verbose=True)
actualclose = dataobj.get_data(timestamps, symbols, "actual_close",verbose=True)

#
# Plot the adjusted close data
#
plt.clf()
newtimestamps = close.index
pricedat = close.values # pull the 2D ndarray out of the pandas object
plt.plot(newtimestamps,pricedat)
plt.legend(symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
savefig('adjustedclose.pdf',format='pdf')

#
# Plot the normalized closing data
#
plt.clf()
normdat = pricedat/pricedat[0,:]
plt.plot(newtimestamps,normdat)
plt.legend(symbols)
plt.ylabel('Normalized Close')
plt.xlabel('Date')
savefig('normalized.pdf',format='pdf')

#
# Plot daily returns
#
plt.clf()
plt.cla()
tsu.returnize0(normdat)
plt.plot(newtimestamps[0:50],normdat[0:50,3]) # SPY 50 days
plt.plot(newtimestamps[0:50],normdat[0:50,4]) # XOM 50 days
plt.axhline(y=0,color='r')
plt.legend(['SPY','XOM'])
plt.ylabel('Daily Returns')
plt.xlabel('Date')
savefig('rets.pdf',format='pdf')

#
# Scatter plat
#
plt.clf()
plt.cla()
plt.scatter(normdat[:,3],normdat[:,4],c='blue') # SPY v XOM
plt.ylabel('XOM')
plt.xlabel('SPY')
savefig('scatter.pdf',format='pdf')

