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
from QSTK.qstkutil import DataAccess as de
from QSTK.qstkutil import qsdateutil as du
from QSTK.qstkutil import tsutil as tsu
from QSTK.qstkutil import fundutil as fu
from dateutil.relativedelta import relativedelta
import numpy as np
from math import log10
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
import scipy.stats as scst

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

def get_annual_return(fund_ts, years):
    """
    @summary prints annual return for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    lf_ret=[]
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year ==year):
                year_vals.append([fund_ts.ix[date]])
        day_rets = tsu.daily1(year_vals)
        ret = tsu.get_ror_annual(day_rets)
        ret=float(ret)
        lf_ret.append(ret*100) #" %+8.2f%%" % (ret*100)
    return lf_ret

def get_winning_days(fund_ts, years):
    """
    @summary prints winning days for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    s_ret=""
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_winning_days(year_vals)
        s_ret+=" % + 8.2f%%" % ret
    return s_ret

def get_max_draw_down(fund_ts, years):
    """
    @summary prints max draw down for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    s_ret=""
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append(fund_ts.ix[date])
        ret = fu.get_max_draw_down(year_vals)
        s_ret+=" % + 8.2f%%" % (ret*100)
    return s_ret

def get_daily_sharpe(fund_ts, years):
    """
    @summary prints sharpe ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    s_ret=""
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sharpe_ratio(year_vals)
        s_ret+=" % + 8.2f " % ret
    return s_ret

