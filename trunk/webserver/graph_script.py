import web
import os
import sys
from pylab import *
from pandas import *
import matplotlib.pyplot as plt
from matplotlib import *
import time as t
import cPickle
import datetime as dt

# qstk imports
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from quicksim import quickSim as qs

def make_text(string):
	symbols=string.split(",")
	tsstart = dt.datetime(2004,1,1)
	tsend = dt.datetime(2009,12,31)
	timeofday=dt.timedelta(hours=16)
	timestamps=du.getNYSEdays(tsstart,tsend,timeofday)
	
	# Get the data from the data store
	dataobj=da.DataAccess('Norgate')
	historic = dataobj.get_data(timestamps,symbols,"close")
	
	# create alloc
	alloc_vals=.8/(len(historic.values[0,:])-1)*ones((1,len(historic.values[0,:])))
	alloc=DataMatrix(index=[historic.index[0]], data=alloc_vals, columns=symbols)
	for date in range(0, len(historic.index)):
	        if(historic.index[date].day==1):
	                alloc=alloc.append(DataMatrix(index=[historic.index[date]], data=alloc_vals, columns=symbols))
	alloc[symbols[0]] = .1
	alloc['_CASH'] = .1
	
	#output to pickle file
	output=open("allocations.pkl","wb")
	cPickle.dump(alloc, output)
	
	#test allocation with quicksim
	funds=qs.quickSim(alloc,historic,1000)
	#output to pickle file
	output2=open("funds2.pkl","wb")
	cPickle.dump(funds, output2)
	
	#plot funds
	plt.clf()
	plt.plot(funds.index,funds.values)
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.draw()
	savefig("./images/funds"+string+".png", format='png')
	#fig=plt.figure()
	#canvas=FigureCanvasAgg(fig)
	#canvas.print_figure("funds"+string+".png");
	return "<img src=funds"+string+".png>"

if __name__ == '__main__':
    make_text(sys.argv[1])

