import cPickle
import math
import numpy as np
from pandas import *
from qstkutil import dateutil
from math import sqrt
from copy import deepcopy

def daily(funds):
	nd=deepcopy(funds)
	nd[0]=0
	for i in range(1,len(funds)):
		nd[i]=funds[i]/funds[i-1]-1
	return(nd)

def monthly(funds):
	funds2=[]
	years=dateutil.getYears(funds)
	for year in years:
		months=dateutil.getMonths(funds,year)
		for month in months:
			funds2.append(funds[dateutil.getFirstDay(funds,year,month)])
	return(daily(funds2))

def averageMonthly(funds):
	rets=daily(funds)
	x=0
	years=dateutil.getYears(funds)
	averages=[]
	for year in years:
		months=dateutil.getMonths(funds,year)
		for month in months:
			avg=0
			count=0
			days=dateutil.getDays(funds,year,month)
			for day in days:
				avg+=rets[x]
				x+=1
				count+=1
			averages.append(float(avg)/count)
	return(averages)	

def fillforward(nd):
	"""
	@summary Removes NaNs from a 2D array by scanning forward in the 
	1st dimension.  If a cell is NaN, the value above it is carried forward.
	@param nd: the array to fill forward
	@return the array is revised in place
	"""
	for col in range(nd.shape[1]):
		for row in range(1,nd.shape[0]):
			if math.isnan(nd[row,col]):
				nd[row,col] = nd[row-1,col]

def fillbackward(nd):
	"""
	@summary Removes NaNs from a 2D array by scanning backward in the 
	1st dimension.  If a cell is NaN, the value above it is carried backward.
	@param nd: the array to fill backward
	@return the array is revised in place
	"""
	for col in range(nd.shape[1]):
		for row in range(nd.shape[0]-2,-1,-1):
			if math.isnan(nd[row,col]):
				nd[row,col] = nd[row+1,col]

def returnize0(nd):
	"""
	@summary Computes stepwise (usually daily) returns relative to 0, where
	0 implies no change in value.
	@return the array is revised in place
	"""
	nd[1:,:] = (nd[1:,:]/nd[0:-1]) - 1
	nd[0,:] = np.zeros(nd.shape[1])

def returnize1(nd):
	"""
	@summary Computes stepwise (usually daily) returns relative to 1, where
	1 implies no change in value.
	@param nd: the array to fill backward
	@return the array is revised in place
	"""
	nd[1:,:] = (nd[1:,:]/nd[0:-1])
	nd[0,:] = np.ones(nd.shape[1])

def getRatio(funds):
	d=daily(funds)
	avg=float(sum(d))/len(d)
	std=0
	for a in d:
		std=std+float((float(a-avg))**2)
	std=sqrt(float(std)/(len(d)-1))
	return(avg/std)

def getYearRatio(funds,year):
	funds2=[]
	for date in funds.index:
		if(date.year==year):
			funds2.append(funds[date])
	return(getRatio(funds2))

