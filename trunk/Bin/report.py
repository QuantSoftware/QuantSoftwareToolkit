'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on Jan 1, 2011

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains tutorial for backtester and report.

'''

from os import path, makedirs
from os import sys
from qstkutil import DataAccess as da
from qstkutil import qsdateutil as du
from qstkutil import tsutil as tsu
from qstkutil import fundutil as fu
import numpy as np
from math import log10
import converter
import locale
from pylab import savefig
from matplotlib import pyplot
from matplotlib import gridspec
import matplotlib.dates as mdates
import cPickle
import datetime as dt
import pandas
import numpy as np
from copy import deepcopy

def _dividend_rets_funds(df_funds, f_dividend_rets):

    df_funds_copy = deepcopy(df_funds)
    f_price = deepcopy(df_funds_copy[0])

    df_funds_copy.values[1:] = (df_funds_copy.values[1:]/df_funds_copy.values[0:-1])
    df_funds_copy.values[0] = 1

    df_funds_copy = df_funds_copy + f_dividend_rets

    na_funds_copy = np.cumprod(df_funds_copy.values)
    na_funds_copy = na_funds_copy*f_price

    df_funds = pandas.Series(na_funds_copy, index = df_funds_copy.index)

    return df_funds

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

def print_annual_return(fund_ts, years, ostream):
    """
    @summary prints annual return for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year ==year):
                year_vals.append([fund_ts.ix[date]])
        day_rets = tsu.daily1(year_vals)
        ret = tsu.get_ror_annual(day_rets[1:-1])
        ostream.write("   % + 6.2f%%" % (ret*100))

def print_winning_days(fund_ts, years, ostream):
    """
    @summary prints winning days for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_winning_days(year_vals)
        ostream.write("   % + 6.2f%%" % ret)

def print_max_draw_down(fund_ts, years, ostream):
    """
    @summary prints max draw down for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts.ix[date])
        ret = fu.get_max_draw_down(year_vals)
        ostream.write("   % + 6.2f%%" % (ret*100))

def print_daily_sharpe(fund_ts, years, ostream):
    """
    @summary prints sharpe ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sharpe_ratio(year_vals)
        ostream.write("   % + 6.2f " % ret)

def print_daily_sortino(fund_ts, years, ostream):
    """
    @summary prints sortino ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sortino_ratio(year_vals)
        ostream.write("   % + 6.2f " % ret)
        
def print_std_dev(fund_ts, ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    fund_ts=fund_ts.fillna(method='pad')
    ret=np.std(tsu.daily(fund_ts.values))*10000
    ostream.write("  % + 7.2f bps " % ret)

def print_industry_coer(fund_ts, ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    industries = [['$DJUSBM', 'Materials'],
    ['$DJUSNC', 'Goods'],
    ['$DJUSCY', 'Services'],
    ['$DJUSFN', 'Financials'],
    ['$DJUSHC', 'Health'],
    ['$DJUSIN', 'Industrial'],
    ['$DJUSEN', 'Oil & Gas'],
    ['$DJUSTC', 'Technology'],
    ['$DJUSTL', 'TeleComm'],
    ['$DJUSUT', 'Utilities']]
    for i in range(0, len(industries) ):
        if(i%2==0):
            ostream.write("\n")
        #load data
        norObj = da.DataAccess('Norgate')
        ldtTimestamps = du.getNYSEdays( fund_ts.index[0], fund_ts.index[-1], dt.timedelta(hours=16) )
        ldfData = norObj.get_data( ldtTimestamps, [industries[i][0]], ['close'] )
        #get corelation
        ldfData[0]=ldfData[0].fillna(method='pad')
        a=np.corrcoef(np.ravel(tsu.daily(ldfData[0][industries[i][0]])),np.ravel(tsu.daily(fund_ts.values)))
        b=np.ravel(tsu.daily(ldfData[0][industries[i][0]]))
        f=np.ravel(tsu.daily(fund_ts))
        fBeta, unused = np.polyfit(b,f,1)
        ostream.write("%10s(%s):%+6.2f,   %+6.2f   " % (industries[i][1], industries[i][0], a[0,1], fBeta))

def print_other_coer(fund_ts, ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    industries = [['$SPX', '    S&P Index'],
    ['$DJI', '    Dow Jones'],
    ['$DJUSEN', 'Oil & Gas'],
    ['$DJGSP', '     Metals']]
    for i in range(0, len(industries) ):
        if(i%2==0):
            ostream.write("\n")
        #load data
        norObj = da.DataAccess('Norgate')
        ldtTimestamps = du.getNYSEdays( fund_ts.index[0], fund_ts.index[-1], dt.timedelta(hours=16) )
        ldfData = norObj.get_data( ldtTimestamps, [industries[i][0]], ['close'] )
        #get corelation
        ldfData[0]=ldfData[0].fillna(method='pad')
        a=np.corrcoef(np.ravel(tsu.daily(ldfData[0][industries[i][0]])),np.ravel(tsu.daily(fund_ts.values)))
        b=np.ravel(tsu.daily(ldfData[0][industries[i][0]]))
        f=np.ravel(tsu.daily(fund_ts))
        fBeta, unused = np.polyfit(b,f,1)
        ostream.write("%10s(%s):%+6.2f,   %+6.2f   " % (industries[i][1], industries[i][0], a[0,1], fBeta))


def print_benchmark_coer(fund_ts, benchmark_close, sym,  ostream):
    """
    @summary prints standard deviation of returns for a fund
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    fund_ts=fund_ts.fillna(method='pad')
    benchmark_close=benchmark_close.fillna(method='pad')
    faCorr=np.corrcoef(np.ravel(tsu.daily(fund_ts.values)),np.ravel(tsu.daily(benchmark_close)));
    b=np.ravel(tsu.daily(benchmark_close))
    f=np.ravel(tsu.daily(fund_ts))
    fBeta, unused = np.polyfit(b,f, 1);
    ostream.write("\n        %6s Correlation:                  %+6.2f" % (sym, faCorr[0,1]))
    ostream.write("\n               %6s Beta:                  %+6.2f" % (sym, fBeta))

def print_monthly_returns(fund_ts, years, ostream):
    """
    @summary prints monthly returns for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    ostream.write("    ")
    month_names = du.getMonthNames()
    for name in month_names:
        ostream.write("    " + str(name))
    ostream.write("\n")
    i = 0
    mrets = tsu.monthly(fund_ts)
    for year in years:
        ostream.write(str(year))
        months = du.getMonths(fund_ts, year)
        for k in range(1, months[0]):
            ostream.write("       ")
        for month in months:
            ostream.write(" % + 6.2f" % (mrets[i]*100))
            i += 1
        ostream.write("\n")
        
        
def print_years(years, ostream):
    ostream.write("\n\n                               ")
    for year in years:
        ostream.write("      " + str(year))
    ostream.write("\n                                ")
    for year in years:
        ostream.write("    " + '------')
    ostream.write("\n")
    
def print_stats(fund_ts, benchmark, name, lf_dividend_rets=0.0, original="", s_original_name="", d_trading_params="", d_hedge_params="", s_comments="", directory = False, leverage = False, commissions = 0, slippage = 0, ostream = sys.stdout):
    """
    @summary prints stats of a provided fund and benchmark
    @param fund_ts: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param name: name to associate with the fund in the report
    @param directory: parameter to specify printing to a directory
    @param leverage: time series to plot with report
    @param commissions: value to print with report
    @param slippage: value to print with report
    @param ostream: stream to print stats to, defaults to stdout
    """
    
    #Set locale for currency conversions
    locale.setlocale(locale.LC_ALL, '')
    
    #make s_original_name symbol length independent for alignment
    s_original_name="%6s" % s_original_name
    
    fund_ts=fund_ts.fillna(method='pad')
    if directory != False :
        if not path.exists(directory):
            makedirs(directory)
        
        sfile = path.join(directory, "report-%s.html" % name )
        splot = "plot-%s.png" % name
        splot_dir =  path.join(directory, splot)
        ostream = open(sfile, "wb")
        ostream.write("<pre>")
        print "writing to ", sfile
        
        if type(original)==type("str"):
            if type(leverage)!=type(False):
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets, leverage=leverage)
            else:
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets) 
        else:
            if type(leverage)!=type(False):
                print_plot([original, fund_ts], benchmark, name, splot_dir, s_original_name, lf_dividend_rets, leverage=leverage)
            else:
                print_plot([original, fund_ts], benchmark, name, splot_dir, s_original_name, lf_dividend_rets) 
            
    start_date = fund_ts.index[0].strftime("%m/%d/%Y")
    end_date = fund_ts.index[-1].strftime("%m/%d/%Y")
    ostream.write("Performance Summary for "\
	 + str(path.basename(name)) + " Backtest\n")
    ostream.write("For the dates " + str(start_date) + " to "\
                                       + str(end_date) + "")
    
    #paramater section
    if d_trading_params!="":
        ostream.write("\n\nTrading Paramaters\n\n")
        for var in d_trading_params:
            ostream.write("%26s: %20s\n" % (var, d_trading_params[var]))
    if d_hedge_params!="":
        ostream.write("\nHedging Paramaters\n\n")
        if type(d_hedge_params['Weight of Hedge']) == type(float):
            d_hedge_params['Weight of Hedge'] = str(int(d_hedge_params['Weight of Hedge']*100)) + '%'
        for var in d_hedge_params:
            ostream.write("%26s: %20s\n" % (var, d_hedge_params[var]))
        
    #comment section
    if s_comments!="":
        ostream.write("\nComments\n\n%s" % s_comments)
    
    
    if directory != False :
        ostream.write("\n\n<img src="+splot+" width=600 />\n\n")
        
    mult = 1000000/fund_ts.values[0]
    
    
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(fund_ts.index[0], fund_ts.index[-1], timeofday)
    dataobj = da.DataAccess('Norgate')
    years = du.getYears(fund_ts)
    benchmark_close = dataobj.get_data(timestamps, benchmark, "close", \
                                                     verbose = False)
    for bench_sym in benchmark:
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(method='pad')
    
    if type(lf_dividend_rets) != type(0.0):
        for i,sym in enumerate(benchmark):
            benchmark_close[sym] = _dividend_rets_funds(benchmark_close[sym], lf_dividend_rets[i])
    
    ostream.write("Resulting Values in $ with an initial investment of $1,000,000.00\n")
    ostream.write("    Resulting   Fund Value:         %15s\n" % (locale.currency(int(round(fund_ts.values[-1]*mult)), grouping=True)))
    if type(original)!=type("str"):
        mult3 = 1000000 / original.values[0]
        ostream.write("    Resulting "+ s_original_name +" Value:         %15s\n" % (locale.currency(int(round(original.values[-1]*mult3)), grouping=True)))
        
    for bench_sym in benchmark:
        mult2=1000000/benchmark_close[bench_sym].values[0]
        ostream.write("    Resulting %6s Value:         %15s\n" % (bench_sym, locale.currency(int(round(benchmark_close[bench_sym].values[-1]*mult2)), grouping=True)))
    ostream.write("\n")    
        
    if len(years) > 1:
        ostream.write("         Fund Sharpe Ratio:                   %6s\n" % str(round(fu.get_sharpe_ratio(fund_ts.values)[0],3)))
        if type(original)!=type("str"):
            ostream.write("       "+ s_original_name +" Sharpe Ratio:                   %6s\n" % str(round(fu.get_sharpe_ratio(original.values)[0],3)))
        
        for bench_sym in benchmark:
            ostream.write("       %6s Sharpe Ratio:                   %6s\n" % (bench_sym,str(round(fu.get_sharpe_ratio(benchmark_close[bench_sym].values)[0],3))))
        ostream.write("\n")  
        
    ostream.write("Transaction Costs\n")
    ostream.write("          Total Comissions:         %15s, %6s%%\n" % (locale.currency(int(round(commissions)), grouping=True), \
                                                                                    str(round(float(round(commissions)/10000),2))))
    ostream.write("            Total Slippage:         %15s, %6s%%\n" % (locale.currency(int(round(slippage)), grouping=True), \
                                                                                    str(round(float(round(slippage)/10000),2))))
    ostream.write("\n")
    ostream.write("   Fund Std Dev of Returns:               ")
    
    print_std_dev(fund_ts, ostream)
    
    
    if type(original)!=type("str"):
        ostream.write("\n "+ s_original_name +" Std Dev of Returns:               ")    
        print_std_dev(original, ostream)
    
    for bench_sym in benchmark:
        ostream.write("\n %6s Std Dev of Returns:               " % bench_sym)  
        print_std_dev(benchmark_close[bench_sym], ostream)  
    ostream.write("\n")
        
    
    for bench_sym in benchmark:
        print_benchmark_coer(fund_ts, benchmark_close[bench_sym], str(bench_sym), ostream)
    ostream.write("\n")    

    ostream.write("\nYearly Performance Metrics")
    print_years(years, ostream)
    
    
    ostream.write("    Fund Annualized Return:      ")
    
    print_annual_return(fund_ts, years, ostream)
    
    
    
    if type(original)!=type("str"):
        ostream.write("\n  "+ s_original_name +" Annualized Return:      ")
        print_annual_return(original, years, ostream)
    
    for bench_sym in benchmark:
        ostream.write("\n  %6s Annualized Return:      " % bench_sym)
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(method='pad')
        print_annual_return(benchmark_close[bench_sym], years, ostream)
    
    print_years(years, ostream)
    
    ostream.write("         Fund Winning Days:      ")                
    print_winning_days(fund_ts, years, ostream)
    
    
    if type(original)!=type("str"):
        ostream.write("\n       "+ s_original_name +" Winning Days:      ")                
        print_winning_days(original, years, ostream)


    for bench_sym in benchmark:
        ostream.write("\n       %6s Winning Days:      " % bench_sym)                
        print_winning_days(benchmark_close[bench_sym], years, ostream)
    

    print_years(years, ostream)
    
    ostream.write("        Fund Max Draw Down:      ")
    print_max_draw_down(fund_ts, years, ostream)
    
    if type(original)!=type("str"):
        ostream.write("\n      "+ s_original_name +" Max Draw Down:      ")
        print_max_draw_down(original, years, ostream)


    for bench_sym in benchmark:
        ostream.write("\n      %6s Max Draw Down:      " % bench_sym)
        print_max_draw_down(benchmark_close[bench_sym], years, ostream)
    

    print_years(years, ostream)
    
    ostream.write("   Fund Daily Sharpe Ratio:      ")
    print_daily_sharpe(fund_ts, years, ostream)


    if type(original)!=type("str"):
        ostream.write("\n "+ s_original_name +" Daily Sharpe Ratio:      ")       
        print_daily_sharpe(original, years, ostream)

    for bench_sym in benchmark:
        ostream.write("\n%6s  Daily Sharpe Ratio:      " % bench_sym)       
        print_daily_sharpe(benchmark_close[bench_sym], years, ostream)
    

    print_years(years, ostream)
    
    ostream.write("  Fund Daily Sortino Ratio:      ")

    print_daily_sortino(fund_ts, years, ostream)

    if type(original)!=type("str"):
        ostream.write("\n"+ s_original_name +" Daily Sortino Ratio:      ")         
        print_daily_sortino(original, years, ostream)


    for bench_sym in benchmark:
        ostream.write("\n%6s Daily Sortino Ratio:      " % bench_sym)         

        print_daily_sortino(benchmark_close[bench_sym], years, ostream)
    
    
    ostream.write("\n\n\nCorrelation and Beta with DJ Industries for the Fund ")
    
    print_industry_coer(fund_ts,ostream)
    
    ostream.write("\n\nCorrelation and Beta with Other Indices for the Fund ")
    
    print_other_coer(fund_ts,ostream)
    
    ostream.write("\n\n\nMonthly Returns for the Fund %\n")
    
    print_monthly_returns(fund_ts, years, ostream) 
    if directory != False:
        ostream.write("</pre>")           

def print_plot(fund, benchmark, graph_name, filename, s_original_name="", lf_dividend_rets=0.0, leverage=False):
    """
    @summary prints a plot of a provided fund and benchmark
    @param fund: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param graph_name: name to associate with the fund in the report
    @param filename: file location to store plot1
    """
    pyplot.clf()
    if type(leverage)!=type(False): 
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
        pyplot.subplot(gs[0])
    start_date = 0
    end_date = 0
    if(type(fund)!= type(list())):
        if(start_date == 0 or start_date>fund.index[0]):
            start_date = fund.index[0]    
        if(end_date == 0 or end_date<fund.index[-1]):
            end_date = fund.index[-1]    
        mult = 1000000/fund.values[0]
        pyplot.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_name))
    else:    
        i=0
        for entity in fund:
            if(start_date == 0 or start_date>entity.index[0]):
                start_date = entity.index[0]    
            if(end_date == 0 or end_date<entity.index[-1]):
                end_date = entity.index[-1]    
            mult = 1000000/entity.values[0]
            if i == 0 and len(fund)!=1:
                pyplot.plot(entity.index, entity.values * mult, label = \
                                  s_original_name)
            else:
                pyplot.plot(entity.index, entity.values * mult, label = \
                                  path.basename(graph_name))
            i=i+1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = da.DataAccess('Norgate')
    benchmark_close = dataobj.get_data(timestamps, benchmark, "close", \
                                            verbose = False)
    benchmark_close = benchmark_close.fillna(method='pad')
    
    if type(lf_dividend_rets) != type(0.0):
        for i,sym in enumerate(benchmark):
            benchmark_close[sym] = _dividend_rets_funds(benchmark_close[sym], lf_dividend_rets[i])

    for sym in benchmark:
        mult = 1000000 / benchmark_close[sym].values[0]
        pyplot.plot(benchmark_close[sym].index, \
                benchmark_close[sym].values*mult, label = sym)
    pyplot.gcf().autofmt_xdate()
    pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
    pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    pyplot.xlabel('Date')
    pyplot.ylabel('Fund Value')
    pyplot.legend(loc = "best")
    if type(leverage)!=type(False):
        pyplot.subplot(gs[1])
        pyplot.plot(leverage.index, leverage.values, label="Leverage")
        pyplot.gcf().autofmt_xdate()
        pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
        pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
        labels=[]
        max_label=max(leverage.values)
        min_label=min(leverage.values)
        rounder= -1*(round(log10(max_label))-1)
        labels.append(round(min_label*0.9, int(rounder)))
        labels.append(round((max_label+min_label)/2, int(rounder)))
        labels.append(round(max_label*1.1, int(rounder)))
        pyplot.yticks(labels)
        pyplot.legend(loc = "best")
        pyplot.title(graph_name + " Leverage")
        pyplot.xlabel('Date')
        pyplot.legend()
    savefig(filename, format = 'png')
     
def generate_report(funds_list, graph_names, out_file):
    """
    @summary generates a report given a list of fund time series
    """
    html_file  =  open("report.html","w")
    print_header(html_file, out_file)
    html_file.write("<IMG SRC = \'./funds.png\' width = 400/>\n")
    html_file.write("<BR/>\n\n")
    i = 0
    pyplot.clf()
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
            pyplot.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_names[i]))
        else:    
            if(start_date == 0 or start_date>fund[0].index[0]):
                start_date = fund[0].index[0]    
            if(end_date == 0 or end_date<fund[0].index[-1]):
                end_date = fund[0].index[-1]    
            mult = 10000/fund[0].values[0]
            pyplot.plot(fund[0].index, fund[0].values * mult, label = \
                                      path.basename(graph_names[i]))    
        i += 1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = da.DataAccess('Norgate')
    benchmark_close = dataobj.get_data(timestamps, symbol, "close", \
                                            verbose = False)
    mult = 10000/benchmark_close.values[0]
    i = 0
    for fund in funds_list:
        if(type(fund)!= type(list())):
            print_stats(fund, ["$SPX"], graph_names[i])
        else:    
            print_stats( fund[0], ["$SPX"], graph_names[i])
        i += 1
    pyplot.plot(benchmark_close.index, \
                 benchmark_close.values*mult, label = "SSPX")
    pyplot.ylabel('Fund Value')
    pyplot.xlabel('Date')
    pyplot.legend()
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


