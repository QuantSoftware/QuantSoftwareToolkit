'''

(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on June 1, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: Used to extract Compustat data from a csv dump and convert into individual pickle files
'''

import numpy as np
import datetime as dt
import pickle as pkl
import qstkutil.utils as utils
import qstkutil.DataAccess as da
import os
import dircache
import time
import csv
import sys


def _dumpFiles( dData, lSets, lsOutPaths ):
    '''
    @summary Helper function to store files on disk: files from dictionary dData, set of paths lSets
    @param dData: Dictionary of indexes to data label strings. 
    @param lSets: List of symbol sets, each corresponds to a directory, e.g. NYSE, NASDAQ.
    @param lsOutPaths: List of path strings, same indexes as lSets.
    '''
    lKeys = dData.keys()
     
    for key in lKeys:
        for i, symSet in enumerate( lSets ):
            if key in symSet:
                sFilename = lsOutPaths[i] + key + '.pkl'
                break
        
        fOut = open( sFilename, 'wb' )
        pkl.dump( dData[key], fOut, -1)
        fOut.close()
    
    
def _analyze():
    '''
    @summary Helper function to analyzes the csv data to determine which columns are float values, and generate the set of valid labels.
    '''
    try:
        rootdir = os.environ['QSDATA']
    except KeyError:
        print "Please be sure to set the value for QSDATA in config.sh or local.sh\n"    
        
    ''' Create lists of input and output paths '''
    fFile = ( rootdir + "/Raw/Compustat/Compustat.csv")
      
    spamReader = csv.reader(open(fFile, 'rb'), delimiter=',')
    
    ''' Take first row as the labels '''
    for row in spamReader:
        lsLabels = row
        break    
    
    used = [0] * len(lsLabels)
    badSet = set()
    
    ''' find non-float valued entities '''
    for i, row in enumerate(spamReader):
        for j, elem in enumerate(row):
            if used[j] == 1:
                continue
            
            if elem == '':
                elem = 0.0
            
            try: 
                float(elem)
            except:
                badSet.add( lsLabels[j] )
                used[j] = 1
        
        if( i % 10000 == 0 ):
            print (i / 1378625.0)*100, '%'   
    
    print 'Bad (non float) labels:'
    print badSet   
    
    for i,label in enumerate(lsLabels):
        if label in badSet:
            del lsLabels[i]
    
    print '\n\nGood (float) labels:'
    print lsLabels
    
    return  
    

