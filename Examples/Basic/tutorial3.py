'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main():
    ''' Main Function'''
    # Reading the portfolio
    na_portfolio = np.loadtxt('tutorial3portfolio.csv', dtype='S5,f4',
                        delimiter=',', comments="#", skiprows=1)
    print na_portfolio

    # Sorting the portfolio by symbol name
    na_portfolio = sorted(na_portfolio, key=lambda x: x[0])
    print na_portfolio

    # Create two list for symbol names and allocation
    ls_port_syms = []
    ls_port_alloc = []
    for port in na_portfolio:
        ls_port_syms.append(port[0])
        ls_port_alloc.append(port[0])

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    ls_all_syms = c_dataobj.get_all_symbols()
    # Bad symbols are symbols present in portfolio but not in all syms
    ls_bad_syms = list(set(ls_port_syms) - set(ls_all_syms))
    for s_sym in ls_bad_syms:
        i_index = ls_port_syms.index(s_sym)
        ls_port_syms.pop(i_index)
        ls_port_alloc.pop(i_index)

    # Reading the historical data.
    dt_end = dt.datetime(2011, 1, 1)
    dt_start = dt_end - dt.timedelta(days=1095)  # Three years
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_port_syms, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')

    # Numpy matrix of filled data values
    na_rets = df_rets.values
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    # Estimate portfolio returns
    na_portrets = np.sum(na_rets * ls_port_alloc, axis=1)
    na_port_total = np.cumprod(na_portrets + 1)
    na_component_total = np.cumprod(na_rets + 1, axis=0)

    # Plotting the results
    plt.clf()
    fig = plt.figure()
    fig.add_subplot(111)
    plt.plot(ldt_timestamps, na_component_total, alpha=0.4)
    plt.plot(ldt_timestamps, na_port_total)
    ls_names = ls_port_syms
    ls_names.append('Portfolio')
    plt.legend(ls_names)
    plt.ylabel('Cumulative Returns')
    plt.xlabel('Date')
    fig.autofmt_xdate(rotation=45)
    plt.savefig('tutorial3.pdf', format='pdf')

if __name__ == '__main__':
    main()

# plt.clf()
# fig = plt.figure()
# fig.add_subplot(111)
# plt.plot(timestamps,componenttot,alpha=0.4)
# plt.plot(timestamps,porttot)
# names = portsyms
# names.append('portfolio')
# plt.legend(names)
# plt.ylabel('Cumulative Returns')
# plt.xlabel('Date')
# fig.autofmt_xdate(rotation=45)
# savefig('tutorial3.pdf',format='pdf')

# #
# # Read the definition of the portfolio from a csv file
# #
# portfolio = np.loadtxt('tutorial3portfolio.csv',
#     dtype='S5,f4',
#     delimiter=',',
#         comments='#',
#     skiprows=1,
#     )
# print portfolio
# # Sort by symbol name
# portfolio = sorted(portfolio, key=lambda x: x[0])
# print portfolio

# #
# # Create two lists: portfolio names and allocations
# #
# portsyms = []
# portalloc = []
# for i in portfolio:
#     portsyms.append(i[0])
#     portalloc.append(i[1])

# #
# # Read in the symbols available and compare with our portfolio
# #
# dataobj = da.DataAccess('Yahoo')
# all_symbols = dataobj.get_all_symbols()
# intersectsyms = list(set(all_symbols) & set(portsyms)) # valid symbols
# badsyms = []
# if size(intersectsyms)<size(portsyms):
#     badsyms = list(set(portsyms) - set(intersectsyms))
#     print "warning: portfolio contains symbols that do not exist:" 
#     print badsyms
# for i in badsyms: # remove the bad symbols from our portfolio
#     index = portsyms.index(i)
#     portsyms.pop(index)
#     portalloc.pop(index)

# #
# # Read the historical data in from our data store
# #
# endday = dt.datetime(2011,1,1) 
# startday = endday - dt.timedelta(days=1095) #three years back
# timeofday=dt.timedelta(hours=16)
# print "start getNYSEdays"
# timestamps = du.getNYSEdays(startday,endday,timeofday)
# print "start read"
# close = dataobj.get_data(timestamps,portsyms,"close")
# print "end read"

# #
# # Copy, prep, and compute daily returns
# #
# rets = close.values.copy()
# tsu.fillforward(rets)
# tsu.returnize0(rets)

# #
# # Estimate portfolio total returns
# #
# portrets = sum(rets*portalloc,axis=1)
# porttot = cumprod(portrets+1)
# componenttot = cumprod(rets+1,axis=0) # compute returns for components

# #
# # Plot the result
# #
# plt.clf()
# fig = plt.figure()
# fig.add_subplot(111)
# plt.plot(timestamps,componenttot,alpha=0.4)
# plt.plot(timestamps,porttot)
# names = portsyms
# names.append('portfolio')
# plt.legend(names)
# plt.ylabel('Cumulative Returns')
# plt.xlabel('Date')
# fig.autofmt_xdate(rotation=45)
# savefig('tutorial3.pdf',format='pdf')
