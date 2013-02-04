'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: An example to show how dataAccess works.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


def main():
    ''' Main Function'''
    # Creating an object of DataAccess Class
    c_dataobj = da.DataAccess('Yahoo')

    # Getting a list of symbols from Lists
    # Lists : S&P5002012, S&P5002008, Index
    ls_symbols = c_dataobj.get_symbols_from_list('sp5002012')
    print "Symbols from the list : ", ls_symbols

    # All symbols possible
    ls_all_syms = c_dataobj.get_all_symbols()
    print "All symbols : ", ls_all_syms

    ls_syms_toread = ['AAPL', 'GOOG']

    # List of TimeStamps to read
    ldt_timestamps = []
    ldt_timestamps.append(dt.datetime(2010, 10, 14, 16))
    ldt_timestamps.append(dt.datetime(2010, 10, 15, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 21, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 22, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 23, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 24, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 25, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 26, 16))
    ldt_timestamps.append(dt.datetime(2010, 11, 27, 10))
    ldt_timestamps.append(dt.datetime(2010, 11, 27, 16))
    ldt_timestamps.append(dt.datetime(2020, 11, 27, 16))
    ldt_timestamps.append(dt.datetime(2020, 11, 27, 18))

    # Reading the data
    # By default it'll read data from the default data provided,
    # But a path can be provided using either an environment variable or
    # as a prarameter.
    df_close = c_dataobj.get_data(ldt_timestamps, ls_syms_toread, "close")
    print df_close


if __name__ == '__main__':
    main()

# import sys
# import profile
# #sys.path.append(str(sys.path[0])+str("/../qstkutil/")) #So that it works without PYTHONPATH being set

# #for i in range (0, len(sys.path)):
# #    print sys.path[i]

# #from DataAccess import *
# import QSTK.qstkutil.DataAccess as DA
# import numpy as np
# import time
# import datetime as dt

# def main():
    
#     da = DA.DataAccess(DA.DataSource.YAHOO);
    
#     symbol_list = list()
#     #symbol_list.append("$SPXFDGR")
#     symbol_list.append ("AAPL")
#     symbol_list.append("DLMAF")
    
#     all_sym= da.get_all_symbols()
#     print str("All symbols: " + str (all_sym))
    
#     sublists= da.get_sublists()
    
#     print str ("All sublists: " + str (sublists))
    
#     sublist_sym= da.get_symbols_in_sublist(sublists[0])
    
#     print str ("Symbols in sublist " + str (sublists[0]) + ": " + str(sublist_sym))
    
#     #symbol_list=  list (set(symbol_list) & set (da.get_all_symbols())) #Intersecting with all symbols to get rid of symbols that do not exist
#     #ts_list = range (1267419600,1267419600 + (86400*10) ,86400)
    
#     ts_list = list()
    
#     ts_list.append(dt.datetime(1610, 11, 21, 16))
#     ts_list.append(dt.datetime(1610, 11, 21, 11))
    
#     ts_list.append(dt.datetime(2010, 10, 14, 16))
#     ts_list.append(dt.datetime(2010, 10, 15, 16))
    
#     ts_list.append(dt.datetime(2010, 11, 21, 16))
#     ts_list.append(dt.datetime(2010, 11, 22, 16))
#     ts_list.append(dt.datetime(2010, 11, 23, 16))
#     ts_list.append(dt.datetime(2010, 11, 24, 16))
#     ts_list.append(dt.datetime(2010, 11, 25, 16))
#     ts_list.append(dt.datetime(2010, 11, 26, 16))
#     ts_list.append(dt.datetime(2010, 11, 27, 10))
#     ts_list.append(dt.datetime(2010, 11, 27, 16))
    
    
#     ts_list.append(dt.datetime(2020, 11, 27, 16))
#     ts_list.append(dt.datetime(2020, 11, 27, 18))
    
#     data_matrix = da.get_data(ts_list, symbol_list, DA.DataItem.OPEN)
#     print str (data_matrix)
    
# #    list_of_symbols= da.get_all_symbols();    
# #    for symbol in list_of_symbols:
# #        print symbol
    
# #main ends 
 
        
# if __name__ == '__main__':
#     main()
