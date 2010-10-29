import matplotlib.pyplot as plt
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
import pandas

# Set the list of stocks for us to look at
# symbols= list()
# symtoplot = 'VZ'
# symbols.append(symtoplot)
# symbols.append('IBM')
# symbols.append('GOOG')

symbols = list(np.loadtxt('allsyms.csv',dtype='str',delimiter=',',
        comments='#',skiprows=0))

# Set start and end boundary times.  They must be specified in Unix Epoch
tsstart = tu.ymd2epoch(2008,1,1)
tsend = tu.ymd2epoch(2008,12,31)

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "close" # adj_open, adj_close, adj_high, adj_low, close, volume
closes = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)

cldata = closes.values
cldata[cldata<=4.0]  = 1.0
cldata[cldata>4.0]   = 0
cldata[isnan(cldata)]= 0
lows = sum(cldata,axis=0)

lownames = array(closes.cols())[lows>0]

f = open('below4.csv', 'w')
for sym in lownames:
	f.write(sym + '\n')
f.close()
