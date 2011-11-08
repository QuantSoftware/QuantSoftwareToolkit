'''
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
from qstkutil import DataAccess as da
from qstkutil import dateutil as du

from qstkfeat.features import featMA, featRSI
from qstkfeat.classes import classFutRet
import qstkfeat.featutil as ftu


def learnerTest( naFeatures ):
    
    
    ''' Split into test and training segments '''
    lStop = int(naFeatures.shape[0] * 0.7)
    naTrain = naFeatures[:lStop,:]
    naTest = naFeatures[lStop:,:]
    
    lfRes = []
    for lK in range(5,30,1):
        cLearn = ftu.createKnnLearner( naTrain, lKnn=lK )
        fError = 0.0

        naResult = cLearn.query( naTest[:,:-1] )
        naError = abs( naResult - naTest[:,-1] )
        lfRes.append( np.sum(naError) )
    
    ''' Generate error of 'dumb' case '''
    naGuess = np.ones( naTest.shape[0] ) * np.average( naTrain[:,-1] )
    lfGuess = [ np.sum( abs(naGuess - naTest[:,-1]) ) ] * len(lfRes)
    
    plt.clf()
    plt.plot( range(5,30,1), lfRes )
    plt.plot( range(5,30,1), lfGuess )
    plt.show()
    
    

if __name__ == '__main__':
    
    ''' Use Dow 30 '''
    lsSym = ['AA', 'AXP', 'BA', 'BAC', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'HD', 'HPQ', 'IBM', 'INTC', 'JNJ', \
             'JPM', 'KFT', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'PFE', 'PG', 'T', 'TRV', 'UTX', 'WMT', 'XOM'  ]
    lsSym = ['XOM']
    
    ''' Get data for 2009-2010 '''
    dtStart = dt.datetime(2010,8,01)
    dtEnd = dt.datetime(2010,12,31)
    
    norObj = da.DataAccess('Norgate')      
    ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )
    
    dfPrice = norObj.get_data( ldtTimestamps, lsSym, 'close' )
    
    ''' Imported functions from qstkfeat.features, NOTE: last function is classification '''
    lfcFeatures = [ featMA, featMA, featRSI, classFutRet ]

    ''' Default Arguments '''
    #ldArgs = [{}] * len(lfcFeatures) 
    
    ''' Custom Arguments '''
    ldArgs = [ {'lLookback':30},\
               {'lLookback':30, 'bRel':True},\
               {},\
               {}]                    
    
    ''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
    ldfFeatures = ftu.applyFeatures( dfPrice, lfcFeatures, ldArgs )
    
    ''' Plot feature for XOM '''
    for i, fcFunc in enumerate(lfcFeatures[:-1]):
        plt.clf()
        plt.subplot(211)
        plt.title( fcFunc.__name__ )
        plt.plot( dfPrice.index, dfPrice['XOM'].values, 'r-' )
        plt.subplot(212)
        plt.plot( dfPrice.index, ldfFeatures[i]['XOM'].values, 'g-' )
        plt.show()
            
    quit()
     
    ''' Stack all information into one Numpy array ''' 
    naFeatPts = ftu.stackSyms( ldfFeatures )
    
    ''' Normalize features '''
    ftu.normFeatures( naFeatPts, -1.0, 1.0, False )

    learnerTest( naFeatPts )
    
    
    