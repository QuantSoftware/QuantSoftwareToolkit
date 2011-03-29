#
# MonthlyRebalancingExample.py
#
# Usage: python MonthlyRebalancingExample.py 1-1-2004' '1-1-2009' 'alloc.pkl'
#
# A strategy script which creates a monthly allocation table using 
# start date and end date along with the first 20 symbols of S&P500.
# It then dumps the allocation table to a pickle file.
#
#

#python imports
import cPickle
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
import datetime as dt

#qstk imports
import qstkutil.DataAccess as da
import qstkutil.dateutil as du

if __name__ == "__main__":
	
	#Get first 20 S&P Symbols 
	symbols = list(np.loadtxt	('S&P500.csv',dtype='str',delimiter=',',comments='#',skiprows=0))
	symbols = symbols[0:19]
	
	#Set start and end boundary times
	t = map(int,sys.argv[1].split('-'))
	startday = dt.datetime(t[2],t[0],t[1])
	t = map(int,sys.argv[2].split('-'))
	endday = dt.datetime(t[2],t[0],t[1])
	
	#Get desired timestamps
	timeofday=dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	
	# Get the data from the data store
	dataobj = da.DataAccess('Norgate')
	historic = dataobj.get_data(timestamps, symbols, "close")

    # Setup the allocation table
	alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
	alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
	for date in range(1, len(historic.index)):
		if(historic.index[date].day==1):
			alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
	alloc[symbols[0]] = .1
	alloc['_CASH'] = .1
	
	#Dump to a pkl file
	output=open(sys.argv[3],"wb")
	cPickle.dump(alloc, output)