import cPickle
from pandas import *
from qstkutil import dateutil

def daily(funds):
	prev=0
	rets=[]
	for line in funds:
		rets.append(float(line-prev)/line)
		prev=line	
	return(rets)

def monthly(funds):
	funds2=[]
	years=dateutil.getYears(funds)
	for year in years:
		months=dateutil.getMonths(funds,year)
		for month in months:
			funds2.append(dateutil.getFirstDay(funds,year,month))
	prev=0
	rets=[]
	for line in funds:
		rets.append(float(line-prev)/line)
		prev=line
	return(rets)	

