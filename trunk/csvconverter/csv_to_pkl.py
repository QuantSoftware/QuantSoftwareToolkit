'''
Created on Feb 25, 2011
@note: This assumes that all the CSV files will have exactly 7 columns. It ignores the first row in the csv files because it it the heading.
@author: sjoshi42
'''

import numpy as np
import pickle as pkl
import os
import dircache
import time
import sys

def clean_output_paths (listOfOutputPaths):

 for path in listOfOutputPaths:
    files_at_this_path = dircache.listdir(str(path))
    for _file in files_at_this_path:
         os.remove(path + _file) 
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
    listOfInputPaths.append("/hzr71/research/QSData/Processed/Norgate/raw/Delisted Securities/US Recent/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/AMEX/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/Delisted Securities/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/OTC/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/NASDAQ/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/NYSE/")
    listOfInputPaths.append ("/hzr71/research/QSData/Processed/Norgate/raw/US/NYSE Arca/")
    
    listOfOutputPaths= list()
#    listOfOutputPaths.append("C:\\test\\temp\\pkl1\\")
#    listOfOutputPaths.append("C:\\test\\temp\\pkl2\\")    
    
    
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/Delisted_US_Recent/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_AMEX/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_Delisted/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/OTC/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NASDAQ/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NYSE/")
    listOfOutputPaths.append("/hzr71/research/QSData/Processed/Norgate/Equities/US_NYSE Arca/")    
    
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