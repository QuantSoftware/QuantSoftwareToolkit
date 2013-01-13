'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Feb 20, 2011
@author: John Cornwell
@organization: Georgia Institute of Technology
@contact: JohnWCornwellV@gmail.com
@summary: This is an implementation of the 1-KNN algorithm for ranking features quickly.
          It uses the knn implementation.
@status: oneKNN functions correctly, optimized to use n^2/2 algorithm.
'''

import matplotlib.pyplot as plt
from pylab import gca

import itertools
import string
import numpy as np
import math
import knn

from time import clock


'''
@summary: Query function for 1KNN, return value is a double between 0 and 1.

@param naData: A 2D numpy array. Each row is a data point with the final column containing the classification.
'''
def oneKnn( naData ):
    
    
    if naData.ndim != 2:
        raise Exception( "Data should have two dimensions" )
    
    lLen = naData.shape[0]
    ''' # of dimensions, subtract one for classification '''
    lDim = naData.shape[1] - 1
    
    ''' Start best distances as very large '''
    ldDistances = [1E300] * lLen
    llIndexes = [-1] * lLen
        
    dDistance = 0.0;

    ''' Loop through finding closest neighbors '''
    for i in range( lLen ):
        for j in range( i+1, lLen ):
             
            dDistance = 0.0
            for k in range( 0, lDim ):
                dDistance += (naData[i][k] - naData[j][k])**2
            dDistance = math.sqrt( dDistance )
            
            ''' Two distances to check, for i's best, and j's best '''
            if dDistance < ldDistances[i]:
                ldDistances[i] = dDistance
                llIndexes[i] = j
                
            if dDistance < ldDistances[j]:
                ldDistances[j] = dDistance
                llIndexes[j] = i
                
    lCount = 0
    ''' Now count # of matching pairs '''
    for i in range( lLen ):
        if naData[i][-1] == naData[ llIndexes[i] ][-1]:
            lCount = lCount + 1

    return float(lCount) / lLen
            

''' Test function to plot  results '''
def _plotResults( naDist1, naDist2, lfOneKnn, lf5Knn ):
    plt.clf()
    
    plt.subplot(311)
    plt.scatter( naDist1[:,0], naDist1[:,1] )

    plt.scatter( naDist2[:,0], naDist2[:,1], color='r' )
    

    #plt.ylabel( 'Feature 2' )
    #plt.xlabel( 'Feature 1' )
    #gca().annotate( '', xy=( .8, 0 ), xytext=( -.3 , 0 ), arrowprops=dict(facecolor='red', shrink=0.05) )    
    gca().annotate( '', xy=( .7, 0 ), xytext=( 1.5 , 0 ), arrowprops=dict(facecolor='black', shrink=0.05) )    
    plt.title( 'Data Distribution' )
    
    plt.subplot(312)
    
    plt.plot( range( len(lfOneKnn) ), lfOneKnn )

    plt.ylabel( '1-KNN Value' )    
    #plt.xlabel( 'Distribution Merge' )

    plt.title( '1-KNN Performance' )

    plt.subplot(313)
    
    plt.plot( range( len(lf5Knn) ), lf5Knn )

    plt.ylabel( '% Correct Classification' )    
    #plt.xlabel( 'Distribution Merge' )

    plt.title( '5-KNN Performance' )
    
    plt.subplots_adjust()
    
    plt.show() 
    
''' Function to plot 2 distributions '''
def _plotDist( naDist1, naDist2, i ):
    plt.clf()

    plt.scatter( naDist1[:,0], naDist1[:,1] )

    plt.scatter( naDist2[:,0], naDist2[:,1], color='r' )
    

    plt.ylabel( 'Feature 2' )
    plt.xlabel( 'Feature 1' )

    plt.title( 'Iteration ' + str(i) )
    
    plt.show()
    
''' Function to test KNN performance '''
def _knnResult( naData ):
    

    ''' Split up data into training/testing '''
    lSplit = naData.shape[0] * .7
    naTrain = naData[:lSplit, :]
    naTest  = naData[lSplit:, :]
    
    knn.addEvidence( naTrain.astype(float), 1 );
    
    ''' Query with last column omitted and 5 nearest neighbors '''
    naResults = knn.query( naTest[:,:-1], 5, 'mode') 
    
    ''' Count returns which are correct '''
    lCount = 0
    for i, dVal in enumerate(naResults):
        if dVal == naTest[i,-1]:
            lCount = lCount + 1
            
    dResult = float(lCount) / naResults.size

    return dResult

