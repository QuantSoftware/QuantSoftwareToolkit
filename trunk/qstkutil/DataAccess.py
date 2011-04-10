'''
Created on Feb 26, 2011

@author: Shreyas Joshi
@contact: shreyasj@gatech.edu
'''

import numpy as np
import pandas as pa
import os
import pickle as pkl
import time
import datetime as dt
import dircache

class Exchange (object):
    AMEX=1
    NYSE=2
    NYSE_ARCA=3
    OTC=4
    DELISTED=5
    NASDAQ=6
    
class DataItem (object):
    OPEN="open"
    HIGH="high"
    LOW="low"
    CLOSE="close"
    VOL="volume"
    VOLUME="volume"
    ACTUAL_CLOSE="actual_close"
    
class DataSource(object):
    NORGATE="Norgate"
    NORGATElc="norgate"
    YAHOO="Yahoo"
    
    #class DataSource ends

class DataAccess(object):
    '''
    @summary: This class is used to access all the symbol data. It readin in pickled numpy arrays converts them into appropriate pandas objects
    and returns that object. The {main} function currently demonstrates use.
    @note: The earliest time for which this works is platform dependent because the python date functionality is platform dependent.
    '''
    def __init__(self, sourcein = DataSource.NORGATE):
        '''
        @param sourcestr: Specifies the source of the data. Initializes paths based on source.
        @note: No data is actually read in the constructor. Only paths for the source are initialized
        '''
        
        self.folderList = list()
        self.folderSubList = list()
        
        try:
            self.rootdir = os.environ['QSDATA']
        except KeyError:
            #self.rootdir = "/hzr71/research/QSData"
            raise KeyError("Please be sure to set the value for QSDATA in config.sh or local.sh")
        
        if (sourcein == DataSource.NORGATE)|(sourcein == DataSource.NORGATElc) :

            self.source = DataSource.NORGATE
            self.midPath = "/Processed/Norgate"
            
            self.fileExtensionToRemove=".pkl"
            #
            #setting up path variables (old Shreyas), consider to remove
            #
            #self.NORGATE_AMEX_PATH= self.rootdir + "/Processed/Norgate/US/AMEX/"
            #self.NORGATE_DELISTED_PATH= self.rootdir + "/Processed/Norgate/US/Delisted Securities/"
            #self.NORGATE_NASDAQ_PATH= self.rootdir + "/Processed/Norgate/US/NASDAQ/"
            #self.NORGATE_NYSE_PATH= self.rootdir + "/Processed/Norgate/US/NYSE/"
            #self.NORGATE_NYSE_ARCA_PATH= self.rootdir + "/Processed/Norgate/US/NYSE Arca/"
            #self.NORGATE_OTC_PATH= self.rootdir + "/Processed/Norgate/US/OTC/"            
            #self.NORGATE_DELISTED_PATH = self.rootdir + "/Processed/Norgate/US/Delisted Securities/")

            self.folderSubList.append("/US/AMEX/")
            self.folderSubList.append("/US/NASDAQ/")
            self.folderSubList.append("/US/NYSE/")
            self.folderSubList.append("/US/NYSE Arca/")
            self.folderSubList.append("/US/OTC/")
            self.folderSubList.append("/US/Delisted Securities/")

            for i in self.folderSubList:
                self.folderList.append(self.rootdir+self.midPath+i)

            #self.folderList.append(self.NORGATE_AMEX_PATH)
            #self.folderList.append(self.NORGATE_DELISTED_PATH )
            #self.folderList.append(self.NORGATE_NASDAQ_PATH)
            #self.folderList.append(self.NORGATE_NYSE_PATH)
            #self.folderList.append(self.NORGATE_NYSE_ARCA_PATH)
            #self.folderList.append(self.NORGATE_OTC_PATH)
            
            #if ends
            
            #Raise error for incorrect source
            
        #__init__ ends


    def get_data (self, ts_list, symbol_list, data_item):
        '''
        @param ts_list: List of timestamps for which the data values are needed. Timestamps must be sorted.
        @param symbol_list: The list of symbols for which the data values are needed
        @param data_item: The data_item needed. Like open, close, volume etc.
        @note: If a symbol is not found then a message is printed. All the values in the column for that stock will be NaN. Execution then 
        continues as usual. No errors are raised at the moment.
        '''
        
        #init data struct
        self.all_stocks_data = np.zeros ((len(ts_list), len(symbol_list)));
        self.all_stocks_data[:][:] = np.NAN
        list_index= [1,2,3,4,5,6]
        
        if  (data_item == DataItem.OPEN):
            list_index.remove(1)
        elif (data_item == DataItem.HIGH):
            list_index.remove (2)
        elif (data_item ==DataItem.LOW):
            list_index.remove(3)
        elif (data_item == DataItem.CLOSE):
            list_index.remove(4)
        elif(data_item == DataItem.VOL):
            list_index.remove(5)
        elif (data_item == DataItem.ACTUAL_CLOSE):
            list_index.remove(6)
        else:
            #incorrect value
            raise ValueError ("Incorrect value for data_item")
        #end elif

        
        #read in data for a stock
        symbol_ctr=-1
        for symbol in symbol_list:
            
            symbol_ctr = symbol_ctr + 1
            #print self.getPathOfFile(symbol)
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
            symbol_ts_list = list() #This list will have all the timestamps for this symbol

            #convert the dates to time since epoch
            for i in range (0, temp_np.shape[0]):
                time_delta= dt.timedelta(seconds= 57600)
                #The earliest time it can generate a time for is platform dependent
                symbol_ts_list.append((dt.datetime.strptime(str(long(temp_np[i][0])),'%Y%m%d')) + time_delta) # To make the time 1600 hrs on the day previous to this midnight
                
                #print "date is: " + str(dt.datetime.fromtimestamp(temp_np[i][0]))
                #for ends
            
            ts_ctr = 0
            
            #Skip data from file which is before the first timestamp in ts_list
            while (ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr] < ts_list[0]):
                ts_ctr=  ts_ctr+1
                
                #print "skipping initial data"
                #while ends
            
            for time_stamp in ts_list:
                
                if (symbol_ts_list[-1] < time_stamp):
                    #The timestamp is after the last timestamp for which we have data. So we give up. Note that we don't have to fill in NaNs because that is 
                    #the default value.
                    break;
                else:
                    while ((ts_ctr < temp_np.shape[0]) and (symbol_ts_list[ts_ctr]< time_stamp)):
                        ts_ctr = ts_ctr+1
                        #while ends
                    #else ends
                                        
                #print "at time_stamp: " + str(time_stamp) + " and symbol_ts"  + str(symbol_ts_list[ts_ctr])
                
                if (time_stamp == symbol_ts_list[ts_ctr]):
                    #Data is present for this timestamp. So add to numpy array.
                    #print "    adding to numpy array"
                    self.all_stocks_data[ts_list.index(time_stamp)][symbol_ctr] = temp_np [ts_ctr][1]
                    ts_ctr = ts_ctr +1
                    
                    
