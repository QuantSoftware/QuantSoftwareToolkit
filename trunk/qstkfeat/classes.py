'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various classification functions

'''

# 3rd Party Imports 
import pandas as pand
import numpy as np

def class_fut_ret( d_data, i_lookforward=21, s_rel=None, b_use_open=False ):
    '''
    @summary: Calculate classification, uses future returns 
    @param d_data: Dictionary of data to use
    @param i_lookforward: Number of days to look in the future
    @param s_rel: Stock symbol that this should be relative to, ususally $SPX.
    @param b_use_open: If True, stock will be purchased at T+1 open, sold at 
        T+i_lookforward close
    @return: DataFrame containing values
    '''
    
    df_close = d_data['close']
    
    # Class DataFrame will be 1:1, we can use the price as a template, 
    # need to copy values 
    df_ret = pand.DataFrame( index=df_close.index, columns=df_close.columns,
                            data=np.copy(df_close.values) ) 
    
    # If we want market relative, calculate those values now
    if not s_rel == None:
        
        #assert False, 'Use generic MR param instead,
        # recognized by applyfeatures'
        
        i_len = len(df_close[s_rel].index)
        
        # Loop over time
        for i in range(i_len):
            
            if i + i_lookforward >= i_len:
                df_ret[s_rel][i] = float('nan')
                continue
            
            # We either buy on todays close or tomorrows open
            if b_use_open:
                df_open = d_data['open']
                f_buy = df_open[s_rel][i + 1]
                f_sell = df_open[s_rel][i + 1 + i_lookforward]
            else:
                f_buy = df_close[s_rel][i]
                f_sell = df_close[s_rel][i + i_lookforward]
                
            df_ret[s_rel][i] = (f_sell - f_buy) / f_buy
    
    # Loop through stocks
    for s_stock in df_close.columns:
        
        # We have already done this stock
        if s_stock == s_rel:
            continue
        
        i_len = len(df_close[s_stock].index)
        # Loop over time
        for i in range(i_len):
            
            if i + i_lookforward >= i_len:
                df_ret[s_stock][i] = float('nan')
                continue
            
            # We either buy on todays close or tomorrows open
            if b_use_open:
                df_open = d_data['open']
                f_buy = df_open[s_stock][i + 1]
                f_sell = df_open[s_stock][i + 1 + i_lookforward]
            else:
                f_buy = df_close[s_stock][i]
                f_sell = df_close[s_stock][i + i_lookforward]
                
            df_ret[s_stock][i] = (f_sell - f_buy) / f_buy
            
            # Make market relative 
            if not s_rel == None:
                df_ret[s_stock][i] -= df_ret[s_rel][i]
            
    return df_ret


if __name__ == '__main__':
    pass
