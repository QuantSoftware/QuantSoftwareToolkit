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

    # Reading the csv file.
    na_data = np.loadtxt('example-data.csv', delimiter=',', skiprows=1)
    na_price = na_data[:, 3:]  # Default np.loadtxt datatype is float.
    na_dates = np.int_(na_data[:, 0:3])  # Dates should be int
    ls_symbols = ['$SPX', 'XOM', 'GOOG', 'GLD']

    # Printing the first 5 rows
    print "First 5 rows of Price Data:"
    print na_price[:5, :]
    print "First 5 rows of Dates:"
    print na_dates[:5, :]

    # Creating the timestamps from dates read
    ldt_timestamps = []
    for i in range(0, na_dates.shape[0]):
        ldt_timestamps.append(dt.date(na_dates[i, 0],
                        na_dates[i, 1], na_dates[i, 2]))

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, na_price)
    plt.legend(ls_symbols)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, na_normalized_price)
    plt.legend(ls_symbols)
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    plt.savefig('normalized.pdf', format='pdf')

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    tsu.returnize0(na_rets)

    # Plotting the plot of daily returns
    plt.clf()
    plt.plot(ldt_timestamps[0:50], na_rets[0:50, 0])  # $SPX 50 days
    plt.plot(ldt_timestamps[0:50], na_rets[0:50, 1])  # XOM 50 days
    plt.axhline(y=0, color='r')
    plt.legend(['$SPX', 'XOM'])
    plt.ylabel('Daily Returns')
    plt.xlabel('Date')
    plt.savefig('rets.pdf', format='pdf')

    # Plotting the scatter plot of daily returns between XOM VS $SPX
    plt.clf()
    plt.scatter(na_rets[:, 0], na_rets[:, 1], c='blue')
    plt.ylabel('XOM')
    plt.xlabel('$SPX')
    plt.savefig('scatterSPXvXOM.pdf', format='pdf')

    # Plotting the scatter plot of daily returns between $SPX VS GLD
    plt.clf()
    plt.scatter(na_rets[:, 0], na_rets[:, 3], c='blue')  # $SPX v GLD
    plt.ylabel('GLD')
    plt.xlabel('$SPX')
    plt.savefig('scatterSPXvGLD.pdf', format='pdf')

if __name__ == '__main__':
    main()

# #
# # read in and slice up the data
# #
# data = np.loadtxt('example-data.csv',delimiter=',',skiprows=1)
# pricedat = data[:,3:]
# datesdat = np.int_(data[:,0:3]) # date stuff should be integer
# pricesnames = ['$SPX','XOM','GOOG','GLD']

# print 'first 5 rows of price data:'
# print pricedat[:5,:]
# print
# print 'first 5 rows of dates:'
# print datesdat[:5,:]

# #
# # Convert columns of date info into date objects
# #
# dates = []
# for i in range(0,datesdat.shape[0]):
# 	dates.append(dt.date(datesdat[i,0],datesdat[i,1],datesdat[i,2]))

# #
# # Plot the closing prices
# #
# plt.clf()
# for i in range(0,size(pricedat[0,:])):
# 	plt.plot(dates,pricedat[:,i])
# plt.legend(pricesnames)
# plt.ylabel('Adjusted Close')
# plt.xlabel('Date')
# savefig('adjustedclose.pdf', format='pdf')

# #
# # Plot the normalized data
# #
# plt.clf()
# normdat = pricedat/pricedat[0,:]
# for i in range(0,size(normdat[0,:])):
# 	plt.plot(dates,normdat[:,i])
# plt.legend(pricesnames)
# plt.ylabel('Normalized Adjusted Close')
# plt.xlabel('Date')
# savefig("normalizedclose.pdf", format='pdf')

# #
# # Daily returns
# #
# plt.clf()
# dailyrets = concatenate(([(zeros(pricedat.shape[1]))],
# 	((pricedat[1:,:]/pricedat[0:-1,:]) - 1)),axis=0)
# plt.plot(dates[0:49],dailyrets[0:49,0]) # just plot first 50 days
# plt.plot(dates[0:49],dailyrets[0:49,1])
# plt.axhline(y=0,color='r')
# plt.legend(['$SPX','XOM'])
# plt.ylabel('Daily Returns')
# plt.xlabel('Date')
# savefig("dailyrets.pdf", format='pdf')

# #
# # scatter plot $SPX v XOM
# #
# plt.clf()
# plt.scatter(dailyrets[:,0],dailyrets[:,1],c='blue')
# plt.ylabel('XOM')
# plt.xlabel('$SPX')
# savefig("scatterSPXvXOM.pdf", format='pdf')

# #
# # scatter plot $SPX v GLD
# #
# plt.clf()
# plt.scatter(dailyrets[:,0],dailyrets[:,3],c='red')
# plt.ylabel('GLD')
# plt.xlabel('$SPX')
# savefig("scatterSPXvGLD.pdf", format='pdf')