def get_daily_sortino(fund_ts, years):
    """
    @summary prints sortino ratio for given fund and years to the given stream
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    s_ret=""
    for year in years:
        year_vals = []
        for date in fund_ts.index:
            if(date.year==year):
                year_vals.append([fund_ts.ix[date]])
        ret = fu.get_sortino_ratio(year_vals)
        s_ret+=" % + 8.2f " % ret
    return s_ret

def get_std_dev(fund_ts):
    """
    @summary gets standard deviation of returns for a fund as a string
    @param fund_ts: pandas fund time series
    @param years: list of years to print out
    @param ostream: stream to print to
    """
    fund_ts=fund_ts.fillna(method='pad')
    fund_ts=fund_ts.fillna(method='bfill')
    ret=np.std(tsu.daily(fund_ts.values))*10000
    return ("%+7.2f bps " % ret)


def ks_statistic(fund_ts):
    fund_ts = deepcopy(fund_ts)
    if len(fund_ts.values) > 60:
        seq1 = fund_ts.values[0:-60]
        seq2 = fund_ts.values[-60:]
        tsu.returnize0(seq1)
        tsu.returnize0(seq2)
        (ks, p) = scst.ks_2samp(seq1, seq2)
        return ks, p
    # elif len(fund_ts.values) > 5:
    #     seq1 = fund_ts.values[0:-5]
    #     seq2 = fund_ts.values[-5:]
    #     (ks, p) = scst.ks_2samp(seq1, seq2)
    #     return ks, p

    ks = -1
    p = -1
    return ks, p

def ks_statistic_calc(fund_ts_past, fund_ts_month):
    try:
        seq1 = deepcopy(fund_ts_past.values)
        seq2 = deepcopy(fund_ts_month.values)
        tsu.returnize0(seq1)
        tsu.returnize0(seq2)
        (ks, p) = scst.ks_2samp(seq1, seq2)
        return ks, p
    except:
        return -1,-1

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
        norObj = de.DataAccess('Yahoo')
        ldtTimestamps = du.getNYSEdays( fund_ts.index[0], fund_ts.index[-1], dt.timedelta(hours=16) )
        ldfData = norObj.get_data( ldtTimestamps, [industries[i][0]], ['close'] )
        #get corelation
        ldfData[0]=ldfData[0].fillna(method='pad')
        ldfData[0]=ldfData[0].fillna(method='bfill')
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
        norObj =de.DataAccess('Yahoo')
        ldtTimestamps = du.getNYSEdays( fund_ts.index[0], fund_ts.index[-1], dt.timedelta(hours=16) )
        ldfData = norObj.get_data( ldtTimestamps, [industries[i][0]], ['close'] )
        #get corelation
        ldfData[0]=ldfData[0].fillna(method='pad')
        ldfData[0]=ldfData[0].fillna(method='bfill')
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
    fund_ts=fund_ts.fillna(method='bfill')
    benchmark_close=benchmark_close.fillna(method='pad')
    benchmark_close=benchmark_close.fillna(method='bfill')
    faCorr=np.corrcoef(np.ravel(tsu.daily(fund_ts.values)),np.ravel(tsu.daily(benchmark_close)));
    b=np.ravel(tsu.daily(benchmark_close))
    f=np.ravel(tsu.daily(fund_ts))
    fBeta, unused = np.polyfit(b,f, 1);
    print_line(sym+"Correlattion","%+6.2f" % faCorr[0,1],i_spacing=3,ostream=ostream)
    print_line(sym+"Beta","%+6.2f" % fBeta,i_spacing=3,ostream=ostream)

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



def print_monthly_turnover(fund_ts, years, ts_turnover, ostream):
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
    # mrets = tsu.monthly(fund_ts)
    for year in years:
        ostream.write(str(year))
        months = du.getMonths(ts_turnover, year)
        if months != []:
            for k in range(1, months[0]):
                ostream.write("       ")
        for month in months:
            ostream.write(" % + 6.2f" % (ts_turnover[i]*100))
            i += 1
        ostream.write("\n")
        
def print_monthly_ks(fund_ts, years, ostream):
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

    # mrets = tsu.monthly(fund_ts)
    m_str = []

    for i, year in enumerate(years):
        months = du.getMonths(fund_ts, year)
        for j, month in enumerate(months):
            if i == 0 and j < 3:
                m_str.append('    ')
            else:
                # dt_st = max(fund_ts.index[0], dt.datetime(year, month, 1)-relativedelta(months=6))
                dt_st = fund_ts.index[0]
                dt_today = dt.datetime(year, month, 1) - relativedelta(months=2)
                dt_end = min(dt.datetime(year, month, 1) + relativedelta(months=1) + dt.timedelta(hours=-5), fund_ts.index[-1])
                fund_ts_past = fund_ts.ix[dt_st: dt_today]
                fund_ts_month = fund_ts.ix[dt_today: dt_end]
                ks, p = ks_statistic_calc(fund_ts_past, fund_ts_month)
                if not(ks == -1 or p == -1):
                    if ks < p:
                        m_str.append('PASS')
                    else:
                        m_str.append('FAIL')
                else:
                    m_str.append('    ')

    i = 0
    for year in years:
        ostream.write(str(year))
        months = du.getMonths(fund_ts, year)
        for k in range(1, months[0]):
            ostream.write("       ")
        for month in months:
            ostream.write("%7s" % (m_str[i]))
            i = i + 1
        ostream.write("\n")


def print_years(years, ostream):
    ostream.write("\n")
    s_line=""
    s_line2=""
    for f_token in years:
        s_line+="%9d " % f_token
        s_line2+="%10s" % '------'

    ostream.write("%35s %s%30s\n" % ("                  ", " "*4, s_line))
    ostream.write("%35s %s%30s\n" % ("                  ", " "*4, s_line2))


def print_line(s_left_side, s_right_side, i_spacing=0, ostream="stdout"):
    ostream.write("%35s:%s%30s\n" % (s_left_side, " "*i_spacing, s_right_side))

def print_stats(fund_ts, benchmark, name, lf_dividend_rets=0.0, original="",s_fund_name="Fund",
    s_original_name="Original", d_trading_params="", d_hedge_params="", s_comments="", directory = False,
    leverage = False, s_leverage_name="Leverage", commissions = 0, slippage = 0, borrowcost = 0, ostream = sys.stdout, 
    i_start_cash=1000000, ts_turnover="False"):
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

    if original != "" and type(original) != type([]):
        original = [original]
        if type(s_original_name) != type([]):
            s_original_name = [s_original_name]

    #make names length independent for alignment
    s_formatted_original_name = []
    for name_temp in s_original_name:
        s_formatted_original_name.append("%15s" % name_temp)
    s_formatted_fund_name = "%15s" % s_fund_name

    fund_ts=fund_ts.fillna(method='pad')
    fund_ts=fund_ts.fillna(method='bfill')
    fund_ts=fund_ts.fillna(1.0)
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
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets, leverage=leverage, i_start_cash = i_start_cash, s_leverage_name=s_leverage_name)
            else:
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets, i_start_cash = i_start_cash)
        else:
            if type(leverage)!=type(False):
                print_plot([fund_ts, original], benchmark, name, splot_dir, s_original_name, lf_dividend_rets,
                             leverage=leverage, i_start_cash = i_start_cash, s_leverage_name=s_leverage_name)
            else:
                print_plot([fund_ts, original], benchmark, name, splot_dir, s_original_name, lf_dividend_rets, i_start_cash = i_start_cash)

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
            print_line(var, d_trading_params[var],ostream=ostream)
    if d_hedge_params!="":
        ostream.write("\nHedging Paramaters\n\n")
        if type(d_hedge_params['Weight of Hedge']) == type(float):
            d_hedge_params['Weight of Hedge'] = str(int(d_hedge_params['Weight of Hedge']*100)) + '%'
        for var in d_hedge_params:
            print_line(var, d_hedge_params[var],ostream=ostream)

    #comment section
    if s_comments!="":
        ostream.write("\nComments\n\n%s" % s_comments)


    if directory != False :
        ostream.write("\n\n<img src="+splot+" width=700 />\n\n")

    mult = i_start_cash/fund_ts.values[0]


    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(fund_ts.index[0], fund_ts.index[-1], timeofday)
    dataobj =de.DataAccess('Yahoo')
    years = du.getYears(fund_ts)
    benchmark_close = dataobj.get_data(timestamps, benchmark, ["close"], \
                                                     verbose = False)[0]
    for bench_sym in benchmark:
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(method='pad')
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(method='bfill')
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(1.0)

    if type(lf_dividend_rets) != type(0.0):
        for i,sym in enumerate(benchmark):
            benchmark_close[sym] = _dividend_rets_funds(benchmark_close[sym], lf_dividend_rets[i])

    ostream.write("Resulting Values in $ with an initial investment of "+ locale.currency(int(round(i_start_cash)), grouping=True) + "\n")

    print_line(s_formatted_fund_name+" Resulting Value"," %15s, %10.2f%%" % (locale.currency(int(round(fund_ts.values[-1]*mult)), grouping=True), \
                                                     float(100*((fund_ts.values[-1]/fund_ts.values[0])-1))), i_spacing=4, ostream=ostream)

    # if type(original)!=type("str"):
    #     mult3 = i_start_cash / original.values[0]
    #     # print_line(s_formatted_original_name +" Resulting Value",(locale.currency(int(round(original.values[-1]*mult3)), grouping=True)),i_spacing=3, ostream=ostream)
    #     print_line(s_formatted_original_name+" Resulting Value"," %15s, %10.2f%%" % (locale.currency(int(round(original.values[-1]*mult3)), grouping=True), \
    #                                                  float(100*((original.values[-1]/original.values[0])-1))), i_spacing=4, ostream=ostream)

    if type(original)!=type("str"):
        for i in range(len(original)):
            mult3 = i_start_cash / original[i].values[0]
            # print_line(s_formatted_original_name +" Resulting Value",(locale.currency(int(round(original[i].values[-1]*mult3)), grouping=True)),i_spacing=3, ostream=ostream)
            print_line(s_formatted_original_name[i]+" Resulting Value"," %15s, %10.2f%%" % (locale.currency(int(round(original[i].values[-1]*mult3)), grouping=True), \
                                                     float(100*((original[i].values[-1]/original[i].values[0])-1))), i_spacing=4, ostream=ostream)

    for bench_sym in benchmark:
        mult2= i_start_cash / benchmark_close[bench_sym].values[0]
        # print_line(bench_sym+" Resulting Value",locale.currency(int(round(benchmark_close[bench_sym].values[-1]*mult2)), grouping=True),i_spacing=3, ostream=ostream)
        print_line(bench_sym+" Resulting Value"," %15s, %10.2f%%" % (locale.currency(int(round(benchmark_close[bench_sym].values[-1]*mult2)), grouping=True), \
                                                     float(100*((benchmark_close[bench_sym].values[-1]/benchmark_close[bench_sym].values[0])-1))), i_spacing=4, ostream=ostream)

    ostream.write("\n")

    # if len(years) > 1:
    print_line(s_formatted_fund_name+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(fund_ts.values)[0],i_spacing=4, ostream=ostream)
    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(original[i].values)[0],i_spacing=4, ostream=ostream)

    for bench_sym in benchmark:
        print_line(bench_sym+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(benchmark_close[bench_sym].values)[0],i_spacing=4,ostream=ostream)
    ostream.write("\n")


    # KS - Similarity
    # ks, p = ks_statistic(fund_ts);
    # if ks!= -1 and p!= -1:
    #     if ks < p:
    #         ostream.write("\nThe last three month's returns are consistent with previous performance (KS = %2.5f, p = %2.5f) \n\n"% (ks, p))
    #     else:
    #         ostream.write("\nThe last three month's returns are NOT CONSISTENT with previous performance (KS = %2.5f, p = %2.5f) \n\n"% (ks, p))


    ostream.write("Transaction Costs\n")
    print_line("Total Commissions"," %15s, %10.2f%%" % (locale.currency(int(round(commissions)), grouping=True), \
                                                  float((round(commissions)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Slippage"," %15s, %10.2f%%" % (locale.currency(int(round(slippage)), grouping=True), \
                                                     float((round(slippage)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Short Borrowing Cost"," %15s, %10.2f%%" % (locale.currency(int(round(borrowcost)), grouping=True), \
                                                     float((round(borrowcost)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Costs"," %15s, %10.2f%%" % (locale.currency(int(round(borrowcost+slippage+commissions)), grouping=True), \
                                  float((round(borrowcost+slippage+commissions)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    ostream.write("\n")

    print_line(s_formatted_fund_name+" Std Dev of Returns",get_std_dev(fund_ts),i_spacing=8, ostream=ostream)

    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Std Dev of Returns", get_std_dev(original[i]), i_spacing=8, ostream=ostream)

    for bench_sym in benchmark:
        print_line(bench_sym+" Std Dev of Returns", get_std_dev(benchmark_close[bench_sym]), i_spacing=8, ostream=ostream)

    ostream.write("\n")


    for bench_sym in benchmark:
        print_benchmark_coer(fund_ts, benchmark_close[bench_sym], str(bench_sym), ostream)
    ostream.write("\n")

    ostream.write("\nYearly Performance Metrics")
    print_years(years, ostream)


    s_line=""
    for f_token in get_annual_return(fund_ts, years):
        s_line+=" %+8.2f%%" % f_token
    print_line(s_formatted_fund_name+" Annualized Return",s_line, i_spacing=4, ostream=ostream)


    if type(original)!=type("str"):
        for i in range(len(original)):
            s_line=""
            for f_token in get_annual_return(original[i], years):
                s_line+=" %+8.2f%%" % f_token
            print_line(s_formatted_original_name[i]+" Annualized Return", s_line, i_spacing=4, ostream=ostream)

    for bench_sym in benchmark:
        s_line=""
        for f_token in get_annual_return(benchmark_close[bench_sym], years):
            s_line+=" %+8.2f%%" % f_token
        print_line(bench_sym+" Annualized Return", s_line, i_spacing=4, ostream=ostream)

    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Winning Days",get_winning_days(fund_ts, years), i_spacing=4, ostream=ostream)


    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Winning Days",get_winning_days(original[i], years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Winning Days",get_winning_days(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Max Draw Down",get_max_draw_down(fund_ts, years), i_spacing=4, ostream=ostream)

    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Max Draw Down",get_max_draw_down(original[i], years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Max Draw Down",get_max_draw_down(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)


    print_line(s_formatted_fund_name+" Daily Sharpe Ratio",get_daily_sharpe(fund_ts, years), i_spacing=4, ostream=ostream)


    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Daily Sharpe Ratio",get_daily_sharpe(original[i], years), i_spacing=4, ostream=ostream)

    for bench_sym in benchmark:
        print_line(bench_sym+" Daily Sharpe Ratio",get_daily_sharpe(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Daily Sortino Ratio",get_daily_sortino(fund_ts, years), i_spacing=4, ostream=ostream)

    if type(original)!=type("str"):
        for i in range(len(original)):
            print_line(s_formatted_original_name[i]+" Daily Sortino Ratio",get_daily_sortino(original[i], years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Daily Sortino Ratio",get_daily_sortino(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    ostream.write("\n\n\nCorrelation and Beta with DJ Industries for the Fund ")

    print_industry_coer(fund_ts,ostream)

    ostream.write("\n\nCorrelation and Beta with Other Indices for the Fund ")

    print_other_coer(fund_ts,ostream)

    ostream.write("\n\n\nMonthly Returns for the Fund %\n")

    print_monthly_returns(fund_ts, years, ostream)

    if type(ts_turnover) != type("False"):
        ostream.write("\n\nMonthly Turnover for the fund\n")
        print_monthly_turnover(fund_ts, years, ts_turnover, ostream)

    ostream.write("\n\n3 Month Kolmogorov-Smirnov 2-Sample Similarity Test\n")

    print_monthly_ks(fund_ts, years, ostream)

    ks, p = ks_statistic(fund_ts);
    if ks!= -1 and p!= -1:
        ostream.write("\nResults for the Similarity Test over last 3 months : (KS = %2.5f, p = %2.5f) \n\n"% (ks, p))

    if directory != False:
        ostream.write("</pre>")


def print_html(fund_ts, benchmark, name, lf_dividend_rets=0.0, original="",
    s_fund_name="Fund", s_original_name="Original", d_trading_params="", d_hedge_params="",
    s_comments="", directory=False, leverage=False, s_leverage_name="Leverage",commissions=0, slippage=0,
    borrowcost=0, ostream=sys.stdout, i_start_cash=1000000):
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

    #make names length independent for alignment
    s_formatted_original_name="%15s" % s_original_name
    s_formatted_fund_name = "%15s" % s_fund_name

    fund_ts=fund_ts.fillna(method='pad')
    if directory != False :
        if not path.exists(directory):
            makedirs(directory)

        sfile = path.join(directory, "report-%s.html" % name )
        splot = "plot-%s.png" % name
        splot_dir =  path.join(directory, splot)
        ostream = open(sfile, "wb")
        print "writing to ", sfile

        if type(original)==type("str"):
            if type(leverage)!=type(False):
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets, leverage=leverage, i_start_cash = i_start_cash, s_leverage_name=s_leverage_name)
            else:
                print_plot(fund_ts, benchmark, name, splot_dir, lf_dividend_rets, i_start_cash = i_start_cash)
        else:
            if type(leverage)!=type(False):
                print_plot([fund_ts, original], benchmark, name, splot_dir, s_original_name, lf_dividend_rets, leverage=leverage, i_start_cash = i_start_cash, s_leverage_name=s_leverage_name)
            else:
                print_plot([fund_ts, original], benchmark, name, splot_dir, s_original_name, lf_dividend_rets, i_start_cash = i_start_cash)

    print_header(ostream,name)
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
            print_line(var, d_trading_params[var],ostream=ostream)
    if d_hedge_params!="":
        ostream.write("\nHedging Paramaters\n\n")
        if type(d_hedge_params['Weight of Hedge']) == type(float):
            d_hedge_params['Weight of Hedge'] = str(int(d_hedge_params['Weight of Hedge']*100)) + '%'
        for var in d_hedge_params:
            print_line(var, d_hedge_params[var],ostream=ostream)

    #comment section
    if s_comments!="":
        ostream.write("\nComments\n\n%s" % s_comments)


    if directory != False :
        ostream.write("\n\n<img src="+splot+" width=600 />\n\n")

    mult = i_start_cash/fund_ts.values[0]


    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(fund_ts.index[0], fund_ts.index[-1], timeofday)
    dataobj =de.DataAccess('Yahoo')
    years = du.getYears(fund_ts)
    benchmark_close = dataobj.get_data(timestamps, benchmark, ["close"])
    benchmark_close=benchmark_close[0]
    for bench_sym in benchmark:
        benchmark_close[bench_sym]=benchmark_close[bench_sym].fillna(method='pad')

    if type(lf_dividend_rets) != type(0.0):
        for i,sym in enumerate(benchmark):
            benchmark_close[sym] = _dividend_rets_funds(benchmark_close[sym], lf_dividend_rets[i])

    ostream.write("Resulting Values in $ with an initial investment of "+ locale.currency(int(round(i_start_cash)), grouping=True) + "\n")

    print_line(s_formatted_fund_name+" Resulting Value",(locale.currency(int(round(fund_ts.values[-1]*mult)), grouping=True)),i_spacing=3, ostream=ostream)

    if type(original)!=type("str"):
        mult3 = i_start_cash / original.values[0]
        print_line(s_formatted_original_name +" Resulting Value",(locale.currency(int(round(original.values[-1]*mult3)), grouping=True)),i_spacing=3, ostream=ostream)

    for bench_sym in benchmark:
        mult2=i_start_cash/benchmark_close[bench_sym].values[0]
        print_line(bench_sym+" Resulting Value",locale.currency(int(round(benchmark_close[bench_sym].values[-1]*mult2)), grouping=True),i_spacing=3, ostream=ostream)

    ostream.write("\n")

    if len(years) > 1:
        print_line(s_formatted_fund_name+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(fund_ts.values)[0],i_spacing=4, ostream=ostream)
        if type(original)!=type("str"):
            print_line(s_formatted_original_name+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(original.values)[0],i_spacing=4, ostream=ostream)

        for bench_sym in benchmark:
            print_line(bench_sym+" Sharpe Ratio","%10.3f" % fu.get_sharpe_ratio(benchmark_close[bench_sym].values)[0],i_spacing=4,ostream=ostream)
        ostream.write("\n")

    ostream.write("Transaction Costs\n")
    print_line("Total Commissions"," %15s, %10.2f%%" % (locale.currency(int(round(commissions)), grouping=True), \
                                                  float((round(commissions)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Slippage"," %15s, %10.2f%%" % (locale.currency(int(round(slippage)), grouping=True), \
                                                     float((round(slippage)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Short Borrowing Cost"," %15s, %10.2f%%" % (locale.currency(int(round(borrowcost)), grouping=True), \
                                                     float((round(borrowcost)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    print_line("Total Costs"," %15s, %10.2f%%" % (locale.currency(int(round(borrowcost+slippage+commissions)), grouping=True), \
                                  float((round(borrowcost+slippage+commissions)*100)/(fund_ts.values[-1]*mult))), i_spacing=4, ostream=ostream)

    ostream.write("\n")

    print_line(s_formatted_fund_name+" Std Dev of Returns",get_std_dev(fund_ts),i_spacing=8, ostream=ostream)

    if type(original)!=type("str"):
        print_line(s_formatted_original_name+" Std Dev of Returns", get_std_dev(original), i_spacing=8, ostream=ostream)

    for bench_sym in benchmark:
        print_line(bench_sym+" Std Dev of Returns", get_std_dev(benchmark_close[bench_sym]), i_spacing=8, ostream=ostream)

    ostream.write("\n")


    for bench_sym in benchmark:
        print_benchmark_coer(fund_ts, benchmark_close[bench_sym], str(bench_sym), ostream)
    ostream.write("\n")

    ostream.write("\nYearly Performance Metrics")
    print_years(years, ostream)

    s_line=""
    for f_token in get_annual_return(fund_ts, years):
        s_line+=" %+8.2f%%" % f_token
    print_line(s_formatted_fund_name+" Annualized Return", s_line, i_spacing=4, ostream=ostream)
    lf_vals=[get_annual_return(fund_ts, years)]
    ls_labels=[name]

    if type(original)!=type("str"):
        s_line=""
        for f_token in get_annual_return(original, years):
            s_line+=" %+8.2f%%" % f_token
        print_line(s_formatted_original_name+" Annualized Return", s_line, i_spacing=4, ostream=ostream)
        lf_vals.append(get_annual_return(original, years))
        ls_labels.append(s_original_name)

    for bench_sym in benchmark:
        s_line=""
        for f_token in get_annual_return(benchmark_close[bench_sym], years):
            s_line+=" %+8.2f%%" % f_token
        print_line(bench_sym+" Annualized Return", s_line, i_spacing=4, ostream=ostream)
        lf_vals.append(get_annual_return(benchmark_close[bench_sym], years))
        ls_labels.append(bench_sym)

    print lf_vals
    print ls_labels
    ls_year_labels=[]
    for i in range(0,len(years)):
        ls_year_labels.append(str(years[i]))
    print_bar_chart(lf_vals, ls_labels, ls_year_labels, directory+"/annual_rets.png")

    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Winning Days",get_winning_days(fund_ts, years), i_spacing=4, ostream=ostream)


    if type(original)!=type("str"):
        print_line(s_formatted_original_name+" Winning Days",get_winning_days(original, years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Winning Days",get_winning_days(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Max Draw Down",get_max_draw_down(fund_ts, years), i_spacing=4, ostream=ostream)

    if type(original)!=type("str"):
        print_line(s_formatted_original_name+" Max Draw Down",get_max_draw_down(original, years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Max Draw Down",get_max_draw_down(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)


    print_line(s_formatted_fund_name+" Daily Sharpe Ratio",get_daily_sharpe(fund_ts, years), i_spacing=4, ostream=ostream)


    if type(original)!=type("str"):
        print_line(s_formatted_original_name+" Daily Sharpe Ratio",get_daily_sharpe(original, years), i_spacing=4, ostream=ostream)

    for bench_sym in benchmark:
        print_line(bench_sym+" Daily Sharpe Ratio",get_daily_sharpe(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    print_years(years, ostream)

    print_line(s_formatted_fund_name+" Daily Sortino Ratio",get_daily_sortino(fund_ts, years), i_spacing=4, ostream=ostream)

    if type(original)!=type("str"):
        print_line(s_formatted_original_name+" Daily Sortino Ratio",get_daily_sortino(original, years), i_spacing=4, ostream=ostream)


    for bench_sym in benchmark:
        print_line(bench_sym+" Daily Sortino Ratio",get_daily_sortino(benchmark_close[bench_sym], years), i_spacing=4, ostream=ostream)


    ostream.write("\n\n\nCorrelation and Beta with DJ Industries for the Fund ")

    print_industry_coer(fund_ts,ostream)

    ostream.write("\n\nCorrelation and Beta with Other Indices for the Fund ")

    print_other_coer(fund_ts,ostream)

    ostream.write("\n\n\nMonthly Returns for the Fund %\n")

    print_monthly_returns(fund_ts, years, ostream)
    print_footer(ostream)

def print_bar_chart(llf_vals, ls_fund_labels, ls_year_labels, s_filename):
    llf_vals=((1,2,3),(3,2,1),(2,2,2))
    amin=min(min(llf_vals))
    print amin
    min_lim=0
    if amin<0:
        min_lim = amin
    ls_fund_labels=("Fund 1","Benchmark","Original")
    ls_year_labels=("2000","2001","2002")
    pyplot.clf()
    ind = np.arange(len(ls_year_labels))
    ind=ind*2
    width = 0.35
    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    colors=('r','g','b')
    rects=[]
    for i in range(0,len(llf_vals)):
        rects.append( ax.bar(ind+width*i, llf_vals[i], width, color=colors[i]))
    ax.set_ylabel('Annual Return')
    ax.set_ylim(min_lim, 5)
    ax.set_title('Annual Return by Fund and Year')
    ax.set_xticks(ind+width*len(llf_vals)/2)
    ax.set_xticklabels(ls_year_labels)
    plots=[]
    for i in range(0,len(llf_vals)):
        plots.append(rects[i][0])
    ax.legend(plots,ls_fund_labels)

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom')
    for i in range(0,len(llf_vals)):
        autolabel(rects[i])
    savefig(s_filename, format = 'png')

def print_plot(fund, benchmark, graph_name, filename, s_original_name="", lf_dividend_rets=0.0, leverage=False, i_start_cash = 1000000, s_leverage_name="Leverage"):
    """
    @summary prints a plot of a provided fund and benchmark
    @param fund: fund value in pandas timeseries
    @param benchmark: benchmark symbol to compare fund to
    @param graph_name: name to associate with the fund in the report
    @param filename: file location to store plot1
    """
    pyplot.clf()
    fig = pyplot.figure()
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')

    if type(leverage)==type(False):
        ax = pyplot.subplot(111)
    else:
        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
        ax = pyplot.subplot(gs[0])

    start_date = 0
    end_date = 0
    if(type(fund)!= type(list())):
        if(start_date == 0 or start_date>fund.index[0]):
            start_date = fund.index[0]
        if(end_date == 0 or end_date<fund.index[-1]):
            end_date = fund.index[-1]
        mult = i_start_cash/fund.values[0]
        pyplot.plot(fund.index, fund.values * mult,'b', label = \
                                 path.basename(graph_name))
    else:
        i=0
        for entity in fund:
            if i == 1 and len(fund)!=1:
                for j in range(len(entity)):
                    if(start_date == 0 or start_date>entity[j].index[0]):
                        start_date = entity[j].index[0]
                    if(end_date == 0 or end_date<entity[j].index[-1]):
                        end_date = entity[j].index[-1]
                    mult = i_start_cash/entity[j].values[0]
                    if j ==0:
                        pyplot.plot(entity[j].index, entity[j].values * mult, 'k', label = \
                                      s_original_name[j])
                    else:
                        pyplot.plot(entity[j].index, entity[j].values * mult, 'g', label = \
                                      s_original_name[j])
            else:
                if(start_date == 0 or start_date>entity.index[0]):
                    start_date = entity.index[0]
                if(end_date == 0 or end_date<entity.index[-1]):
                    end_date = entity.index[-1]
                mult = i_start_cash/entity.values[0]
                pyplot.plot(entity.index, entity.values * mult, 'b', label = \
                                  path.basename(graph_name))
            i=i+1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = de.DataAccess('Yahoo')
    benchmark_close = dataobj.get_data(timestamps, benchmark, ["close"])
    benchmark_close = benchmark_close[0]
    benchmark_close = benchmark_close.fillna(method='pad')
    benchmark_close = benchmark_close.fillna(method='bfill')
    benchmark_close = benchmark_close.fillna(1.0)

    if type(lf_dividend_rets) != type(0.0):
        for i,sym in enumerate(benchmark):
            benchmark_close[sym] = _dividend_rets_funds(benchmark_close[sym], lf_dividend_rets[i])

    for i,sym in enumerate(benchmark):
        mult = i_start_cash / benchmark_close[sym].values[0]
        pyplot.plot(benchmark_close[sym].index, \
                benchmark_close[sym].values*mult, 'r', label = sym)

    # pyplot.gcf().autofmt_xdate()
    # pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
    # pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    pyplot.xlabel('Date', size='xx-small')
    pyplot.ylabel('Fund Value', size='xx-small')
    pyplot.xticks(size='xx-small')
    pyplot.yticks(size='xx-small')

    # Shink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(prop=fontP, loc='upper center', bbox_to_anchor=(0.5, -0.05),
               ncol=3)


    if type(leverage)!=type(False):
        ax1 = pyplot.subplot(gs[1])
        if type(leverage) == type([]):
            for i in range(len(leverage)):
                pyplot.plot(leverage[i].index, leverage[i].values, label=s_leverage_name[i])
        else:
            pyplot.plot(leverage.index, leverage.values, label=s_leverage_name)
        # pyplot.gcf().autofmt_xdate()
        # pyplot.gca().fmt_xdata = mdates.DateFormatter('%m-%d-%Y')
        # pyplot.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
        if type(leverage) != type([]):
            labels=[]
            max_label=max(leverage.values)
            min_label=min(leverage.values)
            rounder= -1*(round(log10(max_label))-1)
            labels.append(round(min_label*0.9, int(rounder)))
            labels.append(round((max_label+min_label)/2, int(rounder)))
            labels.append(round(max_label*1.1, int(rounder)))
            pyplot.yticks(labels, size='xx-small')
        # pyplot.title(graph_name + " Leverage")
        pyplot.xlabel('Date', size='xx-small')
        pyplot.ylabel('Exposure', size='xx-small')
        pyplot.xticks(size='xx-small')
        pyplot.yticks(size='xx-small')

        # Shink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax1.legend(prop=fontP, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                   ncol=3)

    pyplot.savefig(filename, format = 'png')


def generate_report(funds_list, graph_names, out_file, i_start_cash = 10000):
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
            mult = i_start_cash/fund.values[0]
            pyplot.plot(fund.index, fund.values * mult, label = \
                                 path.basename(graph_names[i]))
        else:
            if(start_date == 0 or start_date>fund[0].index[0]):
                start_date = fund[0].index[0]
            if(end_date == 0 or end_date<fund[0].index[-1]):
                end_date = fund[0].index[-1]
            mult = i_start_cash/fund[0].values[0]
            pyplot.plot(fund[0].index, fund[0].values * mult, label = \
                                      path.basename(graph_names[i]))
        i += 1
    timeofday = dt.timedelta(hours = 16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)
    dataobj = de.DataAccess('Yahoo')
    benchmark_close = dataobj.get_data(timestamps, symbol, ["close"], \
                                            verbose = False)[0]
    mult = i_start_cash/benchmark_close.values[0]
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
    # converter.fundsToPNG(fund_matrix,'funds.png')
    html_file.write("<H2>QSTK Generated Report:" + out_file + "</H2>\n")
    # html_file.write("<IMG SRC = \'./funds.png\'/>\n")
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


