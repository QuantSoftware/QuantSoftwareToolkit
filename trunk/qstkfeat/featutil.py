'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Contains utility functions to interact with feature functions in features.py
'''


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
    


if __name__ == '__main__':
    pass