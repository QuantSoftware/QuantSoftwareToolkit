'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on September, 12, 2011

@author: Tucker Balch and Shreyas Joshi
@contact: tucker@cc.gatech.edu
@summary: Example tutorial code.
'''

import matplotlib.pyplot as plt
from pylab import *
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du
from QSTK.qstkutil import tsutil as tsu
import datetime as dt

#
# Read the definition of the portfolio from a csv file
#
portfolio = np.loadtxt('tutorial3portfolio.csv',
	dtype='S5,f4',
	delimiter=',',
        comments='#',
	skiprows=1,
	)
print portfolio
# Sort by symbol name
portfolio = sorted(portfolio, key=lambda x: x[0])
print portfolio

#
# Create two lists: portfolio names and allocations
#
portsyms = []
portalloc = []
for i in portfolio:
	portsyms.append(i[0])
	portalloc.append(i[1])

#
# Read in the symbols available and compare with our portfolio
#
dataobj = da.DataAccess('Yahoo')
all_symbols = dataobj.get_all_symbols()
intersectsyms = list(set(all_symbols) & set(portsyms)) # valid symbols
badsyms = []
if size(intersectsyms)<size(portsyms):
	badsyms = list(set(portsyms) - set(intersectsyms))
	print "warning: portfolio contains symbols that do not exist:" 
	print badsyms
for i in badsyms: # remove the bad symbols from our portfolio
	index = portsyms.index(i)
	portsyms.pop(index)
	portalloc.pop(index)

#
# Read the historical data in from our data store
#
endday = dt.datetime(2011,1,1) 
startday = endday - dt.timedelta(days=1095) #three years back
timeofday=dt.timedelta(hours=16)
print "start getNYSEdays"
timestamps = du.getNYSEdays(startday,endday,timeofday)
print "start read"
close = dataobj.get_data(timestamps,portsyms,"close")
print "end read"

#
# Copy, prep, and compute daily returns
#
rets = close.values.copy()
tsu.fillforward(rets)
tsu.returnize0(rets)

#
# Estimate portfolio total returns
#
portrets = sum(rets*portalloc,axis=1)
porttot = cumprod(portrets+1)
componenttot = cumprod(rets+1,axis=0) # compute returns for components

#
# Plot the result
#
plt.clf()
fig = plt.figure()
fig.add_subplot(111)
plt.plot(timestamps,componenttot,alpha=0.4)
plt.plot(timestamps,porttot)
names = portsyms
names.append('portfolio')
plt.legend(names)
plt.ylabel('Cumulative Returns')
plt.xlabel('Date')
fig.autofmt_xdate(rotation=45)
savefig('tutorial3.pdf',format='pdf')
