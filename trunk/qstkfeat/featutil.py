'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Contains utility functions to interact with feature functions in features.py
'''

''' Python imports '''
import math
import pickle
import datetime as dt
from dateutil.relativedelta import relativedelta

''' 3rd Party Imports '''
import numpy as np

''' Our Imports '''
import qstklearn.kdtknn as kdt
from qstkutil import DataAccess as da
from qstkutil import dateutil as du

from qstkfeat.features import *
from qstkfeat.classes import classFutRet


def applyFeatures( dfPrice, dfVolume, lfcFeatures, ldArgs, sLog=None ):
    '''
    @summary: Calculates the feature values using a list of feature functions and arguments.
    @param dfPrice: Data frame containing the price information for all of the stocks.
    @param lfcFeatures: List of feature functions, most likely coming from features.py
    @param ldArgs: List of dictionaries containing arguments, passed as **kwargs
    @param sLog: If not None, will be filename to log all of the features to 
    @return: list of dataframes containing values
    '''
    
    ldfRet = []
    
    for i, fcFeature in enumerate(lfcFeatures):
        ''' Hack for our one volume indicator '''
        if fcFeature.__name__ == 'featVolumeDelta':
            ldfRet.append( fcFeature( dfVolume, **ldArgs[i] ) )
        else:
            ldfRet.append( fcFeature( dfPrice, **ldArgs[i] ) )
        
    if not sLog == None:
        with open( sLog, 'wb' ) as fFile:
            pickle.dump( ldfRet, fFile, -1 )
        
    return ldfRet

def loadFeatures( sLog ):
    '''
    @summary: Loads cached features.
    @param sLog: Filename of features.
    @return: Numpy array containing values
    '''
    
    ldfRet = []
    
    if not sLog == None:
        with open( sLog, 'rb' ) as fFile:
            ldfRet = pickle.load( fFile )
        
    return ldfRet


def stackSyms( ldfFeatures, dtStart, dtEnd, bDelNan=True ):
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
            
            dfFeat = dfFeat.ix[dtStart:dtEnd]
            
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
    @return: list of (weights, shifts) to be used to normalize the query points
    '''
    
    fNewRange = fMax - fMin
    
    lUseCols = naFeatures.shape[1]
    if bIgnoreLast:
        lUseCols -= 1
    
    ltRet = []
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
        
        ''' scale and shift, save in return array '''
        naFeatures[:,i] *= fMult
        naFeatures[:,i] += fShift
        ltRet.append( (fMult, fShift) )
    
    return ltRet

def normQuery( naQueries, ltWeightShift ):
    '''
    @summary: Normalizes the queries using the given normalization parameters generated from training data.
    @param naQueries:  Numpy array of queries  
    @param ltWeightShift: List of weights and shift amounts to be applied to each query.
    @return: None, modifies naQueries
    '''
    
    assert naQueries.shape[1] == len(ltWeightShift)
    
    for i in range(naQueries.shape[1]):
        
        ''' scale and shift, save in return array '''
        naQueries[:,i] *= ltWeightShift[i][0]
        naQueries[:,i] += ltWeightShift[i][1]
        


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

