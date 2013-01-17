'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.


Created on October, 2, 2012

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Contains converter for csv files to fund values. Also analyzes transactions.

'''

# import sys
import pandas
import csv
# from ofxparse import OfxParser
import numpy
import pickle
import datetime as dt
import dateutil.parser as dp
from Bin import report
from QSTK.qstksim import _calculate_leverage
from QSTK.qstkutil import qsdateutil as du
from QSTK.qstkutil import DataEvolved as de


def calculate_efficiency(dt_start_date, dt_end_date, s_stock):
    """
    @summary calculates the exit-entry/high-low trade efficiency of a stock from historical data
    @param start_date: entry point for the trade
    @param end_date: exit point for the trade
    @param stock: stock to compute efficiency for
    @return: float representing efficiency
    """
    # Get the data from the data store
    dataobj = de.DataAccess('mysql')

    # Get desired timestamps
    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(dt_start_date,dt_end_date+dt.timedelta(days=1),timeofday)
    historic = dataobj.get_data( timestamps, [s_stock] ,["close"] )[0]
    # print "######"
    # print historic
    hi=numpy.max(historic.values)
    low=numpy.min(historic.values)
    entry=historic.values[0]
    exit_price=historic.values[-1]
    return (((exit_price-entry)/(hi-low))[0])

def _ignore_zeros_average(array):
    """
    @summary internal function computes average ignoring zero elements
    @param array: array to compute average for
    @return: float average
    """
    i_num=0
    f_sum=0
    for var in array:
        if var!=0:
            i_num=i_num+1
            f_sum=f_sum+var
    if i_num==0:
        i_num=1
    return f_sum/i_num

def analyze_transactions(filename, plot_name, share_table, show_transactions=False):
    """
    @summary computes various statistics for given filename and appends to report assumed via plot_name
    @param filename: file of past transactions
    @param plot_name: name of report
    """
    html_file  =  open("./"+plot_name+"/report-"+plot_name+".html","a")
    html_file.write("<pre>\n\nTransaction Statistics\n")
    #calc stats

    #first pass
    reader=csv.reader(open(filename,'rU'), delimiter=',')
    reader.next()
    prev=0
    first=1
    diffs=[]
    volume=0
    start=0
    sold=0
    bought=0
    end=0
    rets=[]
    efficiencies=[]
    holds=[]
    commissions=[]
    # slippage=[]
    buy_dates=[] #matrix of when stocks were bought (used for matches)
    for row in reader:
        weighted_ret=0
        weighted_e=0
        weighted_hold=0
        num_stocks=0
        volume+=1
        if(row[7]!=''):
            commissions.append(float(row[7]))
            # slippage.append(float(row[8]))
        if first:
            #add na for first trade efficiency
            start=dp.parse(row[3])
            first=0
            prev=dp.parse(row[3])
        else:
            if row[2] == "Buy":
                bought=bought+float(row[5])
                buy_dates.append({"date":dp.parse(row[3]),"stock":row[0],"amount":row[4],"price":float(row[5])})
            elif row[2] == "Sell":
                #sold at price
                sold=sold+float(row[5])
                #get number of stocks for this sell
                stocks=float(row[4])
                #try and match trade (grab first date of stocks)
                for date in buy_dates:
                    #while stocks are left
                    if(stocks>0):
                        #match a date
                        if(date["stock"]==row[1]):
                            stocks_sold=0
                            #use as many stocks from date as necessary
                            leftover=float(date["amount"])-stocks
                            if(leftover>0):
                                date["amount"]=leftover
                                stocks_sold=stocks
                                #compute stats
                                temp_e=calculate_efficiency(date["date"], dp.parse(row[3]), row[0])
                                weighted_ret=(weighted_ret*num_stocks+(float(row[5])/date["price"])*stocks_sold)/(num_stocks+stocks_sold)
                                weighted_hold=(weighted_hold*num_stocks+(dp.parse(row[3])-date["date"]).days*stocks_sold)/(num_stocks+stocks_sold)
                                weighted_e=(weighted_e*num_stocks+temp_e*stocks_sold)/(num_stocks+stocks_sold)
                                num_stocks=num_stocks+stocks_sold
                                break
                            else:
                                stocks_sold=float(date["amount"])
                                stocks=stocks-stocks_sold
                                #compute stats
                                temp_e=calculate_efficiency(date["date"], dp.parse(row[3]), row[0])
                                weighted_ret=(weighted_ret*num_stocks+(float(row[5])/date["price"])*stocks_sold)/(num_stocks+stocks_sold)
                                weighted_hold=(weighted_hold*num_stocks+(dp.parse(row[3])-date["date"]).days*stocks_sold)/(num_stocks+stocks_sold)
                                weighted_e=(weighted_e*num_stocks+temp_e*stocks_sold)/(num_stocks+stocks_sold)
                                num_stocks=num_stocks+stocks_sold
                                date["stock"]="DONE"
                                #buy_dates.remove(date)
            #elif row[2] == "Sell Short":
                #do nothing
            #elif row[2] == "Buy to Cover":
                #do nothing
            # elif row[2] == "Deposit Cash":

            if(prev!=dp.parse(row[3])):
                diffs.append(dp.parse(row[3])-prev)
                prev=dp.parse(row[3])
                end=prev
        holds.append(weighted_hold)
        efficiencies.append(weighted_e)
        rets.append(weighted_ret*100)

    avg_period=sum(diffs, dt.timedelta(0))/len(diffs)
    avg_hold=_ignore_zeros_average(holds)
    t=sold/(bought+sold)
    turnover=t/(end-start).days
    efficiency=_ignore_zeros_average(efficiencies)
    avg_com=_ignore_zeros_average(commissions)
    # avg_slip=_ignore_zeros_average(slippage)
    avg_ret=_ignore_zeros_average(rets)

    #print stats
    html_file.write("\nNumber of trades:         %10d" % volume)
    html_file.write("\nAverage Trading Period:   %10s" % str(avg_period).split(",")[0])
    html_file.write("\nAverage Position Hold:    %5d days" % avg_hold)
    html_file.write("\nAverage Daily Turnover:   %%%9.4f" % (turnover*100))
    html_file.write("\nAverage Trade Efficiency: %%%9.4f" % (efficiency*100))
    html_file.write("\nAverage Commissions:      %10d" % avg_com)
    # html_file.write("\nAverage Slippage:         %10d" % avg_slip)
    html_file.write("\nAverage Return:           %%%9.4f\n\n" % avg_ret)

    html_file.write("Positions by Date\n")
    for date in share_table.index:
        html_file.write("\nPosition for day: "+str(date).split()[0])
        html_file.write("\n")
        i=0
        for item in share_table.ix[date]:
            if(item>0):
                html_file.write("%15s" % str(share_table.columns[i]))
            i=i+1
        html_file.write("\n")
        for item in share_table.ix[date]:
            if(item>0):
                html_file.write("%15s" % str(item))
        html_file.write("\n\nTransactions for day:\n")
        reader=csv.reader(open(filename,'rU'), delimiter=',')
        a=0
        cash=0
        if(show_transactions):
            for row in reader:
                if a==0:
                    html_file.write("   Date      | ")
                    html_file.write("   Name    | ")
                    html_file.write("   Type    | ")
                    html_file.write("  Price    | ")
                    html_file.write("  Shares   | ")
                    html_file.write("Commission | ")
                    # html_file.write(" Slippage  | ")
                    html_file.write("OnHand Cash| ")
                    html_file.write("Efficiency  | ")
                    html_file.write(" Returns    ")
                    html_file.write(" | ")
                    html_file.write("\n")
                    a=1
                else:
                    compute=False
                    if(len(str(row[3]).split())>2):
                        compute=(dt.datetime.strptime(str(row[3]),"%b %d, %Y")==date)
                    else:
                        compute=(str(row[3])==str(date))
                    if(compute):
                        var=row[2]
                        if var == "Cash Deposit":
                            cash=cash+float(row[6])
                            var="Deposit"
                        elif var == "Cash Withdraw":
                            cash=cash-float(row[6])
                            var="Withdraw"
                        else:
                            cash=cash-float(row[6])
                        var=var.split(" ")[0]
                        html_file.write("%12s | " % str(row[3].split(':')[0]))
                        html_file.write("%10s | " % str(row[0]))
                        html_file.write("%10s | " % str(var))
                        html_file.write("%10s | " % str(row[5]))
                        html_file.write("%10s | " % str(row[4]))
                        html_file.write("%10s | " % str(row[7]))
                        html_file.write("%10s | " % str(row[8]))
                        html_file.write("%10s | " % str(round(cash,2)))
                        html_file.write(" %%%9.2f | " % (efficiencies[a-1]*100))
                        html_file.write(" %%%9.2f " % (rets[a-1]))
                        a=a+1
                        html_file.write(" | ")
                        html_file.write("\n")

    html_file.close()

def csv2fund(filename):
    """
    @summary converts a csv file to a fund with the given starting value
    @param filename: csv file to open and convert
    @param start_val: starting value for the portfolio
    @return fund : time series containing fund value over time
    @return leverage : time series containing fund value over time
    @return slippage : value of slippage over the csv time
    @return commissions : value of slippage over the csv time
    """
    reader=csv.reader(open(filename,'rU'), delimiter=',')
    reader.next()
    symbols=[]
    dates=[]
    for row in reader:
        if not(row[0] in symbols):
            if not(row[0]=="cash" or row[0] == ''):
                symbols.append(row[0])
        if not(dp.parse(row[3]) in dates):
            dates.append(dp.parse(row[3]))
    print symbols
    reader=csv.reader(open(filename,'rU'), delimiter=',')
    reader.next()
    if not("_CASH" in symbols):
        symbols.append("_CASH")
    vals=numpy.zeros([len(dates),len(symbols)])
    share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
    share_table["_CASH"]=0
    # share_table["_CASH"].ix[0]=start_val
    commissions=0

    for row in reader:
        date=dp.parse(row[3])
        order_type=row[2]
        sym = row[0]
        if order_type != 'Deposit Cash':
            price = float(row[5])
            shares=float(row[4])
            commission=float(row[7])

        if order_type=="Deposit Cash":
            cash = float(row[6])
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]+ cash
        if order_type=="Buy":
            share_table.ix[date][sym]+=shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]-float(price)*float(shares)-float(commission)
        if order_type=="Sell":
            share_table[sym].ix[date]+=-1*shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]+float(price)*float(shares)-float(commission)
        if order_type=="Sell Short":
            share_table[sym].ix[date]+=-1*shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]+float(price)*float(shares)-float(commission)
        if order_type=="Buy to Cover":
            share_table.ix[date][sym]+=shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date] = share_table.ix[date]["_CASH"]-float(price)*float(shares)-float(commission)
    share_table = share_table.cumsum()
    time_index = sorted(share_table.index)
    column_index = sorted(share_table.columns)
    share_table = share_table.reindex(index=time_index, columns=column_index)
    i_start_cash = share_table["_CASH"].ix[0]
    print i_start_cash
    return [share_table, commissions, i_start_cash]

# def ofx2fund(filename, start_val):
#     """
#     @summary converts a ofx file to a fund with the given starting value
#     @param filename: ofx file to open and convert
#     @param start_val: starting value for the portfolio
#     @return fund : time series containing fund value over time
#     @return leverage : time series containing fund value over time
#     @return slippage : value of slippage over the ofx time
#     @return commissions : value of slippage over the ofx time
#     """
#     try:
#         from ofxparse import OfxParser
#     except:
#         print "ofxparse is required to use ofx2fund"
#         exit()
#     ofx = OfxParser.parse(file(filename))
#     symbols=[]
#     dates=[]
#     for order in ofx.account.statement.transactions:
#         sym=order.security.split(":")[1]
#         if not(sym in symbols):
#             symbols.append(sym)
#         date=order.tradeDate
#         if not(date in dates):
#             dates.append(date)
#     dates.sort()
#     vals=numpy.zeros([len(dates),len(symbols)+1])
#     symbols.append("_CASH")
#     share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
#     share_table.ix[0]["_CASH"]=start_val
#     for order in ofx.account.statement.transactions:
#         sym=order.security.split(":")[1]
#         share_table.ix[order.tradeDate][sym]=order.units
#         share_table.ix[order.tradeDate]["_CASH"]=share_table.ix[order.tradeDate]["_CASH"]-float(order.unit_price)*float(order.units)
#     share_table=share_table.cumsum()
#     slippage=0
#     commissions=0
#     return [share_table, slippage, commissions]


def share_table2fund(share_table):
    """
    @summary converts data frame of shares into fund values
    @param share_table: data frame containing shares on days transactions occured
    @return fund : time series containing fund value over time
    @return leverage : time series containing fund value over time
    """
    # Get the data from the data store
    dataobj = de.DataAccess('mysql')
    startday = share_table.index[0]
    endday = share_table.index[-1]

    symbols = list(share_table.columns)
    symbols.remove('_CASH')

    # print symbols

    # Get desired timestamps
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday - dt.timedelta(days=5), endday + dt.timedelta(days=1), timeofday)
    historic = dataobj.get_data(timestamps, symbols, ["close"])[0]
    historic.fillna(method='ffill', inplace=True)
    historic["_CASH"] = 1
    closest = historic[historic.index <= share_table.index[0]].ix[:]
    ts_leverage = pandas.Series(0, index=[closest.index[-1]])

    # start shares/fund out as 100% cash
    first_val = closest.ix[-1] * share_table.ix[0]
    fund_ts = pandas.Series([first_val.sum(axis=1)], index=[closest.index[-1]])
    prev_row = share_table.ix[0]
    for row_index, row in share_table.iterrows():
        # print row_index
        trade_price = historic.ix[row_index:].ix[0:1]
        trade_date = trade_price.index[0]

        # print trade_date

        # get stock prices on all the days up until this trade
        to_calculate = historic[(historic.index <= trade_date) & (historic.index > fund_ts.index[-1])]
        # multiply prices by our current shares
        values_by_stock = to_calculate * prev_row

        # for date, sym in values_by_stock.iteritems():
        #     print date,sym
        # print values_by_stock
        prev_row = row
        #update leverage
        ts_leverage = _calculate_leverage(values_by_stock, ts_leverage)

        # calculate total value and append to our fund history
        fund_ts = fund_ts.append([values_by_stock.sum(axis=1)])
    return [fund_ts, ts_leverage]

if __name__ == "__main__":
    filename = "Strat.csv"
    plot_name = "Strategy"
    print "load csv"
    [share_table, commissions, i_start_cash] = csv2fund(filename)
    print share_table
    [fund_ts, ts_leverage] = share_table2fund(share_table)
    print "print report"
    print fund_ts
    report.print_stats(fund_ts, ["SPY"], plot_name, directory="./" + plot_name, commissions=commissions, i_start_cash=i_start_cash)
    print "analyze transactions"
    #Generate new plot based off transactions alone
    analyze_transactions(filename, plot_name, share_table, True)
    print "done"
