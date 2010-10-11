import matplotlib.pyplot as plt
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
import pandas

# Set the list of stocks for us to look at
symbols= list()
symtoplot = 'VZ'
symbols.append(symtoplot)

# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = tu.ymd2epoch(2010,1,1)
tsend = tu.ymd2epoch(2011,1,1)

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume
adjcloses = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)

adjcloses = adjcloses.fill()
adjcloses = adjcloses.fill(method='backfill')

means = pandas.rolling_mean(adjcloses,20,min_periods=20)

# Plot the prices
plt.clf()

plot(adjcloses.index,adjcloses[symtoplot].values,label=symtoplot)
plot(adjcloses.index,means[symtoplot].values)
plt.legend([symtoplot,'Moving Avg.'])
plt.ylabel('Adjusted Close')

savefig("movingavg-ex.png", format='png')
