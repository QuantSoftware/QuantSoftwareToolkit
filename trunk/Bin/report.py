'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on 1/1/2011

@author: Drew Bratcher
@contact: dbratcher@gatech.edu
@summary:  Generates a html file containing a report based 
           off a timeseries of funds from a pickle file.
'''

from os import path
from os import sys
from pylab import *
from qstkutil import DataAccess as da
from qstkutil import dateutil as du
from qstkutil import tsutil as tsu
from qstkutil import fundutil as fu
import converter

from pandas import *
import matplotlib.pyplot as plt
import cPickle
import datetime as dt

BENCHMARK_CLOSE = 0

def print_header(html_file, name):
    """
    @summary prints header of report html file
    """
    html_file.write("<HTML>\n")
    html_file.write("<HEAD>\n")
    html_file.write("<TITLE>QSTK Generated Report:" + name + "</TITLE>\n")
    html_file.write("</HEAD>\n\n")
    html_file.write("<BODY>\n\n")

def print_footer(html_file):
    """
    @summary prints footer of report html file
    """
    html_file.write("</BODY>\n\n")
    html_file.write("</HTML>")

def print_stats(fund_ts, benchmark, name, outstream = sys.stdout):
    """
    @summary prints stats of a provided fund and benchmark
    @param fund_ts: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param name: name to associate with the fund in the report
    @param outstream: stream to print stats to, defaults to stdout
    """
    start_date = fund_ts.index[0].strftime("%m/%d/%Y")
    end_date = fund_ts.index[-1].strftime("%m/%d/%Y")
    outstream.write("Performance Summary for "\
	 + str(path.basename(name)) + " Backtest (Long Only)\n")
    outstream.write("For the dates " + str(start_date) + " to "\
                                       + str(end_date) + "\n\n")
    outstream.write("Yearly Performance Metrics \n")
    years = du.getYears(fund_ts)
    outstream.write("\n\t\t\t\t")
    for year in years:
        outstream.write("\t\t" + str(year))
    outstream.write("\n")
    outstream.write("Fund Annualized Return:\t\t")
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year ==year):
                year_vals.append(fund_ts[date])
        day_rets = tsu.daily1(year_vals)
        ret = tsu.get_ror_annual(day_rets[1:-1])
        outstream.write("\t\t% + 6.2f%%" % (ret*100))

    outstream.write("\n" + str(benchmark[0]) + " Annualized Return:\t\t")
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(fund_ts.index[0], fund_ts.index[-1], timeofday)
    dataobj = da.DataAccess('Norgate')
    global BENCHMARK_CLOSE
    BENCHMARK_CLOSE = dataobj.get_data(timestamps, benchmark, "close", \
                                                     verbose = False)
    for year in years:
        year_vals = []
        for date in BENCHMARK_CLOSE.index:
            if(date.year ==year):
                year_vals.append(BENCHMARK_CLOSE.xs(date))
        day_rets = tsu.daily1(year_vals)
        ret = tsu.get_ror_annual(day_rets[1:-1])
        outstream.write("\t\t% + 6.2f%%" % (ret*100))

    outstream.write("\n\nFund Winning Days:\t\t")                
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts[date])
        ret = fu.get_winning_days(year_vals)
        outstream.write("\t\t% + 6.2f%%" % ret)

    outstream.write("\n" + str(benchmark[0]) + \
                       " Winning Days:\t\t")                
    for year in years:
        year_vals = []
        for date in BENCHMARK_CLOSE.index:
            if(date.year==year):
                year_vals.append(BENCHMARK_CLOSE.xs(date))
        ret = fu.get_winning_days(year_vals)
        outstream.write("\t\t% + 6.2f%%" % ret)

    outstream.write("\n\nFund Max Draw Down:\t\t")
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts[date])
        ret = fu.get_max_draw_down(year_vals)
        outstream.write("\t\t% + 6.2f%%" % (ret*100))

    outstream.write("\n" + str(benchmark[0]) + " Max Draw Down:\t\t")
    for year in years:
        year_vals = []
        for date in BENCHMARK_CLOSE.index:
            if(date.year==year):
                year_vals.append(BENCHMARK_CLOSE.xs(date))
        ret = fu.get_max_draw_down(year_vals)
        outstream.write("\t\t% + 6.2f%%" % (ret*100))

    outstream.write("\n\nFund Daily Sharpe Ratio(for year):")
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts[date])
        ret = fu.get_sharpe_ratio(year_vals)
        outstream.write("\t\t% + 6.2f" % ret)

    outstream.write("\n" + str(benchmark[0]) + \
            " Daily Sharpe Ratio(for year):")       
    for year in years:
        year_vals = []
        for date in BENCHMARK_CLOSE.index:
            if(date.year==year):
                year_vals.append(BENCHMARK_CLOSE.xs(date))
        ret = fu.get_sharpe_ratio(year_vals)
        outstream.write("\t\t% + 6.2f" % ret)

    outstream.write("\n\nFund Daily Sortino Ratio(for year):")
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts[date])
        ret = fu.get_sortino_ratio(year_vals)
        outstream.write("\t\t% + 6.2f" % ret)

    outstream.write("\n" + str(benchmark[0]) + \
                " Daily Sortino Ratio(for year):")         
    for year in years:
        year_vals = []
        for date in BENCHMARK_CLOSE.index:
            if(date.year==year):
                year_vals.append(BENCHMARK_CLOSE.xs(date))
        ret = fu.get_sortino_ratio(year_vals)
        outstream.write("\t\t% + 6.2f" % ret)

    
    outstream.write("\n\nMonthly Returns %\n\t")
    month_names = du.getMonthNames()
    for name in month_names:
        outstream.write("\t  " + str(name))
    outstream.write("\n")
    years = du.getYears(fund_ts)
    i = 0
    mrets = tsu.monthly(fund_ts)
    for year in years:
        outstream.write(str(year) + "\t")
        months = du.getMonths(fund_ts, year)
        if(i==0):
            if(len(months)<12):
                for k in range(0, 12-len(months)):
                    outstream.write("\t")
        for month in months:
            outstream.write("\t% + 6.2f" % (mrets[i]*100))
            i += 1
        outstream.write("\n")

def generate_report(funds_list, graph_names, out_file):
    """
    @summary generates a report given a list of fund time series
    """
    html_file  =  open("report.html","w")
    print_header(html_file, out_file)
    html_file.write("<IMG SRC = \'./funds.png\' width = 400/>\n")
    html_file.write("<BR/>\n\n")
    i = 0
    plt.clf()
    #load spx for time frame
    symbol = ["$SPX"]
    start_date = 0
    end_date = 0
    for fund in funds_list:
        if(type(fund)!= type(list())):
            if(start_date == 0 or start_date>fund.index[0]):
                start_date = fund.index[0]    
            if(end_date == 0 or end_date<fund.index[-1]):
                end_date = fund.index[-1]    
            mult = 10000/fund.values[0]
            plt.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_names[i]))
        else:    
            if(start_date == 0 or start_date>fund[0].index[0]):
                start_date = fund[0].index[0]    
            if(end_date == 0 or end_date<fund[0].index[-1]):
                end_date = fund[0].index[-1]    
            mult = 10000/fund[0].values[0]
            plt.plot(fund[0].index, fund[0].values * mult, label = \
                                      path.basename(graph_names[i]))    
        i += 1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = da.DataAccess('Norgate')
    global BENCHMARK_CLOSE
    BENCHMARK_CLOSE = dataobj.get_data(timestamps, symbol, "close", \
                                            verbose = False)
    mult = 10000/BENCHMARK_CLOSE.values[0]
    i = 0
    for fund in funds_list:
        if(type(fund)!= type(list())):
            print_stats(fund, ["$SPX"], graph_names[i])
        else:    
            print_stats( fund[0], ["$SPX"], graph_names[i])
        i += 1
    plt.plot(BENCHMARK_CLOSE.index, BENCHMARK_CLOSE.values*mult, label = "SSPX")
    plt.ylabel('Fund Value')
    plt.xlabel('Date')
    plt.legend()
    plt.draw()
    savefig('funds.png', format = 'png')
    print_footer(html_file)

def generate_robust_report(fund_matrix, out_file):
    """
    @summary generates a report using robust backtesting
    @param fund_matrix: a pandas matrix of fund time series
    @param out_file: filename where to print report
    """
    html_file  =  open(out_file,"w")
    print_header(html_file, out_file)
    converter.fundsToPNG(fund_matrix,'funds.png')
    html_file.write("<H2>QSTK Generated Report:" + out_file + "</H2>\n")
    html_file.write("<IMG SRC = \'./funds.png\'/>\n")
    html_file.write("<IMG SRC = \'./analysis.png\'/>\n")
    html_file.write("<BR/>\n\n")
    print_stats(fund_matrix, "robust funds", html_file)
    print_footer(html_file)

if __name__  ==  '__main__':
    # Usage
    #
    # Normal:
    # python report.py 'out.pkl' ['out2.pkl' ...]
    #
    # Robust:
    # python report.py -r 'out.pkl'
    #
    
    ROBUST = 0

    if(sys.argv[1] == '-r'):
        ROBUST = 1

    FILENAME  =  "report.html"
    
    if(ROBUST == 1):
        ANINPUT = open(sys.argv[2],"r")
        FUNDS = cPickle.load(ANINPUT)
        generate_robust_report(FUNDS, FILENAME)
    else:
        FILES = sys.argv
        FILES.remove(FILES[0])
        FUNDS = []
        for AFILE in FILES:
            ANINPUT = open(AFILE,"r")
            FUND = cPickle.load(ANINPUT)
            FUNDS.append(FUND)
        generate_report(FUNDS, FILES, FILENAME)


