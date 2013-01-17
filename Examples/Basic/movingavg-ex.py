import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *

#
# Prepare to read the data
#
symbols = ["AAPL","GLD","GOOG","$SPX","XOM"]
startday = dt.datetime(2008,1,1)
endday = dt.datetime(2009,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

dataobj = da.DataAccess('Norgate')
voldata = dataobj.get_data(timestamps, symbols, "volume")
adjcloses = dataobj.get_data(timestamps, symbols, "close")
actualclose = dataobj.get_data(timestamps, symbols, "actual_close")

adjcloses = adjcloses.fillna()
adjcloses = adjcloses.fillna(method='backfill')

means = pandas.rolling_mean(adjcloses,20,min_periods=20)

# Plot the prices
plt.clf()

symtoplot = 'AAPL'
plot(adjcloses.index,adjcloses[symtoplot].values,label=symtoplot)
plot(adjcloses.index,means[symtoplot].values)
plt.legend([symtoplot,'Moving Avg.'])
plt.ylabel('Adjusted Close')

savefig("movingavg-ex.png", format='png')