def log500( sLog ):
    '''
    @summary: Loads cached features.
    @param sLog: Filename of features.
    @return: Nothing, logs features to desired location
    '''
    
    
    lsSym = ['A', 'AA', 'AAPL', 'ABC', 'ABT', 'ACE', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AET', 'AFL', 'AGN', 'AIG', 'AIV', 'AIZ', 'AKAM', 'AKS', 'ALL', 'ALTR', 'AMAT', 'AMD', 'AMGN', 'AMP', 'AMT', 'AMZN', 'AN', 'ANF', 'ANR', 'AON', 'APA', 'APC', 'APD', 'APH', 'APOL', 'ARG', 'ATI', 'AVB', 'AVP', 'AVY', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBBY', 'BBT', 'BBY', 'BCR', 'BDX', 'BEN', 'BF.B', 'BHI', 'BIG', 'BIIB', 'BK', 'BLK', 'BLL', 'BMC', 'BMS', 'BMY', 'BRCM', 'BRK.B', 'BSX', 'BTU', 'BXP', 'C', 'CA', 'CAG', 'CAH', 'CAM', 'CAT', 'CB', 'CBG', 'CBS', 'CCE', 'CCL', 'CEG', 'CELG', 'CERN', 'CF', 'CFN', 'CHK', 'CHRW', 'CI', 'CINF', 'CL', 'CLF', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMS', 'CNP', 'CNX', 'COF', 'COG', 'COH', 'COL', 'COP', 'COST', 'COV', 'CPB', 'CPWR', 'CRM', 'CSC', 'CSCO', 'CSX', 'CTAS', 'CTL', 'CTSH', 'CTXS', 'CVC', 'CVH', 'CVS', 'CVX', 'D', 'DD', 'DE', 'DELL', 'DF', 'DFS', 'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DNB', 'DNR', 'DO', 'DOV', 'DOW', 'DPS', 'DRI', 'DTE', 'DTV', 'DUK', 'DV', 'DVA', 'DVN', 'EBAY', 'ECL', 'ED', 'EFX', 'EIX', 'EL', 'EMC', 'EMN', 'EMR', 'EOG', 'EP', 'EQR', 'EQT', 'ERTS', 'ESRX', 'ETFC', 'ETN', 'ETR', 'EW', 'EXC', 'EXPD', 'EXPE', 'F', 'FAST', 'FCX', 'FDO', 'FDX', 'FE', 'FFIV', 'FHN', 'FII', 'FIS', 'FISV', 'FITB', 'FLIR', 'FLR', 'FLS', 'FMC', 'FO', 'FRX', 'FSLR', 'FTI', 'FTR', 'GAS', 'GCI', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'GME', 'GNW', 'GOOG', 'GPC', 'GPS', 'GR', 'GS', 'GT', 'GWW', 'HAL', 'HAR', 'HAS', 'HBAN', 'HCBK', 'HCN', 'HCP', 'HD', 'HES', 'HIG', 'HNZ', 'HOG', 'HON', 'HOT', 'HP', 'HPQ', 'HRB', 'HRL', 'HRS', 'HSP', 'HST', 'HSY', 'HUM', 'IBM', 'ICE', 'IFF', 'IGT', 'INTC', 'INTU', 'IP', 'IPG', 'IR', 'IRM', 'ISRG', 'ITT', 'ITW', 'IVZ', 'JBL', 'JCI', 'JCP', 'JDSU', 'JEC', 'JNJ', 'JNPR', 'JNS', 'JOYG', 'JPM', 'JWN', 'K', 'KEY', 'KFT', 'KIM', 'KLAC', 'KMB', 'KMX', 'KO', 'KR', 'KSS', 'L', 'LEG', 'LEN', 'LH', 'LIFE', 'LLL', 'LLTC', 'LLY', 'LM', 'LMT', 'LNC', 'LO', 'LOW', 'LSI', 'LTD', 'LUK', 'LUV', 'LXK', 'M', 'MA', 'MAR', 'MAS', 'MAT', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDT', 'MET', 'MHP', 'MHS', 'MJN', 'MKC', 'MMC', 'MMI', 'MMM', 'MO', 'MOLX', 'MON', 'MOS', 'MPC', 'MRK', 'MRO', 'MS', 'MSFT', 'MSI', 'MTB', 'MU', 'MUR', 'MWV', 'MWW', 'MYL', 'NBL', 'NBR', 'NDAQ', 'NE', 'NEE', 'NEM', 'NFLX', 'NFX', 'NI', 'NKE', 'NOC', 'NOV', 'NRG', 'NSC', 'NTAP', 'NTRS', 'NU', 'NUE', 'NVDA', 'NVLS', 'NWL', 'NWSA', 'NYX', 'OI', 'OKE', 'OMC', 'ORCL', 'ORLY', 'OXY', 'PAYX', 'PBCT', 'PBI', 'PCAR', 'PCG', 'PCL', 'PCLN', 'PCP', 'PCS', 'PDCO', 'PEG', 'PEP', 'PFE', 'PFG', 'PG', 'PGN', 'PGR', 'PH', 'PHM', 'PKI', 'PLD', 'PLL', 'PM', 'PNC', 'PNW', 'POM', 'PPG', 'PPL', 'PRU', 'PSA', 'PWR', 'PX', 'PXD', 'QCOM', 'QEP', 'R', 'RAI', 'RDC', 'RF', 'RHI', 'RHT', 'RL', 'ROK', 'ROP', 'ROST', 'RRC', 'RRD', 'RSG', 'RTN', 'S', 'SAI', 'SBUX', 'SCG', 'SCHW', 'SE', 'SEE', 'SHLD', 'SHW', 'SIAL', 'SJM', 'SLB', 'SLE', 'SLM', 'SNA', 'SNDK', 'SNI', 'SO', 'SPG', 'SPLS', 'SRCL', 'SRE', 'STI', 'STJ', 'STT', 'STZ', 'SUN', 'SVU', 'SWK', 'SWN', 'SWY', 'SYK', 'SYMC', 'SYY', 'T', 'TAP', 'TDC', 'TE', 'TEG', 'TEL', 'TER', 'TGT', 'THC', 'TIE', 'TIF', 'TJX', 'TLAB', 'TMK', 'TMO', 'TROW', 'TRV', 'TSN', 'TSO', 'TSS', 'TWC', 'TWX', 'TXN', 'TXT', 'TYC', 'UNH', 'UNM', 'UNP', 'UPS', 'URBN', 'USB', 'UTX', 'V', 'VAR', 'VFC', 'VIA.B', 'VLO', 'VMC', 'VNO', 'VRSN', 'VTR', 'VZ', 'WAG', 'WAT', 'WDC', 'WEC', 'WFC', 'WFM', 'WFR', 'WHR', 'WIN', 'WLP', 'WM', 'WMB', 'WMT', 'WPI', 'WPO', 'WU', 'WY', 'WYN', 'WYNN', 'X', 'XEL', 'XL', 'XLNX', 'XOM', 'XRAY', 'XRX', 'YHOO', 'YUM', 'ZION', 'ZMH']
    lsSym.append('SPY')
    lsSym.sort()
    
    
    ''' Max lookback is 6 months '''
    dtEnd = dt.datetime.now()
    dtEnd = dtEnd.replace(hour=16, minute=0, second=0, microsecond=0)
    dtStart = dtEnd - relativedelta(months=6)
    
    
    ''' Pull in current data '''
    norObj = da.DataAccess('Norgate')
    ''' Get 2 extra months for moving averages and future returns '''
    ldtTimestamps = du.getNYSEdays( dtStart - relativedelta(months=2), \
                                    dtEnd   + relativedelta(months=2), dt.timedelta(hours=16) )
    
    dfPrice = norObj.get_data( ldtTimestamps, lsSym, 'close' )
    dfVolume = norObj.get_data( ldtTimestamps, lsSym, 'volume' )

    ''' Imported functions from qstkfeat.features, NOTE: last function is classification '''
    lfcFeatures, ldArgs, lsNames = getFeatureFuncs()                
    
    ''' Generate a list of DataFrames, one for each feature, with the same index/column structure as price data '''
    applyFeatures( dfPrice, dfVolume, lfcFeatures, ldArgs, sLog=sLog )


def getFeatureFuncs():
    '''
    @summary: Gets feature functions supported by the website.
    @return: Tuple containing (list of functions, list of arguments, list of names)
    '''
    
    lfcFeatures = [ featMA, featMA, featRSI, featDrawDown, featRunUp, featVolumeDelta, classFutRet ]
    lsNames = ['Moving Average', 'Relative Moving Average', 'RSI', 'Draw Down', 'Run Up', 'Volume Delta', 'Future Returns']
      
    ''' Custom Arguments '''
    ldArgs = [ {'lLookback':30},\
               {'lLookback':30, 'bRel':True},\
               {},\
               {},\
               {},\
               {},\
               {'sRel':'SPY'}]   
    
    return lfcFeatures, ldArgs, lsNames
      


if __name__ == '__main__':
    pass