def convert ():
    '''
    @summary: Converts a Compustat CSV file to pickle files of numpy arrays.
    '''
    
    print "Starting..."+ str(time.strftime("%H:%M:%S"))
    
    ''' Write every so often to save memory, 20k lines is usually < .5GB '''
    lSaveMem = 20000
    
    try:
        rootdir = os.environ['QSDATA']
    except KeyError:
        print "Please be sure to set the value for QSDATA in config.sh or local.sh\n"    
    
    ''' Create lists of input and output paths '''
    fFile = ( rootdir + "/Raw/Compustat/Compustat.csv")

    listOfOutputPaths= []
    listOfOutputPaths.append(rootdir + "/Processed/Compustat/US/AMEX/")
    listOfOutputPaths.append(rootdir + "/Processed/Compustat/US/NASDAQ/")
    listOfOutputPaths.append(rootdir + "/Processed/Compustat/US/NYSE/")    
    
    #If the output paths don't exist, then create them...
    for path in listOfOutputPaths:
        if not (os.access(path, os.F_OK)):
            #Path does not exist, so create it
            os.makedirs(path) #Makes paths recursively
    #done making all output paths!
    
    #In case there are already some files there- remove them. This will remove all the pkl fils from the previous run
    utils.clean_paths (listOfOutputPaths)
      
    spamReader = csv.reader(open(fFile, 'rb'), delimiter=',')
    ''' 1378625 rows typical '''    
    
    ''' Take first row as the labels '''
    for row in spamReader:
        lsLabels = row
        break
   
    ''' Generated from _Analyze() '''
    lsBadLabels = set(['LOC', 'ADD4', 'ADD3', 'ADD2', 'ADD1', 'ACCTCHGQ', 'WEBURL', 'IDBFLAG', 'popsrc', 'DATACQTR', 'conm', 'COSTAT', 'FINALQ', 'fdateq', 'FAX', 'RP', 'PRIROW', 'dldte', 'indfmt', 'SPCSRC', 'BUSDESC', 'ipodate', 'PHONE', 'CURCDQ', 'pdateq', 'DATAFQTR', 'PRICAN', 'EIN', 'datadate', 'tic', 'ADDZIP', 'CONML', 'consol', 'datafmt', 'cusip', 'BSPRQ', 'OGMQ', 'COMPSTQ', 'COUNTY', 'STATE', 'CURNCDQ', 'CITY', 'rdq', 'apdedateq', 'STALTQ', 'INCORP'])

    ''' get list of stocks in 3 US indexes '''
    Access = da.DataAccess( 'Norgate' )
    setNyse = set( Access.get_symbols_in_sublist("/US/NYSE") )
    setNasdaq = set( Access.get_symbols_in_sublist("/US/NASDAQ") )
    setAmex = set( Access.get_symbols_in_sublist("/US/AMEX") )
    
    ''' If stock appears in more than one index, remove to avoid ambiguity '''
    print 'Ignoring duplicate stocks:',
    dup1 =  setNyse.intersection( setNasdaq.union(setAmex))
    dup2 =  setNasdaq.intersection( setAmex )
    print dup1.union(dup2)

    setNyse   = setNyse - dup1.union(dup2)
    setAmex   = setAmex - dup1.union(dup2)
    setNasdaq = setNasdaq - dup1.union(dup2)
    
    ''' Note the two lists below must be in the same order '''
    lsOutPaths = []
    lsOutPaths.append(rootdir + "/Processed/Compustat/US/AMEX/")
    lsOutPaths.append(rootdir + "/Processed/Compustat/US/NASDAQ/")
    lsOutPaths.append(rootdir + "/Processed/Compustat/US/NYSE/")  
    
    lSets = [setAmex, setNasdaq, setNyse]  
    
    #If the output paths don't exist, then create them...
    for path in lsOutPaths:
        if not (os.access(path, os.F_OK)):
            #Path does not exist, so create it
            os.makedirs(path) #Makes paths recursively
    #done making all output paths!
    
    #In case there are already some files there- remove them. This will remove all the pkl fils from the previous run
    utils.clean_paths (lsOutPaths)
        
    lDateCol = 0
    llUseCols = []

    
    ''' We have first row (the labels), loop through saving good label indicies '''
    for j, sElem in enumerate(lsLabels):
        if( sElem not in lsBadLabels ):
            llUseCols.append(j)
        
        ''' Keep track of ticker column and date, specially handled later '''
        if( sElem == 'datadate' ):
            lDateCol = j 
        if( sElem == 'tic' ):
            lTicCol = j 
        
        
    ''' Dict of ticker->numpy array mapping '''
    dData = dict()
    print ''
    
    
    ''' Main loop, iterate over the rows in the csv file '''
    for j, row in enumerate(spamReader):
        lsLabels = row
        sTic = row[lTicCol]
        
        ''' Find out what index this belongs to '''
        lIndex = -1
        for i, symSet in enumerate( lSets ):
            if sTic in symSet:
                lIndex = i
                break
        if lIndex == -1:
            continue
        
        sFilename = lsOutPaths[lIndex] + sTic + '.pkl'
        
        ''' If the file exists (temporary memory saving measure), read it in and delete file from disk '''
        if( os.path.isfile(sFilename)):
            if dData.has_key(sTic):
               print 'File should not be both on disk and in dict'
               sys.exit("FAILURE")
            
            fIn = open( sFilename, 'rb' )
            dData[sTic] = pkl.load( fIn )
            fIn.close()
            os.remove( sFilename )
            
        fDate = float( dt.datetime.strptime( row[lDateCol], "%m/%d/%Y").strftime("%Y%m%d") )
        
        ''' convert blanks to nans '''
        for i in llUseCols:
            if row[i] == '':
                row[i] = 'nan'
        
        ''' Add row if data exists, if not, create new array '''
        if dData.has_key(sTic):       
            dData[sTic] = np.vstack( (dData[sTic], np.array([fDate] + [row[i] for i in llUseCols], dtype=np.float)) )
        else:
            dData[sTic]= np.array( [fDate] + [row[i] for i in llUseCols], dtype=np.float )
        
        if( (j+1) % 1000 == 0):
            fDone = (j / 1378625.0) * 100
            print '\rApprox %.2lf%%'%((j / 1378625.0) * 100),
            
        if( (j+1) % lSaveMem == 0):
            ''' Write all the pickle files we currently have '''
            
            print '\nWriting %i lines to pickle files to save memory\n'%(lSaveMem)
            _dumpFiles( dData, lSets, lsOutPaths)
            ''' Remember to delete! '''
            del dData
            dData = dict()
            
        # Done writing files
    # Done with main loop

    print ''
    print 'Writing final pickle files\n'       
    _dumpFiles( dData, lSets, lsOutPaths)
    del dData
    
    print "Finished..."+ str(time.strftime("%H:%M:%S"))
    
    return
    
if __name__ == '__main__':

    #_analyze()
    convert()
    
    
    
    