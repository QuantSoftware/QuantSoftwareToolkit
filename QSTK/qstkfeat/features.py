'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various feature functions

'''

#''' Python imports '''
import random

#''' 3rd Party Imports '''
import pandas as pand
import numpy as np
import datetime as dt

#''' QSTK Imports '''
import QSTK.qstkutil.tsutil as tsu
from QSTK.qstkutil import DataAccess as da
import QSTK.qstkutil.qsdateutil as du

def featMomentum(dData, lLookback=20, b_human=False ):
    '''
    @summary: N day cumulative return (based on 1) indicator
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    dfPrice = dData['close'].copy()
    
    #Calculate Returns
    tsu.returnize0(dfPrice.values)
    
    #Calculate rolling sum
    dfRet = pand.rolling_sum(dfPrice, lLookback)
    
    
    return dfRet

def featHiLow(dData, lLookback=20, b_human=False ):
    '''
    @summary: 1 represents a high for the lookback -1 represents a low
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    dfPrice = dData['close']
    
    #Find Max for each price for lookback
    maxes = pand.rolling_max(dfPrice, lLookback, 1)
    
    #Find Min
    mins = pand.rolling_min(dfPrice, lLookback, 1)
    
    #Find Range
    ranges = maxes - mins
    
    #Calculate (price - min) * 2 / range -1
    dfRet = (((dfPrice-mins)*2)/ranges)-1
    
    return dfRet

def featDate(dData, b_human=False ):
    '''
    @summary: Returns -1 for jan 1st 1 for dec 31st
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    
    dfPrice = dData['close']
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        #'' Loop over time '''
        for i in range(len(tsPrice.index)):
            #get current date
            today = tsPrice.index[i]
            
            #get days since January 1st
            days = today - dt.datetime(today.year, 1, 1)
            
            # multiply by 2, divide by 365, subtract 1
            tsRet[i] = float(days.days * 2) / 365 - 1
            
    return dfRet


def featOption(dData, b_human=False ):
    '''
    @summary: Returns 1 if option close is today, -1 if it was yesterday
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    dfPrice = dData['close']
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        #'' Loop over time '''
        for i in range(len(tsPrice.index)):
            #get current date
            today = tsPrice.index[i]
            
            #get last option close
            last_close = du.getLastOptionClose(today, tsPrice.index)
            
            #get next option close
            next_close = du.getNextOptionClose(today, tsPrice.index)
            
            #get days between
            days_between = next_close - last_close
            
            #get days since last close
            days = today - last_close
            
            # multiply by 2, divide by 365, subtract 1
            tsRet[i] = float(days.days * 2) / days_between.days - 1
            
    return dfRet

def featMA( dData, lLookback=30, bRel=True, b_human=False ):
    '''
    @summary: Calculate moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    dfRet = pand.rolling_mean(dfPrice, lLookback)
    
    if bRel:
        dfRet = dfRet / dfPrice
    if b_human:  
        data2 = dfRet * dData['close']
        data3 = pand.DataFrame({"Raw":data2[data2.columns[0]]})
        for sym in dfRet.columns:
            if sym != '$SPX' and sym != '$VIX':
                data3[sym + " Moving Average"] = data2[sym]
                data3[sym] = dData['close'][sym]
        del data3['Raw']
        return data3
    return dfRet


def featEMA( dData, lLookback=20, bRel=True,  b_human=False ):
    '''
    @summary: Calculate exponential moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    dfRet = pand.ewma(dfPrice, span=lLookback)
    
    if bRel:
        dfRet = dfRet / dfPrice;
    if b_human:  
        data2 = dfRet*dData['close']
        data3 = pand.DataFrame({"Raw":data2[data2.columns[0]]})
        for sym in dfRet.columns:
            if sym != '$SPX' and sym != '$VIX':
                data3[sym + " Moving Average"] = data2[sym]
                data3[sym] = dData['close'][sym]
        del data3['Raw']
        return data3          
    return dfRet

