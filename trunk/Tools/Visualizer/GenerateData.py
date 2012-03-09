#created by Sourabh Bajaj
#email: sourabhbajaj90@gmail.com

#import libraries
import numpy as np
import qstkutil.dateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import qstkfeat.featutil as feat
import datetime as dt
import pickle
import matplotlib.pyplot as plt
from pylab import *
from pandas import *


# Changes made in the featutil file are : Edited the getFeatureFuncs()


def genData(startday=None, endday=None):

	# Initializing the Date Range
	# If Startday or Endday not specified then tries to read from DateRange.csv
		
	if startday==None or endday==None:
		try:
			datesdata= np.loadtxt('DateRange.csv',delimiter=',',skiprows=1)
			datesdata= np.int_(datesdata)	
			dates = []
			for i in range(0,datesdata.shape[0]):
				dates.append(dt.datetime(datesdata[i,0],datesdata[i,1],datesdata[i,2]))
	
			startday=dates[0]
			endday=dates[1]	
		except: 
			print "Please check if DateRange.csv exists or Specify startday and endday"
			return
		
	timeofday = dt.timedelta(hours=16)
	timestamps = du.getNYSEdays(startday,endday,timeofday)
	
	#Creating a txt file of timestamps
	file = open('TimeStamps.txt', 'w')
	for onedate in timestamps:
		stringdate=dt.date.isoformat(onedate)
		file.write(stringdate+'\n')
	file.close()

	# Reading the Stock Price Data
	dataobj = da.DataAccess('Norgate')
	symbols=np.loadtxt('Symbols.csv',dtype='S5',comments='#',skiprows=1,)
	all_symbols = dataobj.get_all_symbols()
	badsymbols=set(symbols)-set(all_symbols)
	if len(list(badsymbols))>0:
		print "Some Symbols are not valid" + str(badsymbols)
	symbols=list(set(symbols)-badsymbols)

	lsKeys = ['open', 'high', 'low', 'close', 'volume']

	ldfData = dataobj.get_data( timestamps, symbols, lsKeys )
	dData = dict(zip(lsKeys, ldfData))
	

	# Creating the 3D Matrix

	(lfcFeatures, ldArgs, lsNames)= feat.getFeatureFuncs()
	featureslist= np.loadtxt('Features.csv',dtype='S',comments='#',skiprows=1,)
	
	lfcFeaturesFinal=[]
	ldArgsFinal=[]	
	
	for func in featureslist:
		if func in lsNames:
			lfcFeaturesFinal.append(lfcFeatures[lsNames.index(func)])
			ldArgsFinal.append(ldArgs[lsNames.index(func)])
	
	FinalData = feat.applyFeatures( dData, lfcFeatures, ldArgs, sMarketRel=None)
	
	Numpyarray=[]
	for IndicatorData in FinalData:
		Numpyarray.append(IndicatorData.values)

	pickle.dump(Numpyarray,open( 'AllData', 'wb' ),-1)
	
if __name__ == '__main__':
	genData()

