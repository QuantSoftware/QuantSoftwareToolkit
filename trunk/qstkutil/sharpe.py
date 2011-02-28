from pandas import *
from QuickSim import quickSim as qs
from qstkutil import returns
import cPickle
from math import sqrt

def getRatio(funds):
	daily=returns.daily(funds)
	avg=float(sum(daily))/len(daily)
	std=0
	for a in daily:
		std=std+float((float(a-avg))**2)
	std=sqrt(float(std)/(len(daily)-1))
	return(avg/std)

def getYearRatio(funds,year):
	funds2=[]
	for date in funds.index:
		if(date.year==year):
			funds2.append(funds[date])
	return(getRatio(funds2))