#We do not need the following code because the values are NaN by default                    
#                if (symbol_ts_list[ts_ctr] > time_stamp):
#                    #we don't have data for this timestamp. Add a NaN.
#                    #print "    we don't have data for this ts. putting in a NaN"
#                    self.all_stocks_data[ts_list.index(time_stamp)][symbol_ctr] = np.NAN
                
                #inner for ends
            #outer for ends        
        data_matrix = pa.DataMatrix (self.all_stocks_data, ts_list, symbol_list)            
        return data_matrix            
                        
        
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
        
        if (len(self.folderList) == 0):
            raise ValueError ("DataAccess source not set")   
    
        for path in self.folderList:
            stocksAtThisPath=list ()
            #print str(path)
            stocksAtThisPath= dircache.listdir(str(path))
            #Next, throw away everything that is not a .pkl And these are our stocks!
            stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .pkl to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)
            
            listOfStocks.extend(stocksAtThisPath)
            #for stock in stocksAtThisPath:
                #listOfStocks.append(stock)
        return listOfStocks    
        #get_all_symbols ends

    def get_all_symbols_on_exchange (self, exchange):
        '''
        @summary: Returns all the symbols belonging to that exchange. Exchange is figured out by the path of the file.
        @param exchange: Specifies what exchange you want. Valid values: nyse, delisted, nasdaq, arca, amex, otc
        @return: A list of symbols belonging to that exchange 
        '''

        if (exchange == Exchange.NYSE):
            stocksAtThisPath= dircache.listdir(self.NORGATE_NYSE_PATH)
        elif (exchange == Exchange.DELISTED):
            stocksAtThisPath= dircache.listdir(self.NORGATE_DELISTED_PATH)
        elif (exchange == Exchange.NASDAQ):
            stocksAtThisPath= dircache.listdir(self.NORGATE_NASDAQ_PATH)
        elif (exchange == Exchange.NYSE_ARCA):
            stocksAtThisPath = dircache.listdir(self.NORGATE_NYSE_ARCA_PATH)
        elif (exchange == Exchange.AMEX):
            stocksAtThisPath= dircache.listdir(self.NORGATE_AMEX_PATH)
        elif (exchange == Exchange.OTC):
            stocksAtThisPath= dircache.listdir(self.NORGATE_OTC_PATH)
        else:
            raise ValueError ("Incorrect value for exchange")
        
        #Next, throw away everything that is not a .pkl And these are our stocks!
        stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
        #Now, we remove the .pkl to get the name of the stock
        stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)
        
        return stocksAtThisPath
        #get_all_symbols_on_exchange ends
        
    def get_symbols_in_sublist (self, subdir):
        '''
        @summary: Returns all the symbols belonging to that subdir of the data store.
        @param subdir: Specifies which subdir you want.
        @return: A list of symbols belonging to that subdir 
        '''

        pathtolook = self.rootdir+self.midPath+subdir
        stocksAtThisPath= dircache.listdir(pathtolook)
        
        print pathtolook
        print stocksAtThisPath
        
        #Next, throw away everything that is not a .pkl And these are our stocks!
        try:
            stocksAtThisPath = filter (lambda x:(str(x).find(str(self.fileExtensionToRemove)) > -1), stocksAtThisPath)
            #Now, we remove the .pkl to get the name of the stock
            stocksAtThisPath = map(lambda x:(x.partition(str(self.fileExtensionToRemove))[0]),stocksAtThisPath)
        except:
            print "error: no path to " + subdir
            stocksAtThisPath = list()
        
        return stocksAtThisPath
        #get_all_symbols_on_exchange ends
        
    def get_sublists (self):
        '''
        @summary: Returns a list of all the sublists for a data store.
        @return: A list of the valid sublists for the data store.
        '''

        return self.folderSubList
        #get_sublists

    def get_info (self):
        '''
        @summary: Returns and prints a string that describes the datastore.
        @return: A string.
        '''

        if (self.source == DataSource.NORGATE):
            retstr = "Norgate:\n"
            retstr = retstr + "Daily price and volume data from Norgate (premiumdata.net)\n"
            retstr = retstr + "that is valid at the time of NYSE close each trading day.\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid data items include: \n"
            retstr = retstr + "\topen, high, low, close, volume, actual_close\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        elif (self.source == DataSource.YAHOO):
            retstr = "Yahoo:\n"
            retstr = retstr + "To be completed by Shreyas\n"
            retstr = retstr + "Valid data items include: \n"
            retstr = retstr + "\topen, high, low, close, volume, actual_close\n"
            retstr = retstr + "\n"
            retstr = retstr + "Valid subdirs include: \n"
            for i in self.folderSubList:
                retstr = retstr + "\t" + i + "\n"

        else:
            retstr = "DataAccess internal error\n"

        print retstr

        return retstr
        #get_sublists
        
        
    #class DataAccess ends
