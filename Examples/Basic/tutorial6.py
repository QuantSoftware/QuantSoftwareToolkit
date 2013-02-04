'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on June 1, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Demonstrates the retrieval and use of Compustat data from the DataAccess object.
'''

### You'll need compustat data license for this tutorial.

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
from math import isnan
from copy import copy


symbols = ['GE','MSFT','XOM','PFE','C','WMT','INTC','AAPL','GOOG']

''' Create compustat object and query it for some information '''

compustatObj = da.DataAccess('Compustat')
compustatObj.get_info()


''' Get data items and create dictionary to translate between string and index '''
lsItems = compustatObj.get_data_labels()
dLabel = dict( zip(lsItems,range(len(lsItems))) )
print 'Valid data items (sorted):\n', sort(lsItems[:])

    

''' Create timestamps for 5 year period, must include all days, financial report may have been filed on non-NYSE day '''
''' get todays date, time = 16:00:00 '''
dtEnd = dt.datetime.combine( dt.datetime.now().date(), dt.time(16) )
dtStart = dtEnd.replace( year=dtEnd.year-5 )

tsAll = [ dtStart ]
while( tsAll[-1] != dtEnd ):
    tsAll.append( tsAll[-1] + dt.timedelta(days=1) )


''' Query data object '''
dmValues = compustatObj.get_data( tsAll, symbols, lsItems)


''' Keep track of non-nan data entries '''
llTotal = [0] * len(lsItems)
llValid = [0] * len(lsItems)
    
for lStock in range(len(symbols)):

    dmKeys = dmValues[ dLabel['gvkey'] ]
    
    ''' Loop through all time indexes '''
    for i, row in enumerate( dmKeys.values ):
        
        ''' Check nan gvkey value, indicating an invalid entry row skip '''
        if( isnan(row[lStock]) ):
            continue
            
        ''' check for other valid entries in the other data types '''
        for lInd in range( len(lsItems) ):
            llTotal[lInd] = llTotal[lInd] + 1
            if( not isnan(dmValues[lInd].values[i,lStock]) ):
                llValid[lInd] = llValid[lInd] + 1 
                
''' sort and print results by percentage valid data '''

ltBoth = []
lNonZero = 0
lHundred = 0
for i, sLabel in enumerate( lsItems ):
    ltBoth.append( ( (llValid[i] * 100.0 / llTotal[i]), sLabel ) )
    if not llValid[i] == 0:
        lNonZero = lNonZero + 1
    if llValid[i] == llTotal[i]:
        lHundred = lHundred + 1
    
ltBoth.sort()
ltBoth.reverse()

for tRes in ltBoth:
    print '%10s: %.02lf%%'%( tRes[1], tRes[0] )
    
print '\n%i out of %i elemenets non-zero.'%(lNonZero, len(lsItems))
print '%i out of %i elemenets have 100%% participation.'%(lHundred, len(lsItems))


''' Retrieve and plot quarterly earnings per share '''

dmEps = dmKeys = dmValues[ dLabel['EPSPIQ'] ]
naEps = dmEps.values
tsu.fillforward( naEps )

plt.clf()

for i, sStock in enumerate( symbols ):
    plt.plot( tsAll, naEps[:,i] )
    
plt.gcf().autofmt_xdate(rotation=45)
plt.legend( symbols, loc='upper left' )
plt.title('EPS of various stocks')

savefig('tutorial6.pdf',format='pdf')

