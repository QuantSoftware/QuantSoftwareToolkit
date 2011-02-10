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

if __name__ == "__main__":
	fund_input_file=open(sys.argv[1],"rb")
	funds=cPickle.load(fund_input_file)

	plt.clf()
	plt.plot(funds.index,funds.values)
	plt.ylabel('Fund Value')
	plt.xlabel('Date')
	plt.draw()
	savefig("funds.png", format='png')
