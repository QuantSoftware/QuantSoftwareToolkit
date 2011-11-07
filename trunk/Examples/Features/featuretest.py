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
from qstkfeat.featutil import applyFeatures



if __name__ == '__main__':
    
    ''' Use Dow 30 '''
    lsSym = ['AA', 'AXP', 'BA', 'BAC', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'HD', 'HPQ', 'IBM', 'INTC', 'JNJ', \
             'JPM', 'KFT', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'PFE', 'PG', 'T', 'TRV', 'UTX', 'WMT', 'XOM'  ]
    
    ''' Get data for 2009-2010 '''
    dtStart = dt.datetime(2009,1,01)
    dtEnd = dt.datetime(2010,12,31)
    
    norObj = da.DataAccess('Norgate')      
    ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, dt.timedelta(hours=16) )
    
    dfPrice = norObj.get_data( ldtTimestamps, lsSym, 'close' )
    
    lfcFeatures = [ featMA, featRSI ]

    ''' Default Arguments '''
    #ldArgs = [{}] * len(lfcFeatures) 
    
    ''' Custom Arguments '''
    ldArgs = [ {'lLookback':30},\
               {}]                    
    
    ''' Generate a list of FataFrames, one for each feature, with the same index/column structure as price data '''
    ldfFeatures = applyFeatures( dfPrice, lfcFeatures, ldArgs )
    
    ''' Plot feature for XOM '''
    for i, fcFunc in enumerate(lfcFeatures):
        if fcFunc.__name__ == 'featMA':
            plt.clf()
            plt.plot( dfPrice.index, dfPrice['XOM'].values, 'r-' )
            print  ldfFeatures[i]['XOM'].values
            plt.plot( dfPrice.index, ldfFeatures[i]['XOM'].values, 'g-' )
            plt.show()
     
    
    
    
    