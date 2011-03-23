"""
Created on March 22, 2011

@author: Drew Bratcher & Tucker Balch
@contact: tucker@cc.gatech.edu

utilities for date and time manipulation
"""

__version__ = "$Revision: 295 $"

import datetime as dt
from datetime import timedelta
import numpy as np
import os

def getMonthNames():
	return(['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])

def getYears(funds):
	years=[]
	for date in funds.index:
		if(not(date.year in years)):
			years.append(date.year)
	return(years)

def getMonths(funds,year):
	months=[]
	for date in funds.index:
		if((date.year==year) and not(date.month in months)):
			months.append(date.month)
	return(months)

def getDays(funds,year,month):
	days=[]
	for date in funds.index:
		if((date.year==year) and (date.month==month)):
			days.append(date)
	return(days)

def getDaysBetween(ts_start, ts_end):
	days=[]
	for i in range(0,(ts_end-ts_start).days):
		days.append(ts_start+timedelta(days=1)*i)
	return(days)

def getFirstDay(funds,year,month):
	for date in funds.index:
		if((date.year==year) and (date.month==month)):
			return(date)
	return('ERROR') 

def getNYSEdays(startday = dt.datetime(1964,7,5), endday = dt.datetime(2020,12,31),
	timeofday = dt.timedelta(0)):
	"""
	@summary Create a list of timestamps between startday and endday (inclusive) 
	that correspond to the days there was trading at the NYSE. This function 
	depends on a separately created a file that lists all days since July 4, 
	1962 that the NYSE has been open, going forward to 2020 (based
	on the holidays that NYSE recognizes).

	@param startday: First timestamp to consider (inclusive)
	@param endday: Last day to consider (inclusive)
	@return list: of timestamps between startday and endday on which NYSE traded
	@rtype datetime
	"""
 
	try:
		filename = os.environ['QS'] + "/qstkutil/NYSE_dates.txt"
	except KeyError:
		print "Please be sure to set the value for QS in config.sh or\n"
		print "in local.sh and then \'source local.sh\'.\n"

	datestxt = np.loadtxt(filename,dtype=str)
	dates = []

	for i in datestxt:
		dates.append(dt.datetime.strptime(i,"%m/%d/%Y")+timeofday)

	dates = [x for x in dates if x >= startday]
	dates = [x for x in dates if x <= endday]

	return(dates)
