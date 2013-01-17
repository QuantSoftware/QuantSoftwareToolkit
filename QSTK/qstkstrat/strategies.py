'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Sep 27, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Various simple trading strategies to generate allocations.
'''

''' Python imports '''
import datetime as dt
from math import sqrt


''' 3rd party imports '''
import numpy as np
import pandas as pand

''' QSTK imports '''
import QSTK.qstkutil.tsutil as tsu


def stratGiven( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Simplest strategy, weights are provided through args.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    if not dFuncArgs.has_key('dmPrice'):
        print 'Error: Strategy requires dmPrice information'
        return
    
    if not dFuncArgs.has_key('lfWeights'):
        print 'Error: Strategy requires weight information'
        return
    
    dmPrice = dFuncArgs['dmPrice']
    lfWeights = dFuncArgs['lfWeights']
    
    ''' Generate two allocations, one for the start day, one for the end '''
    naAlloc = np.array( lfWeights ).reshape(1,-1)

    dfAlloc = pand.DataFrame( index=[dtStart], data=naAlloc, columns=(dmPrice.columns) )
    dfAlloc = dfAlloc.append( pand.DataMatrix(index=[dtEnd], data=naAlloc, columns=dmPrice.columns))
    dfAlloc['_CASH'] = 0.0
    
    return dfAlloc

def strat1OverN( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Evenly distributed strategy.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """        
    if not dFuncArgs.has_key('dmPrice'):
        print 'Error: Strategy requires dmPrice information'
        return
    
    dmPrice = dFuncArgs['dmPrice']
    
    lNumSym = len(dmPrice.columns)
    
    ''' Generate two allocations, one for the start day, one for the end '''
    naAlloc = (np.array( np.ones(lNumSym) ) * (1.0 / lNumSym)).reshape(1,-1)
    dfAlloc = pand.DataMatrix( index=[dtStart], data=naAlloc, columns=(dmPrice.columns) )
    dfAlloc = dfAlloc.append( pand.DataMatrix(index=[dtEnd], data=naAlloc, columns=dmPrice.columns))
    dfAlloc['_CASH'] = 0.0
    
    return dfAlloc
    

def stratMark( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Markovitz strategy, generates a curve and then chooses a point on it.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """         
    if not dFuncArgs.has_key('dmPrice'):
        print 'Error:', stratMark.__name__, 'requires dmPrice information'
        return
    
    if not dFuncArgs.has_key('sPeriod'):
        print 'Error:', stratMark.__name__, 'requires rebalancing period'
        return

    if not dFuncArgs.has_key('lLookback'):
        print 'Error:', stratMark.__name__, 'requires lookback'
        return

    if not dFuncArgs.has_key('sMarkPoint'):
        print 'Error:', stratMark.__name__, 'requires markowitz point to choose'
        return 

    ''' Optional variables '''
    if not dFuncArgs.has_key('bAddAlpha'):
        bAddAlpha = False
    else:
        bAddAlpha = dFuncArgs['bAddAlpha']
    
    dmPrice = dFuncArgs['dmPrice']
    sPeriod = dFuncArgs['sPeriod']
    lLookback = dFuncArgs['lLookback']
    sMarkPoint = dFuncArgs['sMarkPoint']

    ''' Select rebalancing dates '''
    drNewRange = pand.DateRange(dtStart, dtEnd, timeRule=sPeriod) + pand.DateOffset(hours=16)
    
    dfAlloc = pand.DataMatrix()
    ''' Go through each rebalance date and calculate an efficient frontier for each '''
    for i, dtDate in enumerate(drNewRange):
        dtStart = dtDate - pand.DateOffset(days=lLookback)
        
        if( dtStart < dmPrice.index[0] ):
            print 'Error, not enough data to rebalance'
            continue  
       
        naRets = dmPrice.ix[ dtStart:dtDate ].values.copy()
        tsu.returnize1(naRets)
        tsu.fillforward(naRets)
        tsu.fillbackward(naRets)
        
        ''' Add alpha to returns '''
        if bAddAlpha:
            if i < len(drNewRange) - 1:
                naFutureRets = dmPrice.ix[ dtDate:drNewRange[i+1] ].values.copy()
                tsu.returnize1(naFutureRets)
                tsu.fillforward(naFutureRets)
                tsu.fillbackward(naFutureRets)
                
                naAvg = np.mean( naFutureRets, axis=0 )
                
                ''' make a mix of past/future rets '''
                for i in range( naRets.shape[0] ):
                    naRets[i,:] = (naRets[i,:] + (naAvg*0.05)) / 1.05
                

        ''' Generate the efficient frontier '''
        (lfReturn, lfStd, lnaPortfolios) = getFrontier( naRets, fUpper=0.2, fLower=0.01 )
        
        lInd = 0
        
        '''
        plt.clf()
        plt.plot( lfStd, lfReturn)'''
        
        if( sMarkPoint == 'Sharpe'):
            ''' Find portfolio with max sharpe '''
            fMax = -1E300
            for i in range( len(lfReturn) ):
                fShrp = (lfReturn[i]-1) / (lfStd[i])
                if fShrp > fMax:
                    fMax = fShrp
                    lInd = i
            '''     
            plt.plot( [lfStd[lInd]], [lfReturn[lInd]], 'ro')
            plt.draw()
            time.sleep(2)
            plt.show()'''
            
        elif( sMarkPoint == 'MinVar'):
            ''' use portfolio with minimum variance '''
            fMin = 1E300
            for i in range( len(lfReturn) ):
                if lfStd[i] < fMin:
                    fMin = lfStd[i]
                    lInd = i
        
        elif( sMarkPoint == 'MaxRet'):
            ''' use Portfolio with max returns (not really markovitz) '''
            lInd = len(lfReturn)-1
        
        elif( sMarkPoint == 'MinRet'):
            ''' use Portfolio with min returns (not really markovitz) '''
            lInd = 0    
                
        else:
            print 'Warning: invalid sMarkPoint'''
            return
    
        
    
        ''' Generate allocation based on selected portfolio '''
        naAlloc = (np.array( lnaPortfolios[lInd] ).reshape(1,-1) )
        dmNew = pand.DataMatrix( index=[dtDate], data=naAlloc, columns=(dmPrice.columns) )
        dfAlloc = dfAlloc.append( dmNew )
    
    dfAlloc['_CASH'] = 0.0
    return dfAlloc