def featSTD( dData, lLookback=20, bRel=True,  b_human=False ):
    '''
    @summary: Calculate standard deviation
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close'].copy()
    
    tsu.returnize1(dfPrice.values)
    dfRet = pand.rolling_std(dfPrice, lLookback)
    
    if bRel:
        dfRet = dfRet / dfPrice
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet

def featRSI( dData, lLookback=14,  b_human=False):
    '''
    @summary: Calculate RSI
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past, 14 is standard
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''

    # create deltas per day
    dfDelta = dData['close'].copy()
    dfDelta.ix[1:,:] -= dfDelta.ix[:-1,:].values
    dfDelta.ix[0,:] = np.NAN

    dfDeltaUp = dfDelta
    dfDeltaDown = dfDelta.copy()
    
    # seperate data into positive and negative for easy calculations
    for sColumn in dfDeltaUp.columns:
        tsColDown = dfDeltaDown[sColumn]
        tsColDown[tsColDown >= 0] = 0 
        
        tsColUp = dfDeltaUp[sColumn]
        tsColUp[tsColUp <= 0] = 0
    
    # Note we take abs() of negative values, all should be positive now
    dfRolUp = pand.rolling_mean(dfDeltaUp, lLookback, min_periods=1)
    dfRolDown = pand.rolling_mean(dfDeltaDown, lLookback, min_periods=1).abs()
    
    # relative strength
    dfRS = dfRolUp / dfRolDown
    dfRSI = 100.0 - (100.0 / (1.0 + dfRS))
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    
    return dfRSI


def featDrawDown( dData, lLookback=30,  b_human=False):
    '''
    @summary: Calculate Drawdown for the stock
    @param dData: Dictionary of data to use
    @param lLookback: Days to look back
    @return: DataFrame array containing values
    @param b_human: if true return dataframe to plot
    @warning: Drawdown and RunUp can depend heavily on sample period
    '''
    
    dfPrice = dData['close']
    
    #''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    dfMax = pand.rolling_max(dfPrice, lLookback)
    return (dfMax - dfPrice) / dfMax;
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet

def featRunUp( dData, lLookback=30, b_human=False ):
    '''
    @summary: CalculateRunup for the stock
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to calculate min over 
    @return: DataFrame array containing feature values
    @param b_human: if true return dataframe to plot
    @warning: Drawdown and RunUp can depend heavily on when the sample starts
    '''
    
    dfPrice = dData['close']
    
    dfMax = pand.rolling_min(dfPrice, lLookback)
    return dfPrice / dfMax;
            
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet


