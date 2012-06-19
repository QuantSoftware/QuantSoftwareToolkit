'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on May 14, 2012

@author: Sourabh Bajaj
@contact: sourabhbajaj90@gmail.com
@summary: Backtester

'''


# Python imports
from datetime import timedelta

# 3rd Party Imports
import pandas as pand
import numpy as np
from copy import deepcopy

# QSTK imports



def _calculate_leverage(values_by_stock, ts_leverage):
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
            if val >= 0:
                f_long = f_long + val
            else: 
                f_short = f_short + val
        f_lev = (f_long + abs(f_short)) \
                /(f_long + r_val.values[-1] + f_short)

        ts_leverage = ts_leverage.append(pand.Series(f_lev, index = [r_index] ))

    return ts_leverage

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
            i_target_leverage=1, log="false"):
    
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
    
    #open log file 
    if log!="false":
        log_file=open(log,"w")
    
    #write column headings
    if log!="false":
        print "writing transaction log to "+log
        log_file.write("Name,Symbol,Last price,Change,Shares,Date,Type,Commission,\n")
    
    #a dollar is always worth a dollar
    df_historic['_CASH'] = 1.0
 
    # Shares -> Variable holds the shares to be traded on the next timestamp
    # prediction_shares -> Variable holds the shares that were calculated 
                            #for trading based on previous timestamp
    shares = (alloc.ix[0:1] * 0.0)
    shares['_CASH'] = f_start_cash
    prediction_shares = deepcopy(shares)

    # Total commision and Slippage costs 
    f_total_commision = 0
    f_total_slippage = 0
    
    #remember last change in cash due to transaction costs and slippage
    cash_delta = 0
    
    #value of fund ignoring cash_delta
    no_trans_fund = 0
    
    b_first_iter = True

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
        #trade_date = trade_price.index[0]
        if b_first_iter == True:

            # Fund Value on start
            ts_fund = pand.Series( f_start_cash, index = [prediction_date] )
            
            # Ignoring cash delta fund value on start
            no_trans_fund=pand.Series( f_start_cash, index = [prediction_date])

            # Leverage at the start
            ts_leverage = pand.Series( 0, index = [prediction_date] )

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
            no_trans_fund = no_trans_fund.append(values_by_stock.sum(axis=1) - cash_delta)
            #Leverage
            ts_leverage = _calculate_leverage(values_by_stock, ts_leverage)

        #Normalizing the allocations
        proportion = _normalize(row)
        
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
            
        #remove cash delta from current holding
        cash_delta_less_shares=deepcopy(shares)
        cash_delta_less_shares["_CASH"]=cash_delta_less_shares["_CASH"]-cash_delta
        
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
            
            #for all symbols, print required transaction to log
            for sym in shares:
                if sym != "_CASH":
                    commissions=max(f_minimumcommision, f_commision_share*abs(order[sym]))
                    order_type="Buy"
                    if(order[sym]<0):
                        if(shares[sym]<0):
                            order_type="Sell Short"
                        else:
                            order_type="Sell"
                    elif shares[sym]<0:
                        order_type="Buy to Cover"
                    
                    
                    if log!="false":
                        log_file.write(str(sym) + ","+str(sym)+","+str(trade_price[sym].values[0])+","+str(f_slippage*trade_price[sym].values[0])+","+str(abs(int(order[sym])))+","+str(prediction_date)+","+order_type+","+str(commissions))
            
    
            f_total_commision = f_total_commision + f_transaction_cost
    
            # Shares that were actually purchased
            shares = prediction_shares
    
            # Value after the purchase (change in price at execution)
            value_after_trade = (((trade_price + f_slippage*trade_price) \
                                *shares.ix[-1]).sum(axis = 1)).ix[-1]
    
            #Slippage Cost
            f_slippage_cost = value_after_trade - \
                                ((trade_price*shares.ix[-1]).sum(axis=1)).ix[-1]
            f_total_slippage = f_total_slippage + f_slippage_cost
    
            # Rebalancing the cash left
            cashleft = value_before_trade - value_after_trade - f_transaction_cost
            #reset the most recent change in cash
            cash_delta = 0
            cash_delta = cash_delta + cashleft
            shares['_CASH'] = shares['_CASH'] + cashleft
            
            if log!="false":
                log_file.write("\n")

        # End of Loop
    #close log 
    if log!="false":
        log_file.close()
    #print ts_fund
    #print ts_leverage
    #print f_total_commision
    #print f_total_slippage
    return (ts_fund, ts_leverage, f_total_commision, f_total_slippage)


def tradesim_comb( df_alloc, d_data, f_start_cash, i_leastcount=1, 
                   b_followleastcount=False, f_slippage=0.0, 
                   f_minimumcommision=0.0, f_commision_share=0.0, 
                   i_target_leverage=1):
    
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
    
    return tradesim( df_alloc, df_combined, f_start_cash, i_leastcount, 
                   b_followleastcount, f_slippage, f_minimumcommision, 
                   f_commision_share, i_target_leverage)

if __name__ == '__main__':
    print "Done"
