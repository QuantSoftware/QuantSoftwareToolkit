'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Contains utility functions to interact with feature functions in features.py
'''

''' Python imports '''
import math

''' 3rd Party Imports '''
import numpy as np

''' Our Imports '''
import qstklearn.kdtknn as kdt


def applyFeatures( dfPrice, lfcFeatures, ldArgs ):
    '''
    @summary: Calculates the feature values using a list of feature functions and arguments.
    @param dfPrice: Data frame containing the price information for all of the stocks.
    @param lfcFeatures: List of feature functions, most likely coming from features.py
    @param ldArgs: List of dictionaries containing arguments, passed as **kwargs 
    @return: Numpy array containing values
    '''
    
    ldfRet = []
    
    for i, fcFeature in enumerate(lfcFeatures):
        ldfRet.append( fcFeature( dfPrice, **ldArgs[i] ) )
        
    return ldfRet


def stackSyms( ldfFeatures, bDelNan=True ):
    '''
    @summary: Remove symbols from the dataframes, effectively stacking all stocks on top of each other.
    @param ldfFeatures: List of data frames of features.
    @param bDelNan: Optional, default is true: delete all rows with a NaN in it
    @return: Numpy array containing all features as columns and all 
    '''
    
    naRet = None
    ''' Stack stocks vertically '''
    for sStock in ldfFeatures[0].columns:
        
        naStkData = None
        ''' Loop through all features, stacking columns horizontally '''
        for dfFeat in ldfFeatures:
            if naStkData == None:
                naStkData = np.array( dfFeat[sStock].values.reshape(-1,1) )
            else:
                naStkData = np.hstack( (naStkData, dfFeat[sStock].values.reshape(-1,1)) )
   
        ''' Remove nan rows possibly'''
        if True == bDelNan:
            llValidRows = []
            for i, lRow in enumerate(naStkData):
                if not math.isnan( np.sum(lRow) ):
                    llValidRows.append(i)
            naStkData = naStkData[llValidRows,:]
            
    
        ''' Now stack each block of stock data vertically '''
        if naRet == None:
            naRet = naStkData
        else:
            naRet = np.vstack( (naRet, naStkData) )

    return naRet


def normFeatures( naFeatures, fMin, fMax, bAbsolute, bIgnoreLast=True ):
    '''
    @summary: Normalizes the featurespace.
    @param naFeatures:  Numpy array of features,  
    @param fMin: Data frame containing the price information for all of the stocks.
    @param fMax: List of feature functions, most likely coming from features.py
    @param bAbsolute: If true, min value will be scaled to fMin, max to fMax, if false,
                      +-1 standard deviations will be scaled to fit between fMin and fMax, i.e. ~69% of the values
    @param bIgnoreLast: If true, last column is ignored (assumed to be classification)
    @return: None, data is modified in place
    '''
    
    fNewRange = fMax - fMin
    
    lUseCols = naFeatures.shape[1]
    if bIgnoreLast:
        lUseCols -= 1
    
    ''' Loop through all features '''
    for i in range(lUseCols):
        
        ''' If absolutely scaled use exact min and max '''
        if bAbsolute:
            fFeatMin = np.min( naFeatures[:,i] )
            fFeatMax = np.max( naFeatures[:,i] )
        else:
            ''' Otherwise use mean +-1 std deviations for min/max (~94% of data) '''
            fMean = np.average( naFeatures[:,i] )
            fStd = np.std( naFeatures[:,i] ) 
            fFeatMin = fMean - fStd
            fFeatMax = fMean + fStd
            
        ''' Calculate multiplier and shift variable so that new data fits in specified range '''
        fRange = fFeatMax - fFeatMin
        fMult = fNewRange / fRange
        fShift = fMin - (fFeatMin * fMult)
        
        ''' scale and shift '''
        naFeatures[:,i] *= fMult
        naFeatures[:,i] += fShift


def createKnnLearner( naFeatures, lKnn=30 ):
    '''
    @summary: Creates a quick KNN learner 
    @param naFeatures:  Numpy array of features,  
    @param fMin: Data frame containing the price information for all of the stocks.
    @param fMax: List of feature functions, most likely coming from features.py
    @param bAbsolute: If true, min value will be scaled to fMin, max to fMax, if false,
                      +-1 standard deviations will be scaled to fit between fMin and fMax, i.e. ~69% of the values
    @param bIgnoreLast: If true, last column is ignored (assumed to be classification)
    @return: None, data is modified in place
    '''    
    cLearner = kdt.kdtknn( k=lKnn, method='mean' )

    cLearner.addEvidence( naFeatures )

    return cLearner



if __name__ == '__main__':
    pass