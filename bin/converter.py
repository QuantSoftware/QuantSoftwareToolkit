'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''

#
# fundsToPNG.py
#
# Short script which produces a graph of funds 
# over time from a pickle file.
#
# Drew Bratcher
#

from pylab import *
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import tsutil as tsu
# from quicksim import quickSim
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
	plt.gcf().autofmt_xdate(rotation=45)
	plt.draw()
	savefig(output_file, format='png')

def fundsAnalysisToPNG(funds,output_file):
	plt.clf()
	if(type(funds)!=type(list())):
		print 'fundsmatrix only contains one timeseries, not able to analyze.'
	#convert to daily returns
	count=list()
	dates=list()
	sum=list()
	for i in range(0,len(funds)):
		ret=tsu.daily(funds[i].values)
		for j in range(0, len(ret)):
			if (funds[i].index[j] in dates):
				sum[dates.index(funds[i].index[j])]+=ret[j]
				count[dates.index(funds[i].index[j])]+=1
			else:
				dates.append(funds[i].index[j])	
				count.append(1)
				sum.append(ret[j])
	#compute average
	tot_ret=deepcopy(sum)
	for i in range(0,len(sum)):
		tot_ret[i]=sum[i]/count[i]
	
	#compute std
	std=zeros(len(sum))
	for i in range(0,len(funds)):
		temp=tsu.daily(funds[i].values)
		for j in range(0,len(temp)):
			std[dates.index(funds[i].index[j])]=0
			std[dates.index(funds[i].index[j])]+=math.pow(temp[j]-tot_ret[dates.index(funds[i].index[j])],2)
	
	for i in range(1, len(std)):
#		std[i]=math.sqrt(std[i]/count[i])+std[i-1]
		std[i]=math.sqrt(std[i]/count[i])
	
	#compute total returns
	lower=deepcopy(tot_ret)
	upper=deepcopy(tot_ret)
	tot_ret[0]=funds[0].values[0]
	lower[0]=funds[0].values[0]
	upper[0]=lower[0]
#	for i in range(1,len(tot_ret)):
#		tot_ret[i]=tot_ret[i-1]+(tot_ret[i])*tot_ret[i-1]
#		lower[i]=tot_ret[i-1]-(std[i])*tot_ret[i-1]
#		upper[i]=tot_ret[i-1]+(std[i])*tot_ret[i-1]
	for i in range(1,len(tot_ret)):
		lower[i]=(tot_ret[i]-std[i]+1)*lower[i-1]
		upper[i]=(tot_ret[i]+std[i]+1)*upper[i-1]
		tot_ret[i]=(tot_ret[i]+1)*tot_ret[i-1]
		
	
	plt.clf()
	plt.plot(dates,tot_ret)
	plt.plot(dates,lower)
	plt.plot(dates,upper)
	plt.legend(('Tot_Ret','Lower','Upper'),loc='upper left')
	plt.ylabel('Fund Total Return')
	plt.ylim(ymin=0,ymax=2*tot_ret[0])
	plt.draw()
	savefig(output_file, format='png')
