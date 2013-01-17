'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing a simple test of the feature engine.
'''

''' Python imports '''
import datetime as dt

''' 3rd party imports '''
import numpy as np
import pandas as pand
import matplotlib.pyplot as plt

''' QSTK imports '''
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du

from QSTK.qstkfeat.features import featMA, featRSI
from QSTK.qstkfeat.classes import class_fut_ret
import QSTK.qstkfeat.featutil as ftu


def learnerTest( naTrain, naTest ):
    ''' 
    @summary: Takes testing and training data and computes average error over the test set
              This is compared to a baseline guess which is just the average of the training set
    '''
    llRange = range(5,51,5)
    
    lfRes = []
    for lK in llRange:
        cLearn = ftu.createKnnLearner( naTrain, lKnn=lK, leafsize=100 )
        fError = 0.0

        naResult = cLearn.query( naTest[:,:-1] )
        naError = abs( naResult - naTest[:,-1] )
        lfRes.append( np.average(naError) )
    
    ''' Generate error of 'dumb' case, just assume average returns every time '''
    naGuess = np.ones( naTest.shape[0] ) * np.average( naTrain[:,-1] )
    lfGuess = [ np.average( abs(naGuess - naTest[:,-1]) ) ] * len(lfRes)
    
    fAvgRets = np.average(naTest[:,-1])
    
    plt.clf()
    plt.plot( llRange, lfRes )
    plt.plot( llRange, lfGuess )
    plt.title( 'Average error on average returns of %.04lf'%fAvgRets )
    plt.legend( ('Learner Predict', 'Average Return Predict') )
    plt.xlabel('K value')
    plt.ylabel('Error')
    plt.show()
    plt.savefig( 'FeatureTest.png', format='png' )
    
    

if __name__ == '__main__':
    
    ''' Use Dow 30 '''
    lsSym = ['AA', 'AXP', 'BA', 'BAC', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'HD', 'HPQ', 'IBM', 'INTC', 'JNJ', \
             'JPM', 'KFT', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'PFE', 'PG', 'T', 'TRV', 'UTX', 'WMT', 'XOM'  ]
    #lsSym = ['XOM']
    
    ''' Get data for 2009-2010 '''
    dtStart = dt.datetime(2010,8,01)
    dtEnd = dt.datetime(2010,12,31)
    
    norObj = da.DataAccess('Yahoo')      
    ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )
    
    lsKeys = ['open', 'high', 'low', 'close', 'volume']
    ldfData = norObj.get_data( ldtTimestamps, lsSym, lsKeys )
    dData = dict(zip(lsKeys, ldfData))
    
    ''' Imported functions from qstkfeat.features, NOTE: last function is classification '''
    lfcFeatures = [ featMA, featRSI, class_fut_ret ]

    ''' Default Arguments '''
    #ldArgs = [{}] * len(lfcFeatures) 
    
    ''' Custom Arguments '''
    ldArgs = [ {'lLookback':30, 'bRel':True},\
               {},\
               {}]                    
    
    ''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
    ldfFeatures = ftu.applyFeatures( dData, lfcFeatures, ldArgs )
    
    
    bPlot = False
    if bPlot:
        ''' Plot feature for XOM '''
        for i, fcFunc in enumerate(lfcFeatures[:-1]):
            plt.clf()
            plt.subplot(211)
            plt.title( fcFunc.__name__ )
            plt.plot( dfPrice.index, dfPrice['XOM'].values, 'r-' )
            plt.subplot(212)
            plt.plot( dfPrice.index, ldfFeatures[i]['XOM'].values, 'g-' )
            plt.show()
     
    ''' Pick Test and Training Points '''
    lSplit = int(len(ldtTimestamps) * 0.7)
    dtStartTrain = ldtTimestamps[0]
    dtEndTrain = ldtTimestamps[lSplit]
    dtStartTest = ldtTimestamps[lSplit+1]
    dtEndTest = ldtTimestamps[-1]
     
    ''' Stack all information into one Numpy array ''' 
    naFeatTrain = ftu.stackSyms( ldfFeatures, dtStartTrain, dtEndTrain )
    naFeatTest = ftu.stackSyms( ldfFeatures, dtStartTest, dtEndTest )
    
    ''' Normalize features, use same normalization factors for testing data as training data '''
    ltWeights = ftu.normFeatures( naFeatTrain, -1.0, 1.0, False )
    ''' Normalize query points with same weights that come from test data '''
    ftu.normQuery( naFeatTest[:,:-1], ltWeights )

    learnerTest( naFeatTrain, naFeatTest )
    
    
    
