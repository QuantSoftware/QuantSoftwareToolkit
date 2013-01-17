#
# timeseries-ex.py
#
# A short example that shows how to read stock price data from our data store.
#
# Tucker Balch
#

# imports
import matplotlib.pyplot as plt
from pylab import *
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import timeutil as tu
from QSTK.qstkutil import timeseries as ts

# Set the list of stocks for us to look at
symbols= list()
symbols = list(np.loadtxt('example-syms.csv',dtype='str',delimiter=',',
	comments='#',skiprows=0))
symbols.append("IBM")
#symbols.append("BLAH")  # uncomment this line to see what happens

# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = tu.ymd2epoch(2008,1,1)
tsend = tu.ymd2epoch(2010,1,1)

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume
adjcloses = ts.getTSFromData(storename,fieldname,symbols,tsstart,tsend)

# Print out a bit of the data
print "The prices are: "
print symbols
print adjcloses.values

# Convert the timestamps to dates for the plot
dates = []
for ts in adjcloses.timestamps:
    dates.append(tu.epoch2date(ts))

# Normalize the prices
normdat = adjcloses.values/adjcloses.values[0,:]

# Plot the prices
plt.clf()
for i in range(0,size(normdat[0,:])):
        plt.plot(dates,normdat[:,i])

plt.legend(symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.draw()
savefig("fig1.pdf", format='pdf')
