'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on August 29, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Demonstrates the use of the NAG portfolio optimization call.
'''

# You'll need NAG license for this tutorial - Please use tutorial8 instead.

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt

import matplotlib.pyplot as plt
from pylab import *
from math import isnan
from copy import copy

''' Function gets a 100 sample point frontier for given returns '''
def getFrontier(naData, lPeriod):
    ''' Special case for fTarget = None, just get average returns '''
    (naAvgRets, naStd) = tsu.getOptPort( naData, None, lPeriod )
    fMin = np.min(naAvgRets)
    fMax = np.max(naAvgRets)
    
    fStep = (fMax - fMin) / 100.0
    
    lfReturn =  [fMin + x * fStep for x in range(101)]
    lfStd = []
    lnaPortfolios = []
    
    ''' Call the function 100 times for the given range '''
    for fTarget in lfReturn: 
        (naWeights, fStd) = tsu.getOptPort( naData, fTarget, lPeriod )
        lfStd.append(fStd)
        lnaPortfolios.append( naWeights )
    
    return (lfReturn, lfStd, lnaPortfolios, naAvgRets, naStd)
    


''' ******************************************************* '''
''' ******************** MAIN SCRIPT ********************** '''
''' ******************************************************* '''

''' S&P100 '''
lsSymbols = [ 'AA', 'AAPL', 'ABT', 'AEP', 'ALL', 'AMGN', 'AMZN', 'AVP', 'AXP', 'BA', 'BAC', 'BAX', 'BHI', 'BK', 'BMY', 'BNI', 'C', 'CAT', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'COV', 'CPB', 'CSCO', 'CVS', 'CVX', 'DD', 'DELL', 'DIS', 'DOW', 'DVN', 'EMC', 'ETR', 'EXC', 'F', 'FDX', 'GD', 'GE', 'GILD', 'GOOG', 'GS', 'HAL', 'HD', 'HNZ', 'HON', 'HPQ', 'IBM', 'INTC', 'JNJ', 'JPM', 'KFT', 'KO', 'LMT', 'LOW', 'MA', 'MCD', 'MDT', 'MMM', 'MO', 'MRK', 'MS', 'MSFT', 'NKE', 'NOV', 'NSC', 'NYX', 'ORCL', 'OXY', 'PEP', 'PFE', 'PG', 'PM', 'QCOM', 'RF', 'RTN', 'S', 'SGP', 'SLB', 'SLE', 'SO', 'T', 'TGT', 'TWX', 'TXN', 'TYC', 'UNH', 'UPS', 'USB', 'UTX', 'VZ', 'WAG', 'WFC', 'WMB', 'WMT', 'WY', 'WYE', 'XOM', 'XRX']

''' Create norgate object and query it for stock data '''
norgateObj = da.DataAccess('Yahoo')

lsAll = norgateObj.get_all_symbols()
intersect = set(lsAll) & set(lsSymbols)

if len(intersect) < len(lsSymbols):
    print "Warning: S&P100 contains symbols that do not exist: ", 
    print set(lsSymbols) - intersect 
    
    lsSymbols = sort(list( intersect )) 

''''Read in historical data'''
lYear = 2009
dtEnd = dt.datetime(lYear+1,1,1) 
dtStart = dtEnd - dt.timedelta(days=365) 
dtTest = dtEnd + dt.timedelta(days=365) 
timeofday=dt.timedelta(hours=16)

ldtTimestamps = du.getNYSEdays( dtStart, dtEnd, timeofday )
ldtTimestampTest = du.getNYSEdays( dtEnd, dtTest, timeofday )

dmClose = norgateObj.get_data(ldtTimestamps, lsSymbols, "close")
dmTest = norgateObj.get_data(ldtTimestampTest, lsSymbols, "close")

naData = dmClose.values.copy()
naDataTest = dmTest.values.copy()

tsu.fillforward(naData)
tsu.fillbackward(naData)
tsu.returnize1(naData)

tsu.fillforward(naDataTest)
tsu.fillbackward(naDataTest)
tsu.returnize1(naDataTest)

lPeriod = 21

''' Get efficient frontiers '''
(lfReturn, lfStd, lnaPortfolios, naAvgRets, naStd) = getFrontier( naData, lPeriod )
(lfReturnTest, lfStdTest, unused, unused, unused) = getFrontier( naDataTest, lPeriod )

plt.clf()
fig = plt.figure()

''' Plot efficient frontiers '''
plt.plot(lfStd,lfReturn, 'b')
plt.plot(lfStdTest,lfReturnTest, 'r')

''' Plot where efficient frontier WOULD be the following year '''
lfRetTest = []
lfStdTest = []
naRetsTest = tsu.getReindexedRets( naDataTest, lPeriod)
for naPortWeights in lnaPortfolios:
    naPortRets =  np.dot( naRetsTest, naPortWeights)
    lfStdTest.append( np.std(naPortRets) )
    lfRetTest.append( np.average(naPortRets) )

plt.plot(lfStdTest,lfRetTest,'k')

''' plot some arrows showing transition of efficient frontier '''
for i in range(0,101,10):
    arrow( lfStd[i],lfReturn[i], lfStdTest[i]-lfStd[i], lfRetTest[i]-lfReturn[i], color='k' )

''' Plot indifidual stock risk/return as green + ''' 
for i, fReturn in enumerate(naAvgRets):
    plt.plot( naStd[i], fReturn, 'g+' ) 

plt.legend( ['2009 Frontier', '2010 Frontier', 'Performance of \'09 Frontier in 2010'], loc='lower right' )

plt.title('Efficient Frontier For S&P 100 ' + str(lYear))
plt.ylabel('Expected Return')
plt.xlabel('StDev')

savefig('tutorial7.pdf',format='pdf')

    
    


