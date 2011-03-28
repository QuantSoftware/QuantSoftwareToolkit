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
from QuickSim import quickSim
from qstkutil import pseries as ps
from pandas import *
import matplotlib.pyplot as plt
import cPickle

def fundsToPNG(funds,output_file):
	plt.clf()
	plt.plot(funds.index,funds.values)
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.draw()
	savefig(output_file, format='png')