def stratMarkSharpe( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark with sharpe ratio point.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """        
    dFuncArgs['sMarkPoint'] = 'Sharpe'
    return stratMark( dtStart, dtEnd, dFuncArgs )
    
def stratMarkLowVar( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark and uses lowest variance ratio point.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    dFuncArgs['sMarkPoint'] = 'MinVar'
    return stratMark( dtStart, dtEnd, dFuncArgs )

def stratMarkMaxRet( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark and uses maximum returns.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    dFuncArgs['sMarkPoint'] = 'MaxRet'
    return stratMark( dtStart, dtEnd, dFuncArgs )
    
def stratMarkMinRet( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark and uses minimum returns.
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    dFuncArgs['sMarkPoint'] = 'MinRet'
    return stratMark( dtStart, dtEnd, dFuncArgs )
      
def stratMarkSharpeAlpha( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark and chooses the highest share point, uses future knowlege (alpha).
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    dFuncArgs['sMarkPoint'] = 'Sharpe'
    dFuncArgs['bAddAlpha'] = True
    return stratMark( dtStart, dtEnd, dFuncArgs )

def stratMarkMaxRetAlpha( dtStart, dtEnd, dFuncArgs ):
    """
    @summary Calls stratMark chooses the highest returns point, uses future knowlege (alpha).
    @param dtStart: Start date for portfolio
    @param dtEnd: End date for portfolio
    @param dFuncArgs: Dict of function args passed to the function
    @return DataFrame corresponding to the portfolio allocations
    """    
    dFuncArgs['sMarkPoint'] = 'MaxRet'
    dFuncArgs['bAddAlpha'] = True
    return stratMark( dtStart, dtEnd, dFuncArgs )


