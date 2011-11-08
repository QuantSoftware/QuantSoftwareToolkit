'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various feature functions

'''

''' 3rd Party Imports '''
import pandas as pand

def featMA( dfPrice, lLookback=30, bRel=False ):
    '''
    @summary: Calculate moving average
    @param dfPrice: Price data for all the stocks
    @param lLookback: Number of days to look in the past
    @return: DataFrame array containing values
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = dfPrice.copy(deep=True)
    
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
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = dfPrice.copy(deep=True)
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
            
            if i > fLookback - 1:
                if fLoss == 0.0:
                    tsRet[i] = 100.0
                elif fGain == 0.0:
                    tsRet[i] = 0.0
                else:
                    fRS = fGain / fLoss
                    tsRet[i] = 100 - 100 / (1-fRS)
            
            
    return dfRet


if __name__ == '__main__':
    pass