# python imports
import cPickle
from pylab import *
from pandas import *
import datetime as dt

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du

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
	bvals=DataMatrix(index=[timestamps[0]],columns=stocks,data=[zeros(len(stocks))]) 
	for i in range(0,len(timestamps)):
		s=i-lookback
		if s<0:
			s=0
		if s!=i:
			lookbackperiod=adjclose[s:i]
			print lookbackperiod
			avg = calcavg(lookbackperiod)
			stddevs = calcdev(lookbackperiod)
			if avg[0]>0 and stddevs[0]>0:
				b=(adjclose[i:i+1]-avg*ones(len(lookbackperiod.columns)))/stddevs
				bvals=bvals.append(DataMatrix(index=[timestamps[i]],columns=stocks,data=[b]))
	return(bvals)
