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
from qstkutil import tsutil as tsu
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

def fundsAnalysisToPNG(funds,output_file):
	plt.clf()
	if(type(funds)!=type(list())):
		print 'fundsmatrix only contains one timeseries, not able to analyze.'
	#convert to daily returns
	count=0
	sum=zeros(len(funds[i].values))
	for i in range(0,len(funds)):
		ret=funds[i].values
		tsu.returnize0(ret)
		sum+=ret
		count+=1
	#compute average
	tot_ret=sum/count
	#compute std
	std=zeros(len(funds[i].values))
	for i in range(0,len(funds)):
		temp=funds[i].values
		tsu.returnize0(temp)
		std+=(temp-avg)**2
	std=(std/count)**(1/2)
	#compute total returns
	tot_ret[0]=funds[0].values[0]
	for i in range(1,len(tot_ret)):
		tot_ret[i]=(1+tot_ret[i])*tot_ret[i-1]
	plt.plot(funds[i].index,tot_ret)
	plt.plot(funds[i].index,tot_ret-std)
	plt.plot(funds[i].index,tot_ret+std)
	plt.ylabel('Fund Total Return')
	plt.xlabel('Date')
	plt.draw()
	savefig(output_file, format='png')