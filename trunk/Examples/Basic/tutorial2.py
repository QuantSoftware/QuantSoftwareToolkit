'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on September, 12, 2011

@author: Tucker Balch
@contact: tucker@cc.gatech.edu
@summary: Example tutorial code.
'''

#
# imports
#
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import datetime as dt

#
# read in and slice up the data
#
data = np.loadtxt('example-data.csv',delimiter=',',skiprows=1)
pricedat = data[:,3:]
datesdat = np.int_(data[:,0:3]) # date stuff should be integer
pricesnames = ['$SPX','XOM','GOOG','GLD']

print 'first 5 rows of price data:'
print pricedat[:5,:]
print
print 'first 5 rows of dates:'
print datesdat[:5,:]

#
# Convert columns of date info into date objects
#
dates = []
for i in range(0,datesdat.shape[0]):
	dates.append(dt.date(datesdat[i,0],datesdat[i,1],datesdat[i,2]))

#
# Plot the closing prices 
#
plt.clf()
for i in range(0,size(pricedat[0,:])):
	plt.plot(dates,pricedat[:,i])
plt.legend(pricesnames)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
savefig('adjustedclose.pdf', format='pdf')

#
# Plot the normalized data
#
plt.clf()
normdat = pricedat/pricedat[0,:]
for i in range(0,size(normdat[0,:])):
	plt.plot(dates,normdat[:,i])
plt.legend(pricesnames)
plt.ylabel('Normalized Adjusted Close')
plt.xlabel('Date')
savefig("normalizedclose.pdf", format='pdf')

#
# Daily returns
#
plt.clf()
dailyrets = concatenate(([(zeros(pricedat.shape[1]))],
	((pricedat[1:,:]/pricedat[0:-1,:]) - 1)),axis=0)
plt.plot(dates[0:49],dailyrets[0:49,0]) # just plot first 50 days
plt.plot(dates[0:49],dailyrets[0:49,1])
plt.axhline(y=0,color='r')
plt.legend(['$SPX','XOM'])
plt.ylabel('Daily Returns')
plt.xlabel('Date')
savefig("dailyrets.pdf", format='pdf')

#
# scatter plot $SPX v XOM
#
plt.clf()
plt.scatter(dailyrets[:,0],dailyrets[:,1],c='blue')
plt.ylabel('XOM')
plt.xlabel('$SPX')
savefig("scatterSPXvXOM.pdf", format='pdf')

#
# scatter plot $SPX v GLD
#
plt.clf()
plt.scatter(dailyrets[:,0],dailyrets[:,3],c='red')
plt.ylabel('GLD')
plt.xlabel('$SPX')
savefig("scatterSPXvGLD.pdf", format='pdf')
