'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.


Created on June, 20, 2012

@author:Drew Bratcher
@contact: dbratcher@gatech.edu
@summary: Contains converter for csv files to fund values. Also may plot.

'''

import sys
import pandas
import csv
from ofxparse import OfxParser
import numpy
import datetime as dt
import dateutil.parser as dp
from Bin import report
from qstksim import _calculate_leverage
from qstkutil import qsdateutil as du
from qstkutil import DataAccess as da

def print_transactions(filename, outfile="stdout"):
    reader=csv.reader(open(filename,'r'), delimiter=',')
    for row in reader:
        for var in row:
            if var == "Cash Deposit":
                var="Deposit"
            elif var == "Cash Withdraw":
                var="Withdraw"
            var=var.split(" ")[0]
            outfile.write("%10s" % str(var))
            outfile.write("  |  ")
        outfile.write("\n")

def analyze_transactions(filename, plot_name):
    ext=filename.split(".")[-1]
    if ext=="csv":
        [share_table, slippage, commissions]=csv2fund(filename,10000)
    else:
        [share_table, slippage, commissions]=ofx2fund(filename,10000)
    [fund, leverage]=share_table2fund(share_table)
    report.print_stats(fund, ["$SPX"], plot_name, leverage=leverage, commissions=commissions, slippage=slippage, directory="./"+plot_name+"/") 
    html_file  =  open("./"+plot_name+"/report-"+plot_name+".html","a")
    html_file.write("<pre>\n\nTransaction Statistics\n")
    #calc stats
    
    #first pass
    reader=csv.reader(open(filename,'r'), delimiter=',')
    reader.next()
    prev=0
    first=1
    diffs=[]
    volume=0
    start=0
    end=0
    efficiencies=[]
    for row in reader:
        volume+=abs(float(row[6]))
        if first:
            #add na for first trade efficiency
            
            start=dp.parse(row[3])
            first=0
            prev=dp.parse(row[3])
        else:
            #try and match trade (grab first date of stocks
            diffs.append(dp.parse(row[3])-prev)
            prev=dp.parse(row[3])
            end=prev
            
    avg_period=sum(diffs, dt.timedelta(0))/len(diffs)
    avg_hold=1
    t=volume/sum(fund)
    turnover=t/(end-start).days
    efficiency=1
    avg_com=1
    avg_slip=1
    avg_ret=1
    
    #print stats
    html_file.write("\nNumber of trades:         %10d" % len(share_table["_CASH"].values))
    html_file.write("\nAverage Trading Period:   %10s" % str(avg_period).split(",")[0])
    html_file.write("\nAverage Position Hold:    %10d" % avg_hold)
    html_file.write("\nAverage Daily Turnover:   %%%9.4f" % (turnover*100))
    html_file.write("\nAverage Trade Efficiency: %10d" % efficiency)
    html_file.write("\nAverage Commissions:      %10d" % avg_com)
    html_file.write("\nAverage Slippage:         %10d" % avg_slip)
    html_file.write("\nAverage Return:           %10d\n\n" % avg_ret)
    
    print_transactions(filename, html_file)
    
    html_file.close()

def csv2fund(filename, start_val):
    """
    @summary converts a csv file to a fund with the given starting value 
    @param filename: csv file to open and convert
    @param start_val: starting value for the portfolio
    @return fund : time series containing fund value over time
    @return leverage : time series containing fund value over time
    @return slippage : value of slippage over the csv time
    @return commissions : value of slippage over the csv time
    """
    reader=csv.reader(open(filename,'r'), delimiter=',')
    reader.next()
    symbols=[]
    dates=[]
    for row in reader:
        if not(row[0] in symbols):
            if not(row[0]=="cash"):
                symbols.append(row[0])
        if not(dp.parse(row[3]) in dates):
            dates.append(dp.parse(row[3]))
    reader=csv.reader(open(filename,'r'), delimiter=',')
    reader.next()
    vals=numpy.zeros([len(dates),len(symbols)+1])
    symbols.append("_CASH")
    share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
    share_table["_CASH"]=0
    share_table["_CASH"].ix[0]=start_val
    commissions=0
    slippage=0
    row_num=0
    for row in reader:
        row_num+=1
        sym=row[0]
        if row_num == 1 and (sym == "_CASH" or sym=="cash"):
            cash=float(row[6])
            date=dp.parse(row[3])
            share_table["_CASH"].ix[date]=cash
            continue
        elif (sym == "_CASH" or sym=="cash"):
            order_type=row[2]
            cash=float(row[6])
            date=dp.parse(row[3])
            if order_type=="Cash Deposit":
                share_table["_CASH"].ix[date]+=cash
            else:
                share_table["_CASH"].ix[date]-=cash
            continue
        price = float(row[5])
        shares=float(row[4])
        date=dp.parse(row[3])
        order_type=row[2]
        commission=float(row[7])
        if order_type=="Buy":
            share_table.ix[date][sym]=shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]-float(price)*float(shares)-float(commission)
        if order_type=="Sell":
            share_table[sym].ix[date]=-1*shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]+float(price)*float(shares)+float(commission)
    share_table=share_table.cumsum()
    return [share_table, slippage, commissions]
    
def ofx2fund(filename, start_val):
    """
    @summary converts a ofx file to a fund with the given starting value 
    @param filename: ofx file to open and convert
    @param start_val: starting value for the portfolio
    @return fund : time series containing fund value over time
    @return leverage : time series containing fund value over time
    @return slippage : value of slippage over the ofx time
    @return commissions : value of slippage over the ofx time
    """
    try:
        from ofxparse import OfxParser
    except:
        print "ofxparse is required to use ofx2fund"
        exit() 
    ofx = OfxParser.parse(file(filename))
    symbols=[]
    dates=[]
    for order in ofx.account.statement.transactions:
        sym=order.security.split(":")[1]
        if not(sym in symbols):
            symbols.append(sym)
        date=order.tradeDate
        if not(date in dates):
            dates.append(date)
    dates.sort()
    vals=numpy.zeros([len(dates),len(symbols)+1])
    symbols.append("_CASH")
    share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
    share_table.ix[0]["_CASH"]=start_val
    for order in ofx.account.statement.transactions:
        sym=order.security.split(":")[1]
        share_table.ix[order.tradeDate][sym]=order.units
        share_table.ix[order.tradeDate]["_CASH"]=share_table.ix[order.tradeDate]["_CASH"]-float(order.unit_price)*float(order.units)
    share_table=share_table.cumsum()
    slippage=0
    commissions=0
    return [share_table, slippage, commissions]
    
def share_table2fund(share_table):
    """
    @summary converts data frame of shares into fund values
    @param share_table: data frame containing shares on days transactions occured
    @return fund : time series containing fund value over time
    @return leverage : time series containing fund value over time
    """
    # Get the data from the data store
    dataobj = da.DataAccess('Norgate')
    startday=share_table.index[0]
    endday = share_table.index[-1]

    # Get desired timestamps
    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday,endday+dt.timedelta(days=1),timeofday)
    historic = dataobj.get_data( timestamps, share_table.columns ,"close" )
    historic["_CASH"]=1
    closest = historic[historic.index <= share_table.index[0]].ix[:]
    ts_leverage = pandas.Series( 0, index = [closest.index[0]] )

    # start shares/fund out as 100% cash
    first_val=closest.ix[-1] * share_table.ix[0]
    fund_ts = pandas.Series( [first_val.sum(axis=1)], index = [closest.index[0]])
    prev_row=share_table.ix[0]
    for row_index, row in share_table.iterrows():
        
        trade_price = historic.ix[row_index:].ix[0:1]
        trade_date = trade_price.index[0]
        
        # get stock prices on all the days up until this trade
        to_calculate = historic[ (historic.index <= trade_date) &(historic.index > fund_ts.index[-1]) ]

        # multiply prices by our current shares
        values_by_stock = to_calculate * prev_row
        prev_row=row
        #update leverage
        ts_leverage = _calculate_leverage(values_by_stock, ts_leverage)
        
        # calculate total value and append to our fund history
        fund_ts = fund_ts.append( [values_by_stock.sum(axis=1)])
        
    return [fund_ts, ts_leverage]

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print "Usage: python csv2fund input.csv name"
        exit()
    filename=sys.argv[1]
    plot_name=sys.argv[2]
    analyze_transactions(filename,plot_name)
    