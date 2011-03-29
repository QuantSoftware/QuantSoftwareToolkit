#
# OneStock.py
#
# Usage: python OneStock.py '1-1-2004' '1-1-2009' 'alloc.pkl'
#
# A strategy script which creates a daily allocation table using one stock (GOOG)
# and the start and end dates provided by the user.
# It then dumps the allocation table to a pickle file.
#
#

# python imports
import cPickle
import random
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import datetime as dt

# qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du

if __name__ == "__main__":
	# Use google symbol
	symbols = list('GOOG')

	# Set start and end dates
	t = map(int,sys.argv[1].split('-'))
	startday = dt.datetime(t[2],t[0],t[1])
	t = map(int,sys.argv[2].split('-'))
	endday = dt.datetime(t[2],t[0],t[1])
	
	# Get desired timestamps
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	
	# Get the data from the data store
	dataobj = da.DataAccess('Norgate')
	historic = dataobj.get_data(timestamps, symbols, "close")
	
	# Setup the allocation table
	alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
	for date in range(1, len(historic.index)):
		alloc_val=random.randint(0,1);
		alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_val, columns=symbol))
		alloc['_CASH']=1-alloc_val;

	# Dump to pkl file
	output=open(sys.argv[3],"wb")
	cPickle.dump(alloc, output)
