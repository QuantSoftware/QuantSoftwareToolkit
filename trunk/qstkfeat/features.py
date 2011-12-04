'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various feature functions

'''

''' 3rd Party Imports '''
import pandas as pand
import numpy as np

def featMA( dfPrice, lLookback=30, bRel=True ):
    '''
    @summary: Calculate moving average
    @param dfPrice: Price data for all the stocks
    @param lLookback: Number of days to look in the past
    @return: DataFrame array containing values
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) ) 
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        lSum = 0
        
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            
            if pand.notnull( tsPrice[i] ):
                lSum += tsPrice[i]
            
            if i < lLookback - 1:
                tsRet[i] = float('nan')
                continue
            
            ''' If we have the bare min, take the avg, else remove the last and take the avg '''
            if i == lLookback - 1:
                tsRet[i] = (lSum / lLookback) 
            else:
                lSum -= tsPrice[i-lLookback]
                tsRet[i] = (lSum / lLookback)
            
            ''' See if we should make this relative moving average '''
            if bRel:
                tsRet[i] /= tsPrice[i]
    return dfRet


def featRSI( dfPrice, lLookback=14 ):
    '''
    @summary: Calculate RSI
    @param dfPrice: Price data for all the stocks
    @param lLookback: Number of days to look in the past, 14 is standard
    @return: DataFrame array containing values
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    fLookback = float(lLookback)
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
        
        fGain = 0.0
        fLoss = 0.0
        
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
                 
            ''' Once we have the proper number of periods we smooth the totals '''
            if i > fLookback:
                fGain *= (fLookback - 1) / fLookback
                fLoss *= (fLookback - 1) / fLookback
                
            ''' Calculate gain or loss and add to total '''
            if i > 0:
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

def featDrawDown( dfPrice ):
    '''
    @summary: Calculate Drawdown for the stock
    @param dfPrice: Price data for all the stocks
    @return: DataFrame array containing values
    @warning: Drawdown and RunUp can depend heavily on sample period
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        fPeak = tsPrice[0]
        for i in range(len(tsPrice.index)):
            if tsPrice[i] > fPeak:
                fPeak = tsPrice[i]
            
            tsRet[i] = tsPrice[i] / fPeak

    return dfRet

def featRunUp( dfPrice ):
    '''
    @summary: CalculateRunup for the stock
    @param dfPrice: Price data for all the stocks
    @return: DataFrame array containing feature values
    @warning: Drawdown and RunUp can depend heavily on when the sample starts
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        fTrough = tsPrice[0]
        for i in range(len(tsPrice.index)):
            if tsPrice[i] < fTrough:
                fTrough = tsPrice[i]
            
            tsRet[i] = tsPrice[i] / fTrough

    return dfRet


def featVolumeDelta( dfVolume, lLookback=30 ):
    '''
    @summary: Calculate moving average
    @param dfVolume: Colume data for all the stocks
    @param lLookback: Number of days to use for MA
    @return: DataFrame array containing values
    '''
    
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
            if i == lLookback - 1:
                tsRet[i] = (lSum / lLookback) 
            else:
                lSum -= tsVol[i-lLookback]
                tsRet[i] = (lSum / lLookback)
            
            ''' Make this relative to the MA of volume '''
            tsRet[i] /= tsVol[i]
            
    return dfRet

def featAroon( dfPrice, bDown=False ):
    '''
    @summary: Calculate Aroon - indicator indicating days since a 25-day high/low, weighted between 0 and 100
    @param dfPrice: Price data for all the stocks
    @param bDown: If false, calculates aroonUp (high), else aroonDown (lows)
    @return: DataFrame array containing feature values
    '''
    
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
            
            # print lfPeaks
            
            tsRet[i] = ((25.0 - (i - lfPeaks[0][1])) / 25.0) * 100.0

    return dfRet

if __name__ == '__main__':
    pass
