'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''

# python imports
import cPickle
from pylab import *
from pandas import *
import datetime as dt

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.qsdateutil as du

def calcavg(period):
	sum = zeros(len(period.columns))
	count=0
	for day in period.index:
		sum+=period.xs(day)
		count+=1
	return(sum/count)

def calcdev(period):
	avg=calcavg(period)
	devs=zeros(len(period.columns))
	count=0
	for day in period.index:
		devs+=(period.xs(day)-avg*ones(len(period.columns)))*(period.xs(day)-avg*ones(len(period.columns)))
		count+=1
	return(sqrt(devs/count))

def calcbvals(adjclose, timestamps, stocks, lookback):
	for i in adjclose.values:
		if i == 'NaN':
			adjclose.values[adjclose.values.index(i)]=1;
	bvals=DataMatrix(index=[timestamps[0]],columns=stocks,data=[zeros(len(stocks))]) 
	for i in range(1,len(timestamps)):
		s=i-lookback
		if s<0:
			s=0
		lookbackperiod=adjclose[s:i]
		avg = calcavg(lookbackperiod)
		stddevs = calcdev(lookbackperiod)
		if not(0 in stddevs):
			b=(adjclose[i:i+1]-avg*ones(len(lookbackperiod.columns)))/stddevs
			bvals=bvals.append(DataMatrix(index=[timestamps[i]],columns=stocks,data=b))
	return(bvals)
