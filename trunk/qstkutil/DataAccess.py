'''
Created on Feb 26, 2011

@author: sjoshi42
@contact: shreyasj@gatech.edu
'''

import numpy as np
import pandas as pa
import os
import pickle as pkl
import time
import datetime as dt
import dircache


class DataAccess(object):
    '''
    @summary: This class is used to access all the symbol data. It readin in pickled numpy arrays converts them into appropriate pandas objects
    and returns that object. The {main} function currently demonstrates use.
    '''


    def __init__(self, source = "norgate"):
        '''
        Constructor
        @param source: Specifies the source of the data. Initializes paths based on source.
        @note: No data is actually read in the constructor. Only paths for the source are initialized
        '''
        self.folderList = list()

	try:
	    rootdir = os.environ['QSDATA']
	except KeyError:
	    rootdir = "/hzr71/research/QSData"
	    print "Please be sure to set the value for QSDATA in config.sh or local.sh\n"
        
        if ((source == "norgate") | (source == "Norgate"))
            #self.folderList.append("C:\\test\\temp\\pkl1\\")
            
            self.folderList.append("C:\\generated data files\\pkl\\Delisted_US_Recent\\")
            self.folderList.append("C:\\generated data files\\pkl\\US_AMEX\\")
            self.folderList.append("C:\\generated data files\\pkl\\US_Delisted\\")
            self.folderList.append("C:\\generated data files\\pkl\\OTC\\")
            self.folderList.append("C:\\generated data files\\pkl\\US_NASDAQ\\")
            self.folderList.append("C:\\generated data files\\pkl\\US_NYSE\\")
            self.folderList.append("C:\\generated data files\\pkl\\US_NYSE Arca\\")
            
            #if ends
        #__init__ ends
    def get_data (self, ts_list, symbol_list, data_item):
        '''
        @param ts_list: List of timestamps for which the data values are needed.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then 
        continues as usual. No errors are raised at the moment.
        '''
        #init data struct
        self.all_stocks_data = np.zeros ((len(ts_list), len(symbol_list)));
        self.all_stocks_data[:][:] = np.NAN
        list_index= [1,2,3,4,5,6]
        
        if  (data_item == 'open'):
            list_index.remove(1)
        elif (data_item == 'high'):
            list_index.remove (2)
        elif (data_item =='low'):
            list_index.remove(3)
        elif (data_item == 'close'):
            list_index.remove(4)
        elif(data_item == 'volume'):
            list_index.remove(5)
        elif (data_item == 'open'):
            list_index.remove(6)
        else:
            #incorrect value
            raise ValueError ("Incorrect value for data_item")
        #end elif

        
        #read in data for a stock
        symbol_ctr=-1
        for symbol in symbol_list:
            
            symbol_ctr = symbol_ctr + 1
            try:
                _file= open(self.getPathOfFile(symbol), "rb")
            except IOError:
                # If unable to read then break. The value will be nan
                break;
                
            temp_np = pkl.load (_file)
            _file.close()
            #now remove all the columns except the timestamps and one data column
            temp_np = np.delete(temp_np, list_index, 1)
            
            #now we have only timestamps and one data column
            
            #we convert the dates to time since epoch
            for i in range (0, temp_np.shape[0]):
                
                temp_np[i][0] = time.mktime(time.strptime(str(long(temp_np[i][0])),'%Y%m%d'))
                #print "date is: " + str(dt.datetime.fromtimestamp(temp_np[i][0]))
                #for ends
            
            ts_ctr = 0
            
            while ((dt.datetime.fromtimestamp(temp_np[ts_ctr][0])< ts_list[0]) and (ts_ctr < temp_np.shape[0])):
                ts_ctr=  ts_ctr+1
                
                #print "skipping initial data"
                #while ends
            
            for time_stamp in ts_list:
                #print "at time_stamp: " + str(time_stamp) + " and temp_np[ts_ctr][0]"  + str(temp_np[ts_ctr][0])
                if (time_stamp == dt.datetime.fromtimestamp(temp_np[ts_ctr][0])):
                    
                    #add to numpy array
                    #print "    adding to numpy array"
                    self.all_stocks_data[ts_list.index(time_stamp)][symbol_ctr] = temp_np [ts_ctr][1]
                    ts_ctr = ts_ctr +1
                    
                elif (dt.datetime.fromtimestamp(temp_np[ts_ctr][0]) > time_stamp):
                    #we don't have data for this timestamp. Add a NaN.
                    #print "    we don't have data for this ts. putting in a NaN"
                    self.all_stocks_data[ts_list.index(time_stamp)][symbol_ctr] = np.NAN
                else:
                    # (temp_np[ts_ctr][0] is < time_stamp)
                    while ((ts_ctr < temp_np.shape[0]) and (dt.datetime.fromtimestamp(temp_np[ts_ctr][0])< time_stamp)):
                        ts_ctr = ts_ctr+1
                        #while ends
                    
                    if  (ts_ctr >= temp_np.shape[0]):
                        print "breaking"
                        break
                        #break out of the for loop
                        #if ends
                    #else ends
                #inner for ends
            #outer for ends        
        data_frame = pa.DataFrame (self.all_stocks_data, ts_list, symbol_list)            
        return data_frame            
                        
        
        #get_data ends
        
    def getPathOfFile(self, symbol_name):
        '''
        @summary: Since a given pkl file can exist in any of the folders- we need to look for it in each one until we find it. Thats what this function does.
        @return: Complete path to the pkl file including the file name and extension
        '''
        for path1 in self.folderList:
            if (os.path.exists(str(path1)+str(symbol_name+".pkl"))):
                # Yay! We found it!
                return (str(str(path1)+str(symbol_name)+".pkl"))
                #if ends
