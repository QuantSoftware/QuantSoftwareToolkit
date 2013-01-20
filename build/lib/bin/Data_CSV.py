#File to read the data from mysql and push into CSV.

# Python imports
import datetime as dt
import csv
import copy
import os
import pickle

# 3rd party imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# QSTK imports
from QSTK.qstkutil import qsdateutil as du
import QSTK.qstkutil.DataEvolved as de

def get_data(ls_symbols, ls_keys):
    '''
    @summary: Gets a data chunk for backtesting
    @param dt_start: Start time
    @param dt_end: End time
    @param ls_symbols: symbols to use
    @note: More data will be pulled from before and after the limits to ensure
           valid data on the start/enddates which requires lookback/forward
    @return: data dictionry
    '''
    print "Getting Data from MySQL"
    # Modify dates to ensure enough data for all features
    dt_start = dt.datetime(2005,1,1)
    dt_end = dt.datetime(2012, 8, 31)
    ldt_timestamps = du.getNYSEdays( dt_start, dt_end, dt.timedelta(hours=16) )
    
    c_da = de.DataAccess('mysql')

    ldf_data = c_da.get_data(ldt_timestamps, ls_symbols, ls_keys)

    d_data = dict(zip(ls_keys, ldf_data))

    return d_data

def read_symbols(s_symbols_file):

    ls_symbols=[]
    file = open(s_symbols_file, 'r')
    for f in file.readlines():
        j = f[:-1]
        ls_symbols.append(j)
    file.close()
    
    return ls_symbols   


def csv_sym(sym, d_data, ls_keys, s_directory):

    bool_first_iter = True

    for key in ls_keys:
        if bool_first_iter == True:
            df_sym = d_data[key].reindex(columns = [sym])
            df_sym = df_sym.rename(columns = {sym : key})
            bool_first_iter = False
        else: 
            df_temp = d_data[key].reindex(columns = [sym])
            df_temp = df_temp.rename(columns = {sym : key})
            df_sym = df_sym.join(df_temp, how= 'outer')

    symfilename = sym.split('-')[0]
    sym_file = open(s_directory + symfilename + '.csv', 'w')
    sym_file.write("Date,Open,High,Low,Close,Volume,Adj Close \n")

    ldt_timestamps = list(df_sym.index)
    ldt_timestamps.reverse()
    
    for date in ldt_timestamps:
        date_to_csv = '{:%Y-%m-%d}'.format(date)
        string_to_csv = date_to_csv
        for key in ls_keys:
            string_to_csv = string_to_csv + ',' + str(df_sym[key][date])
        string_to_csv = string_to_csv + '\n'
        sym_file.write(string_to_csv)


def main(s_directory, s_symbols_file):

    #ls_symbols = read_symbols(s_symbols_file)
    ls_symbols = ['ACS-201002','BDK-201003','BJS-201004','BSC-201108','CCT-201111','EQ-200907','JAVA-201002','NCC-200901','NOVL-201104','PBG-201003','PTV-201011','ROH-200904','SGP-200911','SII-201008','WB-200901','WYE-200910','XTO-201006']
    ls_keys = ['actual_open', 'actual_high', 'actual_low', 'actual_close', 'volume', 'close']
    d_data = get_data(ls_symbols, ls_keys)
    # print d_data
    print "Creating CSV files now"

    for sym in ls_symbols:
        print sym
        csv_sym(sym,d_data, ls_keys, s_directory)

    print "Created all CSV files"


if __name__ == '__main__' :
    s_directory = 'MLTData/'
    s_directory = os.environ['QSDATA'] + '/Yahoo/' 
    s_symbols_file1 = 'MLTData/sp5002012.txt'
    s_symbols_file2 = 'MLTData/index.txt'
    s_symbols_file3 = 'MLTData/sp5002008.txt'
    main(s_directory, s_symbols_file3)