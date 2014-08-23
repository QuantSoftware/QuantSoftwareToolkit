'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 14, 2012

@author: Sourabh Bajaj
@contact: sourabh@sourabhbajaj.com
@summary: Backtester

'''


# Python imports
from datetime import timedelta

# 3rd Party Imports
import pandas as pand
import numpy as np
from copy import deepcopy

# QSTK imports
from QSTK.qstkutil import tsutil as tsu

def _calculate_leverage(values_by_stock, ts_leverage, ts_long_exposure, ts_short_exposure, ts_net_exposure):
    """
    @summary calculates leverage based on the dataframe values_by_stock
             and returns the updated timeseries of leverage
    @param values_by_stock: Dataframe containing the values held in
             in each stock in the portfolio
    @param ts_leverage: time series of leverage values
    @return ts_leverage : updated time series of leverage values
    """

    for r_index, r_val in values_by_stock.iterrows():
        f_long = 0
        f_short = 0
        for val in r_val.values[:-1]:
            if np.isnan(val) == False:
                if val >= 0:
                    f_long = f_long + val
                else:
                    f_short = f_short + val
                
        f_lev = (f_long + abs(f_short)) \
                /(f_long + r_val.values[-1] + f_short)
        f_net = (f_long - abs(f_short)) \
                /(f_long + r_val.values[-1] + f_short)
        f_long_ex = (f_long) \
                /(f_long + r_val.values[-1] + f_short)
        f_short_ex = (abs(f_short)) \
                /(f_long + r_val.values[-1] + f_short)                

        if np.isnan(f_lev): f_lev = 0
        if np.isnan(f_net): f_net = 0
        if np.isnan(f_long): f_long = 0
        if np.isnan(f_short): f_short = 0

        ts_leverage = ts_leverage.append(pand.Series(f_lev, index = [r_index] ))
        ts_long_exposure = ts_long_exposure.append(pand.Series(f_long_ex, index = [r_index] ))
        ts_short_exposure = ts_short_exposure.append(pand.Series(f_short_ex, index = [r_index] ))
        ts_net_exposure = ts_net_exposure.append(pand.Series(f_net, index = [r_index] ))

    return ts_leverage, ts_long_exposure, ts_short_exposure, ts_net_exposure
    
    
def _monthly_turnover(ts_orders, ts_fund):
    
    order_val_month = 0
    last_date = ts_orders.index[0]
    b_first_month = True
    ts_turnover = "None"
    for date in ts_orders.index:
        if last_date.month == date.month:
            order_val_month += ts_orders.ix[date]
        else:
            if b_first_month == True:
                ts_turnover = pand.Series(order_val_month, index=[last_date])
                b_first_month = False
            else:
                ts_turnover = ts_turnover.append(pand.Series(order_val_month, index=[last_date]))
            order_val_month = ts_orders.ix[date]
            last_date = date
            
    if type(ts_turnover) != type("None"):
        ts_turnover = ts_turnover.append(pand.Series(order_val_month, index=[last_date]))
    else:
        ts_turnover = pand.Series(order_val_month, index=[last_date])
    
    order_month = 0
    len_orders = len(ts_turnover.index)
    last_date = ts_fund.index[0]
    
    for date in ts_fund.index:
        if order_month < len_orders:
            if (ts_turnover.index[order_month]).month != date.month:
                ts_turnover.ix[ts_turnover.index[order_month]] = ts_turnover.ix[ts_turnover.index[order_month]]/(2*ts_fund.ix[last_date])
                order_month += 1 
            else:
                last_date = date
        else:
            if date.month == last_date.month:
                last_date = date
            else:
                break
    
    ts_turnover.ix[ts_turnover.index[-1]] = ts_turnover.ix[ts_turnover.index[-1]]/(2*ts_fund.ix[last_date])           

    return ts_turnover


def _normalize(row):

    """
    @summary Normalize an allocation row based on sum(abs(alloc))
    @param row: single row of the allocation dataframe
    @param proportion: normalized proportion of the row
    """
    total = row.abs().sum()
    proportion = row/total
    return proportion

def _nearest_interger(f_x):

    """
    @summary Return the nearest integer to the float number
    @param x: single float number
    @return: nearest integer to x
    """
    if f_x >= 0:
        return np.floor(f_x)
    else :
        return np.ceil(f_x)

def tradesim( alloc, df_historic, f_start_cash, i_leastcount=1,
            b_followleastcount=False, f_slippage=0.0,
            f_minimumcommision=0.0, f_commision_share=0.0,
            i_target_leverage=1, f_rate_borrow = 0.0, log="false", b_exposure=False):

    """
    @summary Quickly back tests an allocation for certain df_historical data,
             using a starting fund value
    @param alloc: DataMatrix containing timestamps to test as indices and
                 Symbols to test as columns, with _CASH symbol as the last
                 column
    @param df_historic: df_historic dataframe of equity prices
    @param f_start_cash: integer specifing initial fund value
    @param i_leastcount: Minimum no. of shares per transaction, ie: 1, 10, 20
    @param f_slippage: slippage per share (0.02)
    @param f_minimumcommision: Minimum commision cost per transaction
    @param f_commision_share: Commision per share
    @param b_followleastcount: False will allow fractional shares
    @param log: CSV file to log transactions to
    @return funds: TimeSeries with fund values for each day in the back test
    @return leverage: TimeSeries with Leverage values for each day in the back test
    @return Commision costs : Total commision costs in the whole backtester
    @return Slippage costs : Total slippage costs in the whole backtester
    @rtype TimeSeries
    """

    if alloc.index[-1] > df_historic.index[-1]:
        print "Historical Data not sufficient"
        indices, = np.where(alloc.index <= df_historic.index[-1])
        alloc = alloc.reindex(index = alloc.index[indices])

    if alloc.index[0] < df_historic.index[0]:
        print "Historical Data not sufficient"
        indices, = np.where(alloc.index >= df_historic.index[0])
        alloc = alloc.reindex(index = alloc.index[indices])

    #open log file
    if log!="false":
        log_file=open(log,"w")

    #write column headings
    if log!="false":
        print "writing transaction log to "+log
        log_file.write("Symbol,Company Name,Txn Type,Txn Date/Time, Gross Leverage, Net Leverage,# Shares,Price,Txn Value,Portfolio # Shares,Portfolio Value,Commission,Slippage(10BPS),Comments\n")

    #a dollar is always worth a dollar
    df_historic['_CASH'] = 1.0

    # Shares -> Variable holds the shares to be traded on the next timestamp
    # prediction_shares -> Variable holds the shares that were calculated
                            #for trading based on previous timestamp
    shares = (alloc.ix[0:1] * 0.0)
    shares['_CASH'] = f_start_cash
    prediction_shares = deepcopy(shares)

    # Total commision and Slippage costs
    f_total_commision = 0.0
    f_total_slippage = 0.0
    f_total_borrow = 0.0

    #remember last change in cash due to transaction costs and slippage
    cashleft = 0.0

    #value of fund ignoring cashleft
    no_trans_fund = 0.0

    dt_last_date = None
    f_last_borrow = 0.0
    b_first_iter = True
    b_order_flag = True

    for row_index, row in alloc.iterrows():

        # Trade Date and Price (Next timestamp)
        # Prediction Date and Price (Previous timestamp)

        trade_price = df_historic.ix[row_index:].ix[0:1]
        trade_index = df_historic.index.searchsorted(trade_price.index[0])
        pred_index = trade_index - 1
        prediction_price = \
                  df_historic.ix[df_historic.index[pred_index]:].ix[0:1]

        prediction_date = prediction_price.index[0]

        #trade_date is unused right now, but holds the next timestamp
        trade_date = trade_price.index[0]

        if b_first_iter == True:
            #log initial cash value
            if log!="false":
                log_file.write("_CASH,_CASH,Cash Deposit,"+str(prediction_date)+",,,,,"+str(f_start_cash)+",,\n")


            # Fund Value on start
            ts_fund = pand.Series( f_start_cash, index = [prediction_date] )

            # Ignoring cash delta fund value on start
            no_trans_fund=pand.Series( f_start_cash, index = [prediction_date])

            # Leverage at the start
            ts_leverage = pand.Series( 0, index = [prediction_date] )
            ts_long_exposure = pand.Series(0, index=[prediction_date])
            ts_short_exposure = pand.Series(0, index=[prediction_date])
            ts_net_exposure = pand.Series(0, index=[prediction_date])

            ts_orders = None

            days_since_alloc = 0
            f_borrow_cost = 0.0

            # Flag for first iteration is False now
            b_first_iter = False

        else :
            # get stock prices on all the days up until this trade
            to_calculate = df_historic[ (df_historic.index <= prediction_date) \
                        & (df_historic.index > ts_fund.index[-1]) ]

            # multiply prices by our current shares
            values_by_stock = to_calculate * shares.ix[-1]

            # calculate total value and append to our fund history
            ts_fund = ts_fund.append( values_by_stock.sum(axis=1) )
            # remember what value would be without cash delta as well
            no_trans_fund = no_trans_fund.append(values_by_stock.sum(axis=1) - cashleft)

            #Leverage
            ts_leverage, ts_long_exposure, ts_short_exposure, ts_net_exposure = _calculate_leverage(
                                        values_by_stock, ts_leverage, ts_long_exposure, ts_short_exposure, ts_net_exposure)

            days_since_alloc = (trade_date - dt_last_date).days
            f_borrow_cost = abs((days_since_alloc*f_last_borrow*f_rate_borrow)/(100*365))
            f_total_borrow = f_total_borrow + f_borrow_cost

        #Normalizing the allocations
        proportion = _normalize(row)
        '''
        indices_short = np.where(proportion.values < 0)
        short_val = abs(sum(proportion.values[indices_short]))

        indices_long = np.where(proportion.values >= 0)
        long_val = abs(sum(proportion.values[indices_long]))

        sl_ratio = short_val/long_val
        '''
        # Allocation to be scaled upto the allowed Leverage
        proportion = proportion*i_target_leverage

        #Amount allotted to each equity
        value_allotted = proportion*ts_fund.ix[-1]

        value_before_trade = ts_fund.ix[-1]

        # Get shares to be purchased
        prediction_shares = value_allotted/ prediction_price

        #ignoring cash delta calculate value allotted per share and cacluclate number of shares for each
        ntva=proportion*no_trans_fund.ix[-1]
        no_trans_shares = ntva/prediction_price


        #Adjusting the amount of shares to be purchased based on the leastcount
        # default is 1 : whole number of shares

        if b_followleastcount == True:
            prediction_shares /= i_leastcount
            prediction_shares = prediction_shares.apply(_nearest_interger)
            prediction_shares *= i_leastcount
            #handle shares ignoring last cash delta similarly
            no_trans_shares /= i_leastcount
            no_trans_shares = no_trans_shares.apply(_nearest_interger)
            no_trans_shares *= i_leastcount

        #remove cashleft from current holding
        cash_delta_less_shares=deepcopy(shares)
        cash_delta_less_shares["_CASH"]=cash_delta_less_shares["_CASH"]-cashleft


        #compare current holding to future holding (both ignoring the last round of transmission cost and slippage)
        same=1
        for sym in shares:
            if str(cash_delta_less_shares[sym].values[0])!=str(no_trans_shares[sym].values[0]):
                same=0

        #if same:
        #perform a transaction
        if same==0:
            #print "transaction"
            #print tampered_shares
            #print no_trans_shares
            #Order to be executed
            order = pand.Series(((prediction_shares.values \
                    - shares.values)[0])[:-1], index = row.index[:-1])

            # Transaction costs
            f_transaction_cost = 0
            for index in order.index:
                val = abs(order[index])
                if (val != 0):
                    t_cost = max(f_minimumcommision, f_commision_share*val)
                    f_transaction_cost = f_transaction_cost + t_cost

            f_total_commision = f_total_commision + f_transaction_cost

            value_before_trade = ((trade_price*shares.ix[-1]).sum(axis = 1)).ix[-1]

            # Shares that were actually purchased
            shares = prediction_shares

            # Value after the purchase (change in price at execution)
            value_after_trade = ((trade_price*shares.ix[-1]).sum(axis = 1)).ix[-1]

            #Slippage Cost
            f_slippage_cost = f_slippage*(trade_price.values[0][:-1])*order.values
            f_slippage_cost = abs(f_slippage_cost)
            f_slippage_cost[np.isnan(f_slippage_cost)] = 0.0
            f_slippage_cost = f_slippage_cost.sum()

            #Orders
            f_order = (1+f_slippage)*(trade_price.values[0][:-1])*order.values
            f_order = abs(f_order)
            f_order[np.isnan(f_order)] = 0.0
            f_order = f_order.sum()
            
            if b_order_flag == True:
                ts_orders = pand.Series(f_order, index=[trade_date])
                b_order_flag = False
            else:
                ts_orders = ts_orders.append(pand.Series(f_order, index=[trade_date]))

            if np.isnan(f_slippage_cost) == False:
                f_total_slippage = f_total_slippage + f_slippage_cost
                # Rebalancing the cash left
                cashleft = value_before_trade - value_after_trade - f_transaction_cost - f_slippage_cost - f_borrow_cost
            else:
                cashleft = value_before_trade - value_after_trade - f_transaction_cost - f_borrow_cost


            dt_last_date = trade_date
            f_last_holding = ((trade_price*shares.ix[-1]).ix[-1]).values
            indices = np.where(f_last_holding < 0)
            f_last_borrow = abs(sum(f_last_holding[indices]))

            shares['_CASH'] = shares['_CASH'] + cashleft

            money_short = f_last_borrow
            indices_long = np.where(f_last_holding >= 0)
            money_long = abs(sum(f_last_holding[indices_long]))
            money_cash = cashleft

            GL = (money_long + money_short) / (money_long - money_short + money_cash)
            NL = (money_long - money_short) / (money_long - money_short + money_cash)


            #for all symbols, print required transaction to log
            for sym in shares:
                if sym != "_CASH":
                    f_stock_commission=max(f_minimumcommision, f_commision_share*abs(order[sym]))
                    order_type="Buy"
                    if(order[sym]<0):
                        if(shares[sym]<0):
                            order_type="Sell Short"
                        else:
                            order_type="Sell"
                    elif shares[sym]<0:
                        order_type="Buy to Cover"


                    if log!="false":
                        if(abs(order[sym])!=0):
                            log_file.write(str(sym) + ","+str(sym)+","+order_type+","+str(trade_date)+","+str(GL)+","+str(NL)+\
                                       ","+str(order[sym])+","+str(trade_price[sym].values[0])+","+\
                                        str(trade_price[sym].values[0]*order[sym])+","\
                                       +str(shares[sym].ix[-1])+","+str(value_after_trade)+","+str(f_stock_commission)+","+\
                                        str(round(f_slippage_cost,2))+",")
                            log_file.write("\n")

        # End of Loop


    #close log
    if log!="false":
        #deposit nothing at end so that if we reload the transaction history the whole period gets shown
        log_file.write("_CASH,_CASH,Cash Deposit,"+str(prediction_date)+",,,,,"+str(0)+",,")
        log_file.close()
    #print ts_fund
    #print ts_leverage
    #print f_total_commision
    #print f_total_slippage
    #print f_total_borrow

    ts_turnover = _monthly_turnover(ts_orders, ts_fund)
    
    if b_exposure:
        return (ts_fund, ts_leverage, f_total_commision, f_total_slippage, f_total_borrow, 
                        ts_long_exposure, ts_short_exposure, ts_net_exposure, ts_turnover)
    return (ts_fund, ts_leverage, f_total_commision, f_total_slippage, f_total_borrow)


def tradesim_comb( df_alloc, d_data, f_start_cash, i_leastcount=1,
                   b_followleastcount=False, f_slippage=0.0,
                   f_minimumcommision=0.0, f_commision_share=0.0,
                   i_target_leverage=1, f_rate_borrow = 0.0, log="false", b_exposure=False):

    """
    @summary Same as tradesim, but combines open and close data into one.
    @param alloc: DataMatrix containing timestamps to test as indices and
                 Symbols to test as columns, with _CASH symbol as the last
                 column
    @param d_data: Historic dictionary of dataframes containing 'open' and
                   'close'
    @param f_start_cash: integer specifing initial fund value
    @param i_leastcount: Minimum no. of shares per transaction, ie: 1, 10, 20
    @param f_slippage: slippage per share (0.02)
    @param f_minimumcommision: Minimum commision cost per transaction
    @param f_commision_share: Commision per share
    @param b_followleastcount: False will allow fractional shares
    @return funds: TimeSeries with fund values for each day in the back test
    @return leverage: TimeSeries with Leverage values for each day in the back test
    @return Commision costs : Total commision costs in the whole backtester
    @return Slippage costs : Total slippage costs in the whole backtester
    @rtype TimeSeries
    """

    df_close = d_data['close']
    df_open = d_data['open']

    f_shift_close = 16. - df_close.index[0].hour
    f_shift_open = 9.5 - df_open.index[0].hour

    df_new_close = df_close.shift( 1, timedelta(hours=f_shift_close) )
    df_new_open = df_open.shift( 1, timedelta(hours=f_shift_open) )

    df_combined = df_new_close.append( df_new_open ).sort()

    return tradesim(df_alloc, df_combined, f_start_cash, i_leastcount,
                   b_followleastcount, f_slippage, f_minimumcommision,
                   f_commision_share, i_target_leverage, f_rate_borrow, log, b_exposure)

if __name__ == '__main__':
    print "Done"
