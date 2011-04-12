#
# fundsToPNG.py
#
# Short script which produces a graph of funds 
# over time from a pickle file.
#
# Drew Bratcher
#

from pylab import *
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu
from quicksim import quickSim
from pandas import *
import matplotlib.pyplot as plt
import cPickle

def fundsToPNG(funds,output_file):
	plt.clf()
	if(type(funds)==type(list())):
		for i in range(0,len(funds)):
			plt.plot(funds[i].index,funds[i].values)
	else:
		plt.plot(funds.index,funds.values)
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.draw()
	savefig(output_file, format='png')
