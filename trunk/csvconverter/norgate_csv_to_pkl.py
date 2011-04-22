'''
Created on Feb 25, 2011

@note: This assumes that all the CSV files will have exactly 7 columns. It ignores the first row in the csv files because it it the heading.
        All the data is converted from csv to pkl
@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
@summary: This is used to convert CSV files from norgate to pkl files- which are used when the simulator runs.
'''

import numpy as np
import pickle as pkl
import os
import dircache
import time
import sys

def clean_output_paths (listOfOutputPaths):
 '''
 @summary: Removes any previous files in the output path.
 '''

 for path in listOfOutputPaths:
    files_at_this_path = dircache.listdir(str(path))
    for _file in files_at_this_path:
        if (os.path.isfile(path + _file)):
            os.remove(path + _file)
            #if ends 
    #for ends
 #oter for ends   
    
#clean_output_paths  ends

def main ():
    
    print "Starting..."+ str(time.strftime("%H:%M:%S"))
    
    
    fileExtensionToRemove = ".csv"
    
    listOfInputPaths= list()

# For Javelin    
#    listOfInputPaths.append("C:\\Trading data text\\Stocks\\Delisted Securities\\US Recent\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\AMEX\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\Delisted Securities\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\OTC\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\NASDAQ\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\NYSE\\")
#    listOfInputPaths.append ("C:\\Trading data text\\Stocks\\US\\NYSE Arca\\")
    
#For Gekko
    #listOfInputPaths.append("/hzr71/research/QSData/Processed/Norgate/raw/Delisted Securities/US Recent/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/AMEX/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/Delisted Securities/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/NASDAQ/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/NYSE/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/NYSE Arca/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/OTC/")
    listOfInputPaths.append ("/hzr71/research/QSData/Raw/Norgate/US/Indices/")
    
    
    
    listOfOutputPaths= list()
#    listOfOutputPaths.append("C:\\test\\temp\\pkl1\\")
#    listOfOutputPaths.append("C:\\test\\temp\\pkl2\\")    
    try:
        rootdir = os.environ['QSDATA']
    except KeyError:
        #rootdir = "/hzr71/research/QSData"
        print "Please be sure to set the value for QSDATA in config.sh or local.sh\n"
    
    #listOfOutputPaths.append(rootdir + "/Norgate/Delisted Securities/US Recent/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/AMEX/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/Delisted Securities/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/NASDAQ/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/NYSE/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/NYSE Arca/")
    listOfOutputPaths.append(rootdir + "/Processed/Norgate/US/OTC/")    
    listOfOutputPaths.append (rootdir + "/Processed/Norgate/US/Indices/")
    
    
    list_of_paths= dircache.listdir(str(listOfInputPaths[-1])) #Adding the paths in the indices folder
    
    for path in list_of_paths:
        if (os.path.isdir("/hzr71/research/QSData/Raw/Norgate/US/Indices/"+ path) == 1):
            listOfInputPaths.append("/hzr71/research/QSData/Raw/Norgate/US/Indices/"+ path+"/") #Add path to list of input paths
            listOfOutputPaths.append (rootdir + "/Processed/Norgate/US/Indices/" + os.path.split(path)[1]+"/") #Added paths to the list of output paths
        #for loop done    
#    print "Printing paths done"        
            
            
    
    
    #If the output paths don't exist, then create them...
    for path in listOfOutputPaths:
        if not (os.access(path, os.F_OK)):
            #Path does not exist, so create it
            os.mkdir(path)
    #done making all output paths!
    
    #In case there are already some files there- remove them. This will remove all the pkl fils from the previous run
    clean_output_paths (listOfOutputPaths)
    
    
    if (len(listOfInputPaths)!= len(listOfOutputPaths)):
        print "No. of input paths not equal to the number of output paths.. quitting"
        sys.exit("FAILURE")
        #if ends
    
    path_ctr = -1;
    use_cols = range (1, 7 + 1) # will now use cols 1 to 7
    for path in listOfInputPaths:
        path_ctr =  path_ctr + 1;
        stocks_at_this_path = dircache.listdir(str(path))
        #Next, throw away everything that is not a .csv And these are our stocks! Example: this should throw away the '$' folder in the NYSE folder
        filtered_names= filter (lambda x:(str(x).find(str(fileExtensionToRemove)) > -1), stocks_at_this_path)
        #Now, we remove the .csv to get the name of the stock
        filtered_names = map(lambda x:(x.partition(str(fileExtensionToRemove))[0]),filtered_names)
        stock_ctr = -1
        for stock in filtered_names:
            stock_ctr = stock_ctr + 1
            #print "Reading file: " + str (path + stock)
            #read in the stock date from the CSV file
            stock_data= np.loadtxt (path + stock+".csv", np.float, None, ",", None, 1, use_cols)
            
            stock_data_shape = stock_data.shape
            #print "stock_data_shape is: " + str(stock_data_shape)
        
            
#            for i in range (0, stock_data_shape[0]):
#                print stock_data [i,: ]
            
#            print "Reading: " + str(stock)
            f = open (listOfOutputPaths[path_ctr] + filtered_names[stock_ctr] + ".pkl", "wb" )
            pkl.dump (stock_data, f, -1)
            f.close()
        #for stock in stocks_at_this_path ends
    #for path in listOfInputPaths ends
    print "Finished..."+ str(time.strftime("%H:%M:%S"))
    
    #main ends
    
    
if __name__ == '__main__':
    main()