'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Feb 1, 2011
@author: Shreyas Joshi
@organization: Georgia Institute of Technology
@contact: shreyasj@gatech.edu
@summary: This is an implementation of the K nearest neighbor learning algorithm. The implementation is trivial in that the near neighbors are 
          calculated naively- without any smart tricks. Euclidean distance is used to calculate the distance between two points. The implementation
          also provides some coarse parallelism. If the par_query function is used then the query points are split up equally amongst threads and their
          near neighbors are calculated in parallel. If the number of threads to use is not specified then no of threads  = no of cores as returned by
          the cpu_count function. This may not be ideal.    
@status: complete. "mode" untested
'''

import numpy as np
import scipy as sc
import math
import sys
import time
from multiprocessing import Pool
from multiprocessing import cpu_count
data = np.zeros (0)#this is the global data
import scipy.stats

def par_query (allQueries, k, method='mean', noOfThreads=None):
    '''
    @summary: Finds the k- nearest nrighbors in parallel. Based on function "query"
    @param allQueries: is another 2D numpy array. Each row here is one query point. It has no 'y' values. These have to be calculated.
    @param k: no. of neighbors to consider
    @param method: method of combining the 'y' values of the nearest neighbors. Default is mean.
    @param noOfThreads: optional parameter that specifies how many threads to create. Default value: no. of threads = value returned by cpu_count
    @return: A numpy array with the predicted 'y' values for the query points. The ith element in the array is the 'y' value for the ith query point.
    '''
    
    #Here we basically start 'noOfThreads' threads. Each thread calculates the neighbors for (noOfQueryPoints / noOfThreads) query points.
    
    if (noOfThreads == None):
        noOfThreads = cpu_count()
        #if ends
    
    #print "No of threads: " + str (noOfThreads)
    pool = Pool (processes=noOfThreads)
    
    resultList = []
    query_per_thread = allQueries.shape[0] / noOfThreads
    
    #time_start = time.time();
    for thread_ctr in range (0, noOfThreads - 1):
        resultList.append(pool.apply_async(query, (allQueries[math.floor(query_per_thread * thread_ctr): (math.floor(query_per_thread * (thread_ctr + 1 ))),:], k,)))
        #NOTE: we may need a -1 in above. Possible bug
        #for ends
    #the "remaining" query points go to the last thread
    resultList.append (pool.apply_async(query , (allQueries[(math.floor(query_per_thread* (noOfThreads - 1))):, :] ,k ,)))    
    
    pool.close()
    pool.join()
    
    #time_finish = time.time()
    #print "Time taken (secs): " + str (time_finish - time_start)
    
    answer = resultList[0].get()
    
    for thread_ctr  in range (1, noOfThreads):
        answer = np.hstack((answer, resultList[thread_ctr].get()))
        #for ends

    #print "par_query done"
    return answer
    #par_query ends


def query(allQueries, k, method='mean'):
    '''
    @summary: A serial implementation of k-nearest neighbors.
    @param allQueries: is another 2D numpy array. Each row here is one query point. It has no 'y' values. These have to be calculated.
    @param k: no. of neighbors to consider
    @param method: method of combining the 'y' values of the nearest neighbors. Default is mean.
    @return: A numpy array with the predicted 'y' values for the query points. The ith element in the array is the 'y' value for the ith query point. If there is more than one mode then only the first mode is returned.
    '''
    
    limit = allQueries.shape [0]
    data_limit = data.shape[0]
    omitLastCol = data.shape [1] - 1; #It must have two columns at least. Possibly add a check for this?
    answer = np.zeros (limit) #initialize the answer array to all zeros
    temp1 = np.zeros ((data.shape[0], (data.shape[1] -1)))
    temp2= np.zeros (data.shape[0])
    
    if (allQueries.shape[1] != (data.shape[1] -1) ):
        print "ERROR: Data and query points are not of the same dimension"
        raise ValueError
        #if ends
    if (k < 1):
        print "ERROR: K should be >= 1"
        raise ValueError
        #if ends    
    if (k > data.shape[0]):
        print "ERROR: K is greater than the total number of data points."
        raise ValueError
        #if ends
    
    for ctr in range (0, limit): #for every query point...  
        #if (ctr % 10 == 0):
         #   print ctr
            #if ends
        
        #for i in range (0 , data_limit): #for every data point
        temp1[0:data_limit, :] = data [0:data_limit ,0:omitLastCol] - allQueries[ctr, :]
        #for loop done
        
        temp1 = temp1*temp1; #square each element in temp1
        for ctr2 in range (0, data_limit):
            temp2[ctr2] = math.sqrt(sum (temp1[ctr2,:]))
            #for ends
                  
        index = temp2.argsort () #This is actually overkill because we need to sort only the top 'k' terms- but this sorts all of them     
        #following loop for debugging only  
        #for j in range (0, k):
        #   print str(data [index[j], :])
            #for ends
        
        if (method == 'mean'):
            #Now we need to find the average of the k top most 'y' values
            answer[ctr] = sum (data[ index [0:k], -1]) / k  #0 to (k-1)th index will be k values. But for this we have to give [0:k] because it stops one short of the last index
            #if method == mean ends
        if (method == 'median'):
            answer [ctr] = np.median (data[index [0:k], -1])
            # if median ends
        if (method == 'mode'):
            answer [ctr] = sc.stats.mode (data[index[0:k],-1])[0][0]; #The first mode. If there is more than one mode then the only the first mode is returned
            #endif mode    
        #for ctr in range (0, limit) ends
    return answer
    #getAnswer ends


def addEvidence (newData):
    '''
    @summary: This is the funtion to be called to add data. This function can be called multiple times- to add data whenever you like.
    @note: Any dimensional data can be added the first time. After that- the data must have the same number of columns as the data that was added the first time.
    @param newData: A 2D numpy array. Each row is a data point and each column is a dimension. The last dimension corresponds to 'y' values.
    '''
    
    global data
    if (data.shape[0] == 0):
        data = newData
    else:
        try:
            data= np.vstack ((data, newData))
        except Exception as ex:
            print "Type of exception: "+ str(type (ex))
            print "args: " + str(ex.args)
            #except ends   
    #addEvidence ends


def main(args):
    '''
    @summary: This function is just for testing. Will not be used as such...
    '''
    
    #Below code just for testing
    a = np.loadtxt ("/nethome/sjoshi42/knn_naive/data/3_D_1000_diskQueryPoints.txt")
    b= np.loadtxt ("/nethome/sjoshi42/knn_naive/data/3_D_128000_diskDataPoints.txt")
    addEvidence(b)

    answer = par_query(a, 5 ,'mode')
    #answer = query(a, 5, 'mean')
    
    for i in range (0, answer.shape[0]):
        print answer[i]
    #end for    
    
    
    print "The answer is: "

if __name__ == '__main__':
    main (sys.argv)
