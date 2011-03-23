'''
Created on Jun 1, 2010

@author: Shreyas Joshi
@summary: An example to show how dataAccess works.
'''

import sys
import profile
#sys.path.append(str(sys.path[0])+str("/../qstkutil/")) #So that it works without PYTHONPATH being set

#for i in range (0, len(sys.path)):
#    print sys.path[i]

#from DataAccess import *
import qstkutil.DataAccess as DA
import numpy as np
import time
import datetime as dt

def main():
    
    da = DA.DataAccess('norgate');
    
    symbol_list = list()
    symbol_list.append ("AAPL")
    symbol_list.append("AMZN")
    symbol_list.append ("BOB")
    symbol_list.append("GLD")
    symbol_list.append("SPY")
    
    symbol_list=  list (set(symbol_list) & set (da.get_all_symbols())) #Intersecting with all symbols to get rid of symbols that do not exist
    #ts_list = range (1267419600,1267419600 + (86400*10) ,86400)
    ts_list = list()
    
    ts_list.append(dt.datetime(2010, 11, 21, 16))
    ts_list.append(dt.datetime(2010, 11, 22, 16))
    ts_list.append(dt.datetime(2010, 11, 23, 16))
    ts_list.append(dt.datetime(2010, 11, 24, 16))
    ts_list.append(dt.datetime(2010, 11, 25, 16))
    ts_list.append(dt.datetime(2010, 11, 26, 16))
    ts_list.append(dt.datetime(2010, 11, 26, 10))
    ts_list.append(dt.datetime(2010, 11, 27, 16))
    
    
    data_matrix = da.get_data(ts_list, symbol_list, "volume")
    print str (data_matrix)
    
#    list_of_symbols= da.get_all_symbols();    
#    for symbol in list_of_symbols:
#        print symbol
    
#main ends 
 
        
if __name__ == '__main__':
    main()


         

