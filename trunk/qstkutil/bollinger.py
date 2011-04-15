# python imports
import cPickle
from pylab import *
from pandas import *
import datetime as dt

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du

def calcavg(period):
	sum = zeros(len(period(0)))
	count=0
	for day in period:
		sum+=period(day)
		count+=1
	return(sum/count)

def calcdev(period):
	avg=calcavg(period)
	devs=zeros(len(period(0)))
	count=0
	for day in period:
		devs+=(period(day)-avg)*(period(day)-avg)
		count+=1
	return(sqrt(devs/count))

def bollinger(adjclose, timestamps, stocks, lookback):
	bvals=DataMatrix(index=timestamps[0],columns=stocks,data=zeros(len(stocks))) 
	for day in timestamps:
		lookbackperiod=adjclose[day-lookback:day]
		avg = calcavg(lookbackperiod)
		stddev = calcdev(lookbackperiod)
		b=(adjclose(day)-avg)/stddev
		bvals=bvals.append(DataMatrix(day,stocks,b)
	return(bvals)
