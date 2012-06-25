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
        
def calculate_efficiency(start_date, end_date, stock):
    # Get the data from the data store
    dataobj = da.DataAccess('Norgate')
    startday=start_date
    endday = end_date

    # Get desired timestamps
    timeofday=dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startday,endday+dt.timedelta(days=1),timeofday)
    historic = dataobj.get_data( timestamps, [stock] ,"close" )
    hi=numpy.max(historic.values)
    low=numpy.min(historic.values)
    entry=historic.values[0]
    exit_price=historic.values[-1]
    return (((exit_price-entry)/(hi-low))[0])

def _ignore_zeros_average(array):
    i_num=0
    f_sum=0
    for var in array:
        if var!=0:
            i_num=i_num+1
            f_sum=f_sum+var
    return f_sum/i_num

def analyze_transactions(filename, plot_name):
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
    sold=0
    bought=0
    end=0
    rets=[]
    efficiencies=[]
    holds=[]
    commissions=[]
    slippage=[]
    buy_dates=[] #matrix of when stocks were bought (used for matches)
    for row in reader:
        weighted_ret=0
        weighted_e=0
        weighted_hold=0
        num_stocks=0
        volume+=1
        if(row[5]!=""):
            commissions.append(float(row[7]))
            slippage.append(float(row[8]))
        if first:
            #add na for first trade efficiency
            start=dp.parse(row[3])
            first=0
            prev=dp.parse(row[3])
        else:
            if row[2] == "Buy":
                bought=bought+float(row[5])
                buy_dates.append({"date":dp.parse(row[3]),"stock":row[1],"amount":row[4],"price":float(row[5])})
            elif row[2] == "Sell":
                sold=sold+float(row[5])
                #try and match trade (grab first date of stocks)
                for date in buy_dates:
                    #matched a date
                    if(date["stock"]==row[1]):
                        #use as many stocks from date as necessary
                        leftover=float(date["amount"])-float(row[4])
                        #compute efficiency
                        temp_e=calculate_efficiency(date["date"], dp.parse(row[3]), row[1])
                        weighted_ret=weighted_ret*num_stocks+(float(row[5])/date["price"])*float(row[4])/(num_stocks+float(row[4]))
                        weighted_hold=weighted_hold*num_stocks+(dp.parse(row[3])-date["date"]).days*float(row[4])/(num_stocks+float(row[4]))
                        weighted_e=weighted_e*num_stocks+temp_e*float(row[4])/(num_stocks+float(row[4]))
                        num_stocks=num_stocks+float(row[4])
                        while(leftover<0):
                            if(date in buy_dates):
                                buy_dates.remove(date)
                            else:
                                break
                            for date in buy_dates:
                                if date["stock"] == row[1]:
                                    leftover= float(date["amount"])-leftover
                                    break
                        if(leftover==0):
                            buy_dates.remove(date)
                        else:
                            date["amount"]=leftover
                        break
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
    avg_slip=_ignore_zeros_average(slippage)
    avg_ret=_ignore_zeros_average(rets)
    
    #print stats
    html_file.write("\nNumber of trades:         %10d" % volume)
    html_file.write("\nAverage Trading Period:   %10s" % str(avg_period).split(",")[0])
    html_file.write("\nAverage Position Hold:    %5d days" % avg_hold)
    html_file.write("\nAverage Daily Turnover:   %%%9.4f" % (turnover*100))
    html_file.write("\nAverage Trade Efficiency: %%%9.4f" % (efficiency*100))
    html_file.write("\nAverage Commissions:      %10d" % avg_com)
    html_file.write("\nAverage Slippage:         %10d" % avg_slip)
    html_file.write("\nAverage Return:           %%%9.4f\n\n" % avg_ret)
    
    reader=csv.reader(open(filename,'r'), delimiter=',')
    a=0
    for row in reader:
        if a==0:
            html_file.write("   Date    | ")
            html_file.write("   Name    | ")
            html_file.write("   Type    | ")
            html_file.write("  Price    | ")
            html_file.write("  Shares   | ")
            html_file.write("Commission | ")
            html_file.write(" Slippage  | ")
            html_file.write("Efficiency  | ")
            html_file.write(" Returns    ")
            a=1
        else:
            var=row[2]
            if var == "Cash Deposit":
                var="Deposit"
            elif var == "Cash Withdraw":
                var="Withdraw"
            var=var.split(" ")[0]
            html_file.write("%10s | " % str(row[3].split()[0]))
            html_file.write("%10s | " % str(row[0]))
            html_file.write("%10s | " % str(var))
            html_file.write("%10s | " % str(row[5]))
            html_file.write("%10s | " % str(row[4]))
            html_file.write("%10s | " % str(row[7]))
            html_file.write("%10s | " % str(row[8]))
            html_file.write(" %%%9.2f | " % (efficiencies[a-1]*100))
            html_file.write(" %%%9.2f " % (rets[a-1]))
            a=a+1
        html_file.write(" | ")
        html_file.write("\n")
                      
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
    if not("_CASH" in symbols):
        symbols.append("_CASH")
    vals=numpy.zeros([len(dates),len(symbols)])
    share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
    share_table["_CASH"]=0
    share_table["_CASH"].ix[0]=start_val
    commissions=0
    slippage=0
    row_num=0
    f_total_slippage=0
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
        slippage=float(row[8])
        f_total_slippage=f_total_slippage+slippage
        if order_type=="Buy":
            share_table.ix[date][sym]=shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]-float(price)*float(shares)-float(commission)-slippage
        if order_type=="Sell":
            share_table[sym].ix[date]=-1*shares
            commissions=commissions+float(commission)
            share_table["_CASH"].ix[date]=share_table.ix[date]["_CASH"]+float(price)*float(shares)-float(commission)-slippage
    share_table=share_table.cumsum()
    return [share_table, f_total_slippage, commissions]
    
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
    filename="../Examples/Basic/transactions.csv"
    plot_name="AAPL"
    analyze_transactions(filename,plot_name)
    