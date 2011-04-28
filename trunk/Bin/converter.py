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
from copy import deepcopy
import math
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
	count=1
	sum=tsu.daily(funds[0].values)
	for i in range(1,len(funds)):
		ret=tsu.daily(funds[i].values)
		for j in range(0, len(sum)):
			if j <len(ret):
				sum[j]+=ret[j]
		count+=1
	#compute average
	tot_ret=sum
	for i in range(0,len(sum)):
		tot_ret[i]=sum[i]/count
	#compute std
	std=zeros(len(funds[0].values))
	dates=list()
	for i in range(0,len(funds)):
		temp=tsu.daily(funds[i].values)
		for j in range(0,len(temp)):
			std[j]+=(temp[j]-tot_ret[j])**2
	for i in range(0, len(std)):
		std[i]=math.sqrt(std[i]/count)
	#compute total returns
	tot_ret[0]=funds[0].values[0]
	lower=deepcopy(tot_ret)
	upper=deepcopy(tot_ret)
	for i in range(1,len(tot_ret)):
		fact=tot_ret[i]
		tot_ret[i]=tot_ret[i-1]+(fact)*tot_ret[i-1]
		lower[i]=tot_ret[i-1]+(fact-std[i])*tot_ret[i-1]
		upper[i]=tot_ret[i-1]+(fact+std[i])*tot_ret[i-1]
	dates=funds[0].index
	plt.clf()
	plt.plot(dates,tot_ret)
	plt.plot(dates,lower)
	plt.plot(dates,upper)
	plt.legend(('Tot_Ret','Lower','Upper'),loc='upper left')
	plt.ylabel('Fund Total Return')
	plt.draw()
	savefig(output_file, format='png')
