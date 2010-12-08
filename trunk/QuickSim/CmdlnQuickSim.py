#
# CmdlnQuickSim.py
#
# A function which runs a quick sim on an allocation provided via command line,
# along with the stock symbols csv file and a start and end date in month/day/year format.
# 
# sample call:
# python CmdlnQuickSim.py 'alloc_file.pkl' 'symbols.csv' '1/1/2007' '12/31/2009'  
#
# Drew Bratcher
#

#sample_alloc setup
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from qstkutil import pseries as ps
from pandas import *
import quickSim as simulator
import matplotlib.pyplot as plt
import time as t
import pickle
import sys
import calendar

#read in alloc table from command line arguements
alloc_input_file=open(sys.argv[1],"rb")
print 'Loading allocations table from file:'
print sys.argv[1]
print '\n'
alloc=pickle.load(alloc_input_file)

#setup historic table using command line arguements
print 'Loading symbols list from file:'
print sys.argv[2]
print '\n'
symbols = list(np.loadtxt(sys.argv[2],dtype='str',delimiter=',',comments='#',skiprows=0))
#Set start and end boundary times.  They must be specified in Unix Epoch
t = map(int,sys.argv[3].split('/'))
print 'Using start date:'
print sys.argv[3],t[2],t[0],t[1]
print '\n'
tsstart=tu.ymd2epoch(t[2],t[0],t[1])
t = map(int,sys.argv[4].split('/'))
print 'Using end date:'
print sys.argv[4],t[2],t[0],t[1]
print '\n'
tsend = tu.ymd2epoch(t[2],t[0],t[1])

# Get the data from the data store
storename = "Norgate" # get data from our daily prices source
fieldname = "adj_close" # adj_open, adj_close, adj_high, adj_low, close, volume

historic = ps.getDataMatrixFromData(storename,fieldname,symbols,tsstart,tsend)


funds=simulator.quickSim(alloc,historic,1000)

plt.clf()
plt.plot(funds.index,funds.values)
plt.ylabel('Fund Value')
plt.xlabel('Date')
plt.draw()
savefig("funds.pdf", format='pdf')