''' Tests performance of 1-KNN '''
def _test1():
        
    ''' Generate three random samples to show the value of 1-KNN compared to 5KNN learner performance '''
    
    for i in range(3):
        
        ''' Select one of three distributions '''
        if i == 0:
            naTest1 = np.random.normal( loc=[0,0],scale=.25,size=[500,2] )
            naTest1 = np.hstack( (naTest1, np.zeros(500).reshape(-1,1) ) )
            
            naTest2 = np.random.normal( loc=[1.5,0],scale=.25,size=[500,2] )
            naTest2 = np.hstack( (naTest2, np.ones(500).reshape(-1,1) ) )
        elif i == 1:
            naTest1 = np.random.normal( loc=[0,0],scale=.25,size=[500,2] )
            naTest1 = np.hstack( (naTest1, np.zeros(500).reshape(-1,1) ) )
            
            naTest2 = np.random.normal( loc=[1.5,0],scale=.1,size=[500,2] )
            naTest2 = np.hstack( (naTest2, np.ones(500).reshape(-1,1) ) )
        else:
            naTest1 = np.random.normal( loc=[0,0],scale=.25,size=[500,2] )
            naTest1 = np.hstack( (naTest1, np.zeros(500).reshape(-1,1) ) )
            
            naTest2 = np.random.normal( loc=[1.5,0],scale=.25,size=[250,2] )
            naTest2 = np.hstack( (naTest2, np.ones(250).reshape(-1,1) ) )
        
        naOrig = np.vstack( (naTest1, naTest2) )
        naBoth = np.vstack( (naTest1, naTest2) )
        
        ''' Keep track of runtimes '''
        t = clock()
        cOneRuntime = t-t;
        cKnnRuntime = t-t;
                                  
        lfResults = []
        lfKnnResults = []
        for i in range( 15 ):
            #_plotDist( naTest1, naBoth[100:,:], i )
            
            t = clock()
            lfResults.append( oneKnn( naBoth ) )
            cOneRuntime = cOneRuntime + (clock() - t)
            
            t = clock()
            lfKnnResults.append( _knnResult( np.random.permutation(naBoth) ) )
            cKnnRuntime = cKnnRuntime + (clock() - t)
            
            naBoth[500:,0] = naBoth[500:,0] - .1

        print 'Runtime OneKnn:', cOneRuntime
        print 'Runtime 5-KNN:', cKnnRuntime   
        _plotResults( naTest1, naTest2, lfResults, lfKnnResults )

''' Tests performance of 1-KNN '''
def _test2():
    ''' Generate three random samples to show the value of 1-KNN compared to 5KNN learner performance '''
    
    np.random.seed( 12345 )

    ''' Create 5 distributions for each of the 5 attributes '''
    dist1 = np.random.uniform( -1, 1, 1000 ).reshape( -1, 1 )
    dist2 = np.random.uniform( -1, 1, 1000 ).reshape( -1, 1 )   
    dist3 = np.random.uniform( -1, 1, 1000 ).reshape( -1, 1 )
    dist4 = np.random.uniform( -1, 1, 1000 ).reshape( -1, 1 )
    dist5 = np.random.uniform( -1, 1, 1000 ).reshape( -1, 1 )
    
    lDists = [ dist1, dist2, dist3, dist4, dist5 ]

    ''' All features used except for distribution 4 '''
    distY = np.sin( dist1 ) + np.sin( dist2 ) + np.sin( dist3 ) + np.sin( dist5 )
    distY = distY.reshape( -1, 1 )
    
    for i, fVal  in enumerate( distY ):
        if fVal >= 0:
            distY[i] = 1
        else:
            distY[i] = 0
    
    for i in range( 1, 6 ):
        
        lsNames = []
        lf1Vals = []
        lfVals = []   
             
        for perm in itertools.combinations( '12345', i ):
            
            ''' set test distribution to first element '''
            naTest = lDists[ int(perm[0]) - 1 ]
            sPerm = perm[0]
            
            ''' stack other distributions on '''
            for j in range( 1, len(perm) ):
                sPerm = sPerm + str(perm[j])
                naTest = np.hstack( (naTest, lDists[ int(perm[j]) - 1 ] ) )
            
            ''' finally stack y values '''
            naTest = np.hstack( (naTest, distY) )
            
            lf1Vals.append( oneKnn( naTest ) )
            lfVals.append( _knnResult( np.random.permutation(naTest) ) )
            lsNames.append( sPerm )

        ''' Plot results '''
        plt1 = plt.bar( np.arange(len(lf1Vals)), lf1Vals, .2, color='r' )
        plt2 = plt.bar( np.arange(len(lfVals)) + 0.2, lfVals, .2, color='b' )
        
        plt.legend( (plt1[0], plt2[0]), ('1-KNN', 'KNN, K=5') )
    
        plt.ylabel('1-KNN Value/KNN Classification')
        plt.xlabel('Feature Set')
        plt.title('Combinations of ' + str(i) + ' Features')

        plt.ylim( (0,1) )
        if len(lf1Vals) < 2:
            plt.xlim( (-1,1) )

        gca().xaxis.set_ticks( np.arange(len(lf1Vals)) + .2 )
        gca().xaxis.set_ticklabels( lsNames )
        
        plt.show()

          
    
if __name__ == '__main__':
    
    _test1()
    #_test2()
    
    
    
    
