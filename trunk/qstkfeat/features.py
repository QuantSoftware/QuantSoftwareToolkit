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

''' Python imports '''
import random

''' 3rd Party Imports '''
import pandas as pand
import numpy as np

''' QSTK Imports '''
import qstkutil.tsutil as tsu

def featMomentum(dData, lLookback=20, b_human=False ):
    '''
    @summary: N day cumulative return (based on 1) indicator
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    dfPrice = dData['close']
    
    #Calculate Returns
    tsu.returnize1(dfPrice.values)
    
    #Calculate rolling sum
    dfRet = pand.rolling_sum(dfPrice, lLookback, lLookback)
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
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
    
    dfRet = pand.rolling_mean(dfPrice, lLookback, lLookback)
    
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


def featEMA( dData, lLookback=20, bRel=True,  b_human=False ):
    '''
    @summary: Calculate exponential moving average
    @param dData: Dictionary of data to use
    @param lLookback: Number of days to look in the past
    @param b_human: if true return dataframe to plot
    @return: DataFrame array containing values
    '''
    
    dfPrice = dData['close']
    
    dfRet = pand.ewma(dfPrice, span=lLookback, min_periods=lLookback)
    
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
    dfRet = pand.rolling_std(dfPrice, lLookback, lLookback)
    
    if bRel:
        dfRet = dfRet / dfPrice;
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
            
    
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet


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
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
            
            ''' Get starting and stopping indexes '''
            if i != len(tsPrice.index):
                lStop = i + 1
            else:
                lStop = None
                
            lStart = max( 0,  i - (lLookback - 1) )
 
            ''' Calculate peak value, and subsequent drawdown '''
            fPeak = np.max( tsPrice.values[ lStart:lStop ] )    
            
            tsRet[i] = tsPrice[i] / fPeak
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
    
    dfPrice = dData['open']
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        tsPrice = dfPrice[sStock]
        tsRet = dfRet[sStock]
           
        ''' Loop over time '''
        for i in range(len(tsPrice.index)):
                      
            ''' Get starting and stopping indexes '''
            if i != len(tsPrice.index):
                lStop = i + 1
            else:
                lStop = None
                
            lStart = max( 0,  i - (lLookback - 1) )
 
            ''' Calculate trough value, and subsequent drawdown '''
            fTrough = np.min( tsPrice.values[ lStart:lStop ] )    
            
            tsRet[i] = tsPrice[i] / fTrough
            if tsPrice[i] < fTrough or pand.isnull(fTrough):
                fTrough = tsPrice[i]
            
            tsRet[i] = tsPrice[i] / fTrough
            
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
        
    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']    
    return dfRet

def featAroon( dData, bDown=False, lLookback=25, b_human=False ):
    '''
    @summary: Calculate Aroon - indicator indicating days since a 25-day high/low, weighted between 0 and 100
    @param dData: Dictionary of data to use
    @param bDown: If false, calculates aroonUp (high), else aroonDown (lows)
    @param lLookback: Days to lookback to calculate high/low from
    @param b_human: if true return dataframe to plot
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
                if i - lfPeaks[j][1] > lLookback:
                    lfPeaks.pop(j)
                    continue
                    
                j += 1    
            
            #print lfPeaks
            
            tsRet[i] = ((lLookback - (i - lfPeaks[0][1])) / float(lLookback)) * 100.0
            
            ''' perturb value '''
            random.seed(i)
            tsRet[i] += random.uniform( -0.0001, 0.0001 )

    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet


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
            if i < lLookback - 1:
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
                 
                

    if b_human:
        for sym in dData['close']:
            x=1000/dData['close'][sym][0]
            dData['close'][sym]=dData['close'][sym]*x
        return dData['close']
    return dfRet

def featBeta( dData, lLookback=14, sMarket='$SPX', b_human=False ):
    '''
    @summary: Calculate beta relative to a given stock/index.
    @param dData: Dictionary of data to use
    @param sStock: Stock to calculate beta relative to
    @param b_human: if true return dataframe to plot
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
            if i < lLookback - 1:
                tsRet[i] = float('nan')
                continue    
            
            naStock = tsHistReturns[ i - (lLookback - 1): i+1 ]
            naMarket = tsMarket[ i - (lLookback - 1): i+1 ]
            
            ''' Beta is the slope the line, with market returns on X, stock returns on Y '''
            try:
                fBeta, unused = np.polyfit( naMarket, naStock, 1)
                tsRet[i] = fBeta
            except:
                'Numpy Error featBeta'
                tsRet[i] = float('NaN')

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
                    pstdRet[i] = fAvg+fStd
                    nstdRet[i] = fAvg-fStd  
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
        for sStock in dfPrice.columns:   
            tsPrice = dfPrice[sStock]
            tsRet = dfRet[sStock]
               
            #''' Loop over time '''
            for i in range(len(tsPrice.index)):
                
                #''' NaN if not enough data to do lookback '''
                if i < lLookback - 1:
                    tsRet[i] = float('nan')
                    continue    
                
                fAvg = np.average( tsPrice[ i-(lLookback-1):i+1 ] )
                fStd = np.std( tsPrice[ i-(lLookback-1):i+1 ] )
                
                tsRet[i] = (tsPrice[i] - fAvg) / fStd
    
        return dfRet


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
       
    ''' Calculate returns '''
    naRets = dfPrice.values.copy()
    tsu.returnize1(naRets)
    dfHistReturns = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=naRets )

    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.zeros(dfPrice.shape) )
    
    ''' Loop through stocks '''
    for sStock in dfHistReturns.columns:   
        tsHistReturns = dfHistReturns[sStock]
        tsRelativeReturns = dfHistReturns[sRel]
        tsRet = dfRet[sStock]
        
        ''' Loop over time '''
        for i in range(len(tsHistReturns.index)):
            
            ''' NaN if not enough data to do lookback '''
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
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
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
