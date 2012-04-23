'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on April, 20, 2012

@author: Sourabh Bajaj
@contact: sourabhbajaj90@gmail.com
@summary: Visualizer - Generating Data from QSTK

'''

#import libraries
import numpy as np
import qstkutil.dateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import qstkfeat.sb_featutil as feat
import datetime as dt
import pickle
import os
import matplotlib.pyplot as plt
from pylab import *
from pandas import *


# Changes made in the featutil file are : Edited the getFeatureFuncs()


def genData(startday, endday, datadirectory, symbols):

	coredirectory = os.environ['QS']+'Tools/Visualizer/Data/'

	directorylocation= coredirectory+datadirectory+'_'+startday.date().isoformat() +'_'+endday.date().isoformat()

	if not os.path.exists(directorylocation):
		os.mkdir(directorylocation)

	directorylocation = directorylocation +'/'

	timeofday = dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	
	#Creating a txt file of timestamps
	file = open(directorylocation +'TimeStamps.txt', 'w')
	for onedate in timestamps:
		stringdate=dt.date.isoformat(onedate)
		file.write(stringdate+'\n')
	file.close()

	# Reading the Stock Price Data
	dataobj = da.DataAccess('Norgate')
	all_symbols = dataobj.get_all_symbols()
	badsymbols=set(symbols)-set(all_symbols)
	if len(list(badsymbols))>0:
		print "Some Symbols are not valid" + str(badsymbols)
	symbols=list(set(symbols)-badsymbols)

	lsKeys = ['open', 'high', 'low', 'close', 'volume']

	ldfData = dataobj.get_data( timestamps, symbols, lsKeys )
	dData = dict(zip(lsKeys, ldfData))
	
	
	# Creating the 3D Matrix

	(lfcFeatures, ldArgs, lsNames)= feat.getFeatureFuncs22()	

	FinalData = feat.applyFeatures( dData, lfcFeatures, ldArgs, sMarketRel='SPY')
	
	#Creating a txt file of symbols
	file = open(directorylocation +'Symbols.txt', 'w')
	for sym in symbols:
		file.write(str(sym)+'\n')
	file.close()

	#Creating a txt file of Features
	file = open(directorylocation +'Features.txt', 'w')
	for f in lsNames:
		file.write(f+'\n')
	file.close()
	
	Numpyarray=[]
	for IndicatorData in FinalData:
		Numpyarray.append(IndicatorData.values)

	pickle.dump(Numpyarray,open(directorylocation +'ALLDATA.pkl', 'wb' ),-1)
	
def main():
	startday=dt.datetime(2009,1,1)
	endday=dt.datetime(2010,12,31)
	datadirectory = 'Dow'
#	datadirectory = 'SP500'
#	symbols=np.loadtxt('Symbols.csv',dtype='S5',comments='#',skiprows=1,)
	symbols=['SPY','MMM','AA','AXP','T','BAC','BA','CAT','CVX','CSCO','KO','DD','XOM','GE','HPQ','HD','INTC','IBM','JNJ','JPM','KFT', 'MCD','MRK','MSFT','PFE','PG','TRV','UTX','VZ','WMT','DIS']
	genData(startday,endday, datadirectory, symbols)

if __name__ == '__main__':
	main()
