'''

(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

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
    
    if b_use_open:
        df_val = d_data['open'].copy()
    else:
        df_val = d_data['close'].copy()
    
    na_val = df_val.values

    if b_use_open:
        na_val[:-(i_lookforward + 1), :] = ((na_val[i_lookforward + 1:, :] -
                                       na_val[1:-(i_lookforward), :]) /
                                       na_val[1:-(i_lookforward), :])
        na_val[-(i_lookforward+1):, :] = np.nan
        
    else:
        na_val[:-i_lookforward, :] = ((na_val[i_lookforward:, :] -
                                       na_val[:-i_lookforward, :]) /
                                       na_val[:-i_lookforward, :])
        na_val[-i_lookforward:, :] = np.nan

    return df_val


if __name__ == '__main__':
    pass