#            else:
#                print str(path1)+str(stockName)+".h5" + " does not exist!"
            #for ends
        print "Did not find path to " + str (symbol_name)+". Looks like this file is missing"        
    
    def get_all_symbols (self):
        '''
        @summary: Returns a list of all the symbols located at any of the paths for this source. @see: {__init__}
        @attention: This will discard all files that are not of type pkl. ie. Only the files with an extension pkl will be reported.
        '''
    
        listOfStocks=list()
        #Path does not exist
        print "Reading in all stock names..."
        fileExtensionToRemove=".pkl"
        
        if (len(self.folderList) == 0):
            raise ValueError ("DataAccess source not set")   
    
        for path in self.folderList:
            stocksAtThisPath=list ()
            print str(path)
            stocksAtThisPath= dircache.listdir(str(path))
            #Next, throw away everything that is not a .h5 And these are our stocks!
            stocksAtThisPath = filter (lambda x:(str(x).find(str(fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .h5 to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(fileExtensionToRemove))[0]),stocksAtThisPath)
            
            listOfStocks.extend(stocksAtThisPath)
            #for stock in stocksAtThisPath:
                #listOfStocks.append(stock)
                
                
        return listOfStocks    
        #get_all_symbols ends
        
    #class DataAccess ends
 
def main():
    
    da = DataAccess('norgate');
    symbol_list = list()
    symbol_list.append ("AAPL")
    symbol_list.append("AMZN")
    symbol_list.append ("MSFT")
    #ts_list = range (1267419600,1267419600 + (86400*10) ,86400)
    ts_list = list()
    
    ts_list.append(dt.datetime(2010, 11, 21))
    ts_list.append(dt.datetime(2010, 11, 22))
    ts_list.append(dt.datetime(2010, 11, 23))
    ts_list.append(dt.datetime(2010, 11, 24))
    ts_list.append(dt.datetime(2010, 11, 25))
    ts_list.append(dt.datetime(2010, 11, 26))
    ts_list.append(dt.datetime(2010, 11, 26, 10))
    ts_list.append(dt.datetime(2010, 11, 27))
    
    
    data_frame= da.get_data(ts_list, symbol_list, "volume")
    print str (data_frame)
    
#    list_of_symbols= da.get_all_symbols();
#    
#    for symbol in list_of_symbols:
#        print symbol
    
#main ends 
 
        
if __name__ == '__main__':
    main()
