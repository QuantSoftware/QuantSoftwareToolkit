'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various feature functions

'''

''' 3rd Party Imports '''
import pandas as pand

def featMA( dfPrice, lLookback=30 ):
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
        
        lSum = 0
        
        ''' Loop over time '''
        for i in range(len(dfPrice[sStock].index)):
            
            if sStock == 'XOM':
                print dfPrice[sStock][i]
            
            if pand.notnull( dfPrice[sStock][i] ):
                lSum += dfPrice[sStock][i]
            
            if i < lLookback - 1:
                dfRet[sStock][i] = float('nan')
                continue
            
            ''' If we have the bare min, take the avg, else remove the last and take the avg '''
            if i == lLookback - 1:
                dfRet[sStock][i] = lSum / lLookback
            else:
                lSum -= dfPrice[sStock][i-lLookback]
                dfRet[sStock][i] = lSum / lLookback
            
    return dfRet




def featRSI( dfPrice ):
    '''
    @summary: Calculate moving average
    @param dfPrice: Price data for all the stocks
    @param lLookback: Number of days to look in the past
    @return: DataFrame array containing values
    '''
    
    ''' Feature DataFrame will be 1:1, we can use the price as a template '''
    dfPrice = dfPrice.copy(deep=True)
            
    return dfPrice


if __name__ == '__main__':
    pass