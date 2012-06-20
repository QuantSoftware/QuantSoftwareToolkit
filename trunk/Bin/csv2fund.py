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

def csv2fund(filename, start_val):
    reader=csv.reader(open(filename,'r'), delimiter=',')
    format="GOOG"
    x=reader.next()
    if x[5]=="Date":
        format="QSTK"
    symbols=[]
    dates=[]
    if(format=="GOOG"):
        for row in reader:
            if not(row[0] in symbols):
                symbols.append(row[0])
            if not(dp.parse(row[3]) in symbols):
                dates.append(dp.parse(row[3]))
    else:
        for row in reader:
            if not(row[0] in symbols):
                symbols.append(row[0])
            if not(dp.parse(row[5]) in symbols):
                dates.append(dp.parse(row[5]))
        
    reader=csv.reader(open(filename,'r'), delimiter=',')
    reader.next()
    vals=numpy.zeros([len(dates),len(symbols)+1])
    symbols.append("_CASH")
    share_table=pandas.DataFrame(index=dates, columns=symbols, data=vals)
    share_table["_CASH"]=0
    share_table.ix[0]["_CASH"]=start_val
    commissions=0
    slippage=0
    for row in reader:
        if(format=="GOOG"):
            sym=row[0]
            price = float(row[5])
            shares=float(row[4])
            date=dp.parse(row[3])
            order_type=row[2]
            commission=float(row[7])
        else:
            sym=row[0]
            price = float(row[2])
            shares=float(row[4])
            date=dp.parse(row[5])
            order_type=row[6]
            commission=float(row[7])
        if order_type=="Buy":
            share_table.ix[date][sym]=shares
            commissions=commissions+float(commission)
            share_table.ix[date]["_CASH"]=share_table.ix[date]["_CASH"]-float(price)*float(shares)-float(commission)
        if order_type=="Sell":
            share_table.ix[date][sym]=-1*shares
            commissions=commissions+float(commission)
            share_table.ix[date]["_CASH"]=share_table.ix[date]["_CASH"]+float(price)*float(shares)+float(commission)
    share_table=share_table.cumsum()
    [fund, leverage]=share_table2fund(share_table)
    return [fund, leverage, slippage, commissions]
    
def ofx2fund(filename, start_val):
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
    [fund, leverage]=share_table2fund(share_table)
    slippage=0
    commissions=0
    return [fund, leverage, slippage, commissions]
    
def share_table2fund(share_table):
    # Get the data from the data store
    dataobj = da.DataAccess('Norgate')
    startday=share_table.index[0]-dt.timedelta(days=10)
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
    
    for row_index, row in share_table.iterrows():
        
        trade_price = historic.ix[row_index:].ix[0:1]
        trade_date = trade_price.index[0]
        
        # get stock prices on all the days up until this trade
        to_calculate = historic[ (historic.index <= trade_date) &(historic.index > fund_ts.index[-1]) ]

        # multiply prices by our current shares
        values_by_stock = to_calculate * row
        
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
    ext=filename.split(".")[1]
    plot_name=sys.argv[2]
    if ext=="csv":
        [fund, leverage, slippage, commissions]=csv2fund(filename,10000)
    else:
        [fund, leverage, slippage, commissions]=ofx2fund(filename,10000)
    report.print_stats(fund, ["$SPX"], plot_name, leverage=leverage, commissions=commissions, slippage=slippage, directory="./"+plot_name+"/")
    