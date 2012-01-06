'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various feature functions

'''

''' Python imports '''
import random

''' 3rd Party Imports '''
import pandas as pand
import numpy as np

''' QSTK Imports '''
import qstkutil.tsutil as tsu


def featMA( dData, lLookback=30, bRel=True ):
    '''
    @summary: Calculate moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) ) 
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        lSum = 0
        
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            
            if pand.isnull(tsPrice[i]):
                continue
                
            
            if pand.notnull( tsPrice[i] ):
                lSum += tsPrice[i]
            
            if i < lLookback - 1:
                tsRet[i] = float('nan')
                continue
            
            ''' If we have the bare min, take the avg, else remove the last and take the avg '''
            tsRet[i] = np.sum( tsPrice[i-(lLookback-1):i+1]) / lLookback
            
            ''' See if we should make this relative moving average '''
            if bRel:
                tsRet[i] /= tsPrice[i]
            
    return dfRet


def featRSI( dData, lLookback=14 ):
    '''
    @summary: Calculate RSI
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past, 14 is standard
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    fLookback = float(lLookback)
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        
        fGain = 0.0
        fLoss = 0.0
        
        lNonNull=0
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            
            if pand.isnull( tsPrice[i] ):
                continue
            else:
                lNonNull += 1
                 
            ''' Once we have the proper number of periods we smooth the totals '''
            if lNonNull > fLookback:
                fGain *= (fLookback - 1) / fLookback
                fLoss *= (fLookback - 1) / fLookback
                
            ''' Calculate gain or loss and add to total '''
            if lNonNull > 1:
                fDelta = tsPrice[i] - tsPrice[i-1]
                if fDelta > 0.0:
                    fGain += fDelta / fLookback
                else:
                    fLoss += fDelta / fLookback
            
            ''' Calculate RS and then RSI '''
            if i > fLookback - 1:
                if fLoss == 0.0:
                    tsRet[i] = 100.0
                elif fGain == 0.0:
                    tsRet[i] = 0.0
                else:
                    fRS = fGain / fLoss
                    tsRet[i] = 100 - 100 / (1-fRS)
            
            
    return dfRet


def featDrawDown( dData ):
    '''
    @summary: Calculate Drawdown for the stock
    @param dData: Dictionary of data to use
    @return: DataFrame array containing values
    @warning: Drawdown and RunUp can depend heavily on sample period
    '''
    
    dfPrice = dData['close']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        fPeak = tsPrice[0]
        for i in range(len(tsPrice.index)):
            if tsPrice[i] > fPeak or pand.isnull(fPeak):
                fPeak = tsPrice[i]
            
            tsRet[i] = tsPrice[i] / fPeak

    return dfRet

def featRunUp( dData ):
    '''
    @summary: CalculateRunup for the stock
    @param dData: Dictionary of data to use
    @return: DataFrame array containing feature values
    @warning: Drawdown and RunUp can depend heavily on when the sample starts
    '''
    
    dfPrice = dData['open']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        fTrough = tsPrice[0]
        for i in range(len(tsPrice.index)):
            if tsPrice[i] < fTrough or pand.isnull(fTrough):
                fTrough = tsPrice[i]
            
            tsRet[i] = tsPrice[i] / fTrough

    return dfRet


def featVolumeDelta( dData, lLookback=30 ):
    '''
    @summary: Calculate moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to use for MA
    @return: DataFrame array containing values
    '''
    
    dfVolume = dData['volume']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfVolume.index, columns=dfVolume.columns, data=np.zeros(dfVolume.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfVolume.columns:
        
        tsVol = dfVolume[sStock]
        tsRet = dfRet[sStock]
        lSum = 0
        
        ''' Loop over time '''
        for i in range(len(tsVol.index)):
            
            if pand.notnull( tsVol[i] ):
                lSum += tsVol[i]
            
            if i < lLookback - 1:
                tsRet[i] = float('nan')
                continue
            
            ''' If we have the bare min, take the avg, else remove the last and take the avg '''
            tsRet[i] = np.sum( tsVol[i-(lLookback-1):i+1]) / lLookback
            
            ''' Make this relative to the MA of volume '''
            tsRet[i] /= tsVol[i]
            
    return dfRet

def featAroon( dData, bDown=False ):
    '''
    @summary: Calculate Aroon - indicator indicating days since a 25-day high/low, weighted between 0 and 100
    @param dData: Dictionary of data to use
    @param bDown: If false, calculates aroonUp (high), else aroonDown (lows)
    @return: DataFrame array containing feature values
    '''
    
    dfPrice = dData['close']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Peaks will be a sorted, descending list of highs and indexes '''
        lfPeaks = []
        
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            j = 0
            while j < (len(lfPeaks)):
                if bDown:
                    ''' If down, use troughts '''
                    if tsPrice[i] < lfPeaks[j][0]:
                        break
                else:
                    ''' If up, use peaks '''
                    if tsPrice[i] > lfPeaks[j][0]:
                        break
                j+=1
                
            ''' Insert into sorted list, remove all lesser, older peaks '''
            lfPeaks.insert( j, (tsPrice[i], i) )
            lfPeaks = lfPeaks[:j+1]
            
            ''' Remove all outdated peaks '''
            j = 0
            while j < (len(lfPeaks)):
                if i - lfPeaks[j][1] > 25:
                    lfPeaks.pop(j)
                    continue
                    
                j += 1    
            
            #print lfPeaks
            
            tsRet[i] = ((25.0 - (i - lfPeaks[0][1])) / 25.0) * 100.0
            
            ''' perturb value '''
            random.seed(i)
            tsRet[i] += random.uniform( -0.0001, 0.0001 )

    return dfRet


