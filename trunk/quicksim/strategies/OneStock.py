#
# MonthlyRebalancingExample.py
#
# An example which creates a daily allocation table
# from 2004 to 2009 and using one stock.
# It then dumps the allocation table to a picklefile format
# file named allocations.pkl
#
# Drew Bratcher
#

#sample_alloc setup
from pylab import *
from qstkutil import DataAccess
from qstkutil import dateutil as du
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quickSim as simulator
import matplotlib.pyplot as plt
import time as t
import cPickle
import random

if __name__ == "__main__":
	#sample_historic setup
	#use google 
	symbol = 'GOOG'

	#Set start and end boundary times.  They must be specified in Unix Epoch
	t = map(int,sys.argv[1].split('-'))
	tsstart=tu.ymd2epoch(t[2],t[0],t[1])
	t = map(int,sys.argv[2].split('-'))
	tsend = tu.ymd2epoch(t[2],t[0],t[1])
	
	# Get the data from the data store
	storename = "Norgate" # get data from our daily prices source
	fieldname = "close" # adj_open, adj_close, adj_high, adj_low, close, volume
	
	da=DataAccess.DataAccess(storename)
	symbol_list=list(symbol)
	ts_list=du.getDaysBetween(tu.epoch2date(tsstart),tu.epoch2date(tsend))
	historic = da.get_data(ts_list, symbol_list, fieldname)
	alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
	for date in range(1, len(historic.index)):
		alloc_val=random.randint(0,1);
		alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_val, columns=symbol))
		alloc['_CASH']=1-alloc_val;

	output=open(sys.argv[3],"wb")
	cPickle.dump(alloc, output)