def featVolumeDelta( dData, lLookback=30, b_human=False ):
    '''
    @summary: Calculate moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to use for MA
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfVolume = dData['volume']
    
    dfRet = pand.rolling_mean(dfVolume, lLookback)
    dfRet /= dfVolume
        
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']    
    return dfRet

def featAroon( dData, bDown=False, lLookback=25, b_human=False ):
    '''
    @summary: Calculate Aroon - indicator indicating days since a 25-day 
              high/low, weighted between 0 and 100
    @param dData: Dictionary of data to use
    @param bDown: If false, calculates aroonUp (high), else aroonDown (lows)
    @param lLookback: Days to lookback to calculate high/low from
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing feature values
    '''
    
    dfPrice = dData['close']

    #Feature DataFrame will be 1:1, we can use the price as a template
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, 
                            data=np.zeros(dfPrice.shape) )
    
    #Loop through time
    for i in range(dfPrice.shape[0]):
        if( (i-lLookback) < 0 ):
            dfRet.ix[i,:] = np.NAN
        else:
            if bDown:
                dfRet.ix[i,:] = dfPrice.values[i:(i-lLookback):-1,:].argmin(
                                axis=0)
            else:
                dfRet.ix[i,:] = dfPrice.values[i:(i-lLookback):-1,:].argmax(
                                axis=0)
    
    dfRet = ((lLookback - 1.) - dfRet) / (lLookback - 1.) * 100.

    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet


def featAroonDown( dData, lLookback=25, b_human=False ):
    '''
    @summary: Wrapper to call aroon with flag = true
    '''
    return featAroon(dData, bDown=True, lLookback=lLookback, b_human=b_human)


def featStochastic( dData, lLookback=14, bFast=True, lMA=3, b_human=False ):
    '''
    @summary: Calculate stochastic oscillator - indicates what range of recent low-high spread we are in.
    @param dData: Dictionary of data to use
    @param bFast: If false, do slow stochastics, 3 day MA, if not use fast, no MA
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing feature values
    '''

    dfLow = dData['low']
    dfHigh = dData['high']
    dfPrice = dData['close']

    
    #''' Loop through stocks '''
    dfLows = pand.rolling_min(dfLow, lLookback)
    dfHighs = pand.rolling_max(dfHigh, lLookback)
    
    dfStoch = (dfPrice - dfLows) / (dfHighs - dfLows)
            
    #''' For fast we just take the stochastic value, slow we need 3 day MA '''
    if not bFast:
       dfStoch = pand.rolling_mean(dfStoch, lMA)
                 
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    
    return dfStoch

def featBeta( dData, lLookback=14, sMarket='$SPX', b_human=False ):
    '''
    @summary: Calculate beta relative to a given stock/index.
    @param dData: Dictionary of data to use
    @param sStock: Stock to calculate beta relative to
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing feature values
    '''

    dfPrice = dData['close']

    #''' Calculate returns '''
    dfRets = dfPrice.copy()
    tsu.returnize1(dfRets.values)

    tsMarket = dfRets[sMarket]

    dfRet = pand.rolling_cov(tsMarket, dfRets, lLookback)
    dfRet /= dfRet[sMarket]
   
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet

def featBollinger( dData, lLookback=20, b_human=False ):
    '''
    @summary: Calculate bollinger position as a function of std deviations.
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to calculate moving average over
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing feature values
    '''
    if b_human:
        dfPrice = dData['close']
        nstdsRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
        #average minus standard deviation
        pstdsRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )      
        data3 = pand.DataFrame({"Raw":dfPrice[dfPrice.columns[0]]})
        for sym in dfPrice.columns:
            if sym != '$SPX' and sym != '$VIX':
                tsPrice = dfPrice[sym]
                nstdRet = nstdsRet[sym]
                pstdRet = pstdsRet[sym]
                for i in range(len(tsPrice.index)):
                    if i < lLookback - 1:
                        nstdRet[i] = float('nan')
                        pstdRet[i] = float('nan')
                        continue    
                    fAvg = np.average( tsPrice[ i-(lLookback-1):i+1 ] )
                    fStd = np.std( tsPrice[ i-(lLookback-1):i+1 ] )
                    pstdRet[i] = fAvg+2.0*fStd
                    nstdRet[i] = fAvg-2.0*fStd  
                data3[sym] = dfPrice[sym]
                data3[sym + " Lower"] = nstdsRet[sym]
                data3[sym + " Upper"] = pstdsRet[sym]
        del data3['Raw']
        return data3
    else:
        dfPrice = dData['close']
        #''' Feature DataFrame will be 1:1, we can use the price as a template '''
        dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
        
        #''' Loop through stocks '''
        dfAvg = pand.rolling_mean(dfPrice, lLookback)
        dfStd = pand.rolling_std(dfPrice, lLookback)
        return (dfPrice - dfAvg) / (2.0*dfStd)


def featCorrelation( dData, lLookback=20, sRel='$SPX', b_human=False ):
    '''
    @summary: Calculate correlation of two stocks.
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to calculate moving average over
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing feature values
    '''

    dfPrice = dData['close']
    
    if sRel not in dfPrice.columns:
        raise KeyError( "%s not found in data provided to featCorrelation"%sRel )
       
    #''' Calculate returns '''
    naRets = dfPrice.values.copy()
    tsu.returnize1(naRets)
    dfHistReturns = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=naRets )

    #''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    #''' Loop through stocks '''
    for sStock in dfHistReturns.columns:   
        tsHistReturns = dfHistReturns[sStock]
        tsRelativeReturns = dfHistReturns[sRel]
        tsRet = dfRet[sStock]
        
        #''' Loop over time '''
        for i in range(len(tsHistReturns.index)):
            
            #''' NaN if not enough data to do lookback '''
            if i < lLookback - 1:
                tsRet[i] = float('nan')
                continue    
            
            naCorr = np.corrcoef( tsHistReturns[ i-(lLookback-1):i+1 ], tsRelativeReturns[ i-(lLookback-1):i+1 ] )
            
            tsRet[i] = naCorr[0,1]

    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet

def featPrice(dData, b_human=False):
    '''
    @summary: Price feature
    @param dData: Dictionary of data to use
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dData['close']

def featVolume(dData, b_human=False):
    '''
    @summary: Volume feature
    @param dData: Dictionary of data to use
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dData['volume']


def featRand( dData, b_human=False ):
    '''
    @summary: Random feature - used for robustness testing
    @param dData: Dictionary of data to use
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    #''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, 
                            data=np.random.randn(*dfPrice.shape) )
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet


if __name__ == '__main__':
    pass
