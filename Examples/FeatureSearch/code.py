''' Python imports '''
import datetime as dt

''' 3rd party imports '''
import numpy as np
import pandas as pand
import matplotlib.pyplot as plt

''' QSTK imports '''
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du

from QSTK.qstkfeat.features import *
from QSTK.qstkfeat.classes import class_fut_ret
import QSTK.qstkfeat.featutil as ftu	
	
import sys
import time

from functions import *

if __name__ == '__main__':
	''' Use Dow 30 '''
	#lsSym = ['AA', 'AXP', 'BA', 'BAC', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'HD', 'HPQ', 'IBM', 'INTC', 'JNJ', \
	#		 'JPM', 'KFT', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'PFE', 'PG', 'T', 'TRV', 'UTX', 'WMT', 'XOM'  ]

	#lsSymTrain = lsSym[0:4] + ['$SPX']
	#lsSymTest = lsSym[4:8] + ['$SPX']
	
	f = open('2008Dow30.txt')
	lsSymTrain = f.read().splitlines() + ['$SPX']
	f.close()
	
	f = open('2010Dow30.txt')
	lsSymTest = f.read().splitlines() + ['$SPX']
	f.close()
	
	lsSym = list(set(lsSymTrain).union(set(lsSymTest)))
	
	dtStart = dt.datetime(2008,01,01)
	dtEnd = dt.datetime(2010,12,31)
	
	norObj = da.DataAccess('Norgate')	  
	ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )	
	
	lsKeys = ['open', 'high', 'low', 'close', 'volume']
	
	ldfData = norObj.get_data( ldtTimestamps, lsSym, lsKeys ) #this line is important even though the ret value is not used
	
	for temp in ldfData:
		temp.fillna(method="ffill").fillna(method="bfill")
	
	ldfDataTrain = norObj.get_data( ldtTimestamps, lsSymTrain, lsKeys )
	ldfDataTest = norObj.get_data( ldtTimestamps, lsSymTest, lsKeys)
	
	for temp in ldfDataTrain:
		temp.fillna(method="ffill").fillna(method="bfill")
		
	for temp in ldfDataTest:
		temp.fillna(method="ffill").fillna(method="bfill")
	
	dDataTrain = dict(zip(lsKeys, ldfDataTrain))
	dDataTest = dict(zip(lsKeys, ldfDataTest))
	
	''' Imported functions from qstkfeat.features, NOTE: last function is classification '''
	lfcFeatures = [ featMA, featMA, featMA, featMA, featMA, featMA, \
					featRSI, featRSI, featRSI, featRSI, featRSI, featRSI, \
					featDrawDown, featDrawDown, featDrawDown, featDrawDown, featDrawDown, featDrawDown, \
					featRunUp, featRunUp, featRunUp, featRunUp, featRunUp, featRunUp, \
					featVolumeDelta, featVolumeDelta, featVolumeDelta, featVolumeDelta, featVolumeDelta, featVolumeDelta, \
					featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, featAroon, \
					#featStochastic, featStochastic, featStochastic, featStochastic, featStochastic, featStochastic,featStochastic, featStochastic, featStochastic, featStochastic, featStochastic, featStochastic, \
					featBeta, featBeta, featBeta, featBeta, featBeta, featBeta,\
					featBollinger, featBollinger, featBollinger, featBollinger, featBollinger, featBollinger,\
					featCorrelation, featCorrelation, featCorrelation, featCorrelation, featCorrelation, featCorrelation,\
					featPrice, \
					featVolume, \
					class_fut_ret]

	ldArgs = [  {'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5,'bDown':True},{'lLookback':10,'bDown':True},{'lLookback':20,'bDown':True},{'lLookback':5,'bDown':False},{'lLookback':10,'bDown':False},{'lLookback':20,'bDown':False},{'lLookback':5,'bDown':True,'MR':True},{'lLookback':10,'bDown':True,'MR':True},{'lLookback':20,'bDown':True,'MR':True},{'lLookback':5,'bDown':False,'MR':True},{'lLookback':10,'bDown':False,'MR':True},{'lLookback':20,'bDown':False,'MR':True},\
				#{'lLookback':5,'bFast':True},{'lLookback':10,'bFast':True},{'lLookback':20,'bFast':True},{'lLookback':5,'bFast':False},{'lLookback':10,'bFast':False},{'lLookback':20,'bFast':False},{'lLookback':5,'bFast':True,'MR':True},{'lLookback':10,'bFast':True,'MR':True},{'lLookback':20,'bFast':True,'MR':True},{'lLookback':5,'bFast':False,'MR':True},{'lLookback':10,'bFast':False,'MR':True},{'lLookback':20,'bFast':False,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{'lLookback':5},{'lLookback':10},{'lLookback':20}, {'lLookback':5,'MR':True},{'lLookback':10,'MR':True},{'lLookback':20,'MR':True},\
				{},\
				{},\
				{'i_lookforward':5}
				]
	
	
	''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
	ldfFeaturesTrain = ftu.applyFeatures( dDataTrain, lfcFeatures, ldArgs, '$SPX')
	ldfFeaturesTest = ftu.applyFeatures( dDataTest, lfcFeatures, ldArgs, '$SPX')

	''' Pick Test and Training Points '''		
	dtStartTrain = dt.datetime(2008,01,01)
	dtEndTrain = dt.datetime(2009,12,31)
	dtStartTest = dt.datetime(2010,01,01)
	dtEndTest = dt.datetime(2010,12,31)
	
	''' Stack all information into one Numpy array ''' 
	naFeatTrain = ftu.stackSyms( ldfFeaturesTrain, dtStartTrain, dtEndTrain )
	naFeatTest = ftu.stackSyms( ldfFeaturesTest, dtStartTest, dtEndTest )
	
	''' Normalize features, use same normalization factors for testing data as training data '''
	ltWeights = ftu.normFeatures( naFeatTrain, -1.0, 1.0, False )
	''' Normalize query points with same weights that come from test data '''
	ftu.normQuery( naFeatTest[:,:-1], ltWeights )	
	

	lFeatures = range(0,len(lfcFeatures)-1)
	classLabelIndex = len(lfcFeatures) - 1
	
	funccall = sys.argv[1] + '(naFeatTrain,naFeatTest,lFeatures,classLabelIndex)'
	
	timestart = time.time()
	clockstart = time.clock()
	eval(funccall)
	clockend = time.clock()
	timeend = time.time()
	
	sys.stdout.write('\n\nclock diff: '+str(clockend-clockstart)+'sec\n')
	sys.stdout.write('time diff: '+str(timeend-timestart)+'sec\n')
	


