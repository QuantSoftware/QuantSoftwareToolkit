'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various classification functions

'''

''' 3rd Party Imports '''
import pandas as pand
import numpy as np

def classFutRet( dfPrice, lLookforward=21, sRel=None ):
    '''
    @summary: Calculate classification, uses future returns 
    @param dfPrice: Price data for all the stocks
    @param lLookforward: Number of days to look in the future
    @param sRel: Stock symbol that this should be relative to, ususally SPY.
    @return: DataFrame containing values
    '''
    
    ''' Class DataFrame will be 1:1, we can use the price as a template, need to copy values '''
    dfRet = pand.DataFrame( index=dfPrice.index, columns=dfPrice.columns, data=np.copy(dfPrice.values) ) 
    
    ''' If we want market relative, calculate those values now '''
    if not sRel == None:
        lLen = len(dfPrice[sRel].index)
        ''' Loop over time '''
        for i in range(lLen):
            
            if i + lLookforward >= lLen:
                dfRet[sRel][i] = float('nan')
                continue
            
            dfRet[sRel][i] = (dfRet[sRel][i+lLookforward] - dfRet[sRel][i]) / dfRet[sRel][i]
    
    ''' Loop through stocks '''
    for sStock in dfPrice.columns:
        
        ''' We have already done this stock '''
        if sStock == sRel:
            continue
        
        lLen = len(dfPrice[sStock].index)
        ''' Loop over time '''
        for i in range(lLen):
            
            if i + lLookforward >= lLen:
                dfRet[sStock][i] = float('nan')
                continue
            
            dfRet[sStock][i] = (dfRet[sStock][i+lLookforward] - dfRet[sStock][i]) / dfRet[sStock][i]
            
            ''' Make market relative '''
            if not sRel == None:
                dfRet[sStock][i] -= dfRet[sRel][i]
            
    return dfRet
        

if __name__ == '__main__':
    pass