def featStochastic( dData, lLookback=14, bFast=True, lMA=3 ):
    '''
    @summary: Calculate stochastic oscillator - indicates what range of recent low-high spread we are in.
    @param dData: Dictionary of data to use
    @param bFast: If false, do slow stochastics, 3 day MA, if not use fast, no MA
    @return: DataFrame array containing feature values
    '''

    dfLow = dData['low']
    dfHigh = dData['high']
    dfPrice = dData['close']

    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsHigh = dfHigh[sStock]
        tsLow = dfLow[sStock]
        tsRet = dfRet[sStock]
           
        ''' For slow stochastic oscillator we need to remember 3 past values '''
        lfPastStoch = []
        
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            
            ''' NaN if not enough data to do lookback '''
            if i < lLookback:
                tsRet[i] = float('nan')
                continue    
            
            fLow = 1E300
            fHigh = -1E300
            ''' Find highest high and lowest low '''
            for j in range(lLookback):
                
                lInd = i-j
                
                if tsHigh[lInd] > fHigh:
                    fHigh = tsHigh[lInd]
                if tsLow[lInd] < fLow:
                    fLow = tsLow[lInd]
             
            fStoch = (tsPrice[i] - fLow) / (fHigh - fLow)
            
            ''' For fast we just take the stochastic value, slow we need 3 day MA '''
            if bFast:
                tsRet[i] = fStoch   
            else:
                if len(lfPastStoch) < lMA:
                    lfPastStoch.append(fStoch)
                    continue
                
                lfPastStoch.append(fStoch)
                lfPastStoch.pop(0)
                
                tsRet[i] = sum(lfPastStoch) / float(len(lfPastStoch))
                 
                

    return dfRet

def featBeta( dData, lLookback=14, sMarket='SPY' ):
    '''
    @summary: Calculate beta relative to a given stock/index.
    @param dData: Dictionary of data to use
    @param sStock: Stock to calculate beta relative to
    @return: DataFrame array containing feature values
    '''

    dfPrice = dData['close']

    ''' Calculate returns '''
    naRets = dfPrice.values.copy()
    tsu.returnize1(naRets)
    dfHistReturns = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=naRets )
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfHistReturns.columns:   
        tsHistReturns = dfHistReturns[sStock]
        tsMarket = dfHistReturns[sMarket]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        for i in range(len(tsRet.index)):
            
            ''' NaN if not enough data to do lookback '''
            if i < lLookback:
                tsRet[i] = float('nan')
                continue    
            
            naStock = tsHistReturns[ i - lLookback:i ]
            naMarket = tsMarket[ i - lLookback:i ]
            
            ''' Beta is the slope the line, with market returns on X, stock returns on Y '''
            fBeta, unused = np.polyfit( naMarket, naStock, 1)
            
            tsRet[i] = fBeta

    return dfRet

if __name__ == '__main__':
    pass