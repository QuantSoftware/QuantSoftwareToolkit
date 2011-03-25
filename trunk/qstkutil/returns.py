import cPickle
import math
from pandas import *
from qstkutil import dateutil

def daily(funds):
	prev=0
	rets=[]
	for line in funds:
		rets.append(float(line-prev)/line-1)
		prev=line	
	return(rets)

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
