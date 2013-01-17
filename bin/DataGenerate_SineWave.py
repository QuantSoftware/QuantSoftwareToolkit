import datetime as dt
import csv
import copy
import os
import pickle
import math

# 3rd party imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# QSTK imports
from QSTK.qstkutil import qsdateutil as du
# import qstkutil.DataEvolved as de

def write(ls_symbols, d_data, ldt_timestamps):

    ldt_timestamps.reverse()
    ls_keys = ['actual_open', 'actual_high', 'actual_low', 'actual_close', 'volume', 'close']

    length = len(ldt_timestamps)

    for symbol in ls_symbols:

        sym_file = open('./' + symbol + '.csv', 'w')
        sym_file.write("Date,Open,High,Low,Close,Volume,Adj Close \n")

        for i,date in enumerate(ldt_timestamps):
            date_to_csv = '{:%Y-%m-%d}'.format(date)
            string_to_csv = date_to_csv

            for key in ls_keys:
                string_to_csv = string_to_csv + ',' + str(d_data[symbol][length-i-1])

            string_to_csv = string_to_csv + '\n'
            sym_file.write(string_to_csv)


def main():
    print "Creating Stock data from Sine Waves"
    dt_start = dt.datetime(2000, 1, 1)
    dt_end = dt.datetime(2012, 10, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    x = np.array(range(len(ldt_timestamps)))

    ls_symbols = ['SINE_FAST', 'SINE_SLOW', 'SINE_FAST_NOISE', 'SINE_SLOW_NOISE']
    sine_fast = 10*np.sin(x/10.) + 100
    sine_slow = 10*np.sin(x/30.) + 100

    sine_fast_noise = 10*(np.sin(x/10.) + np.random.randn(x.size)) + 100
    sine_slow_noise = 10*(np.sin(x/30.) + np.random.randn(x.size)) + 100

    d_data = dict(zip(ls_symbols, [sine_fast, sine_slow, sine_fast_noise, sine_slow_noise]))

    write(ls_symbols, d_data, ldt_timestamps)

    plt.clf()
    plt.plot(ldt_timestamps, sine_fast)
    plt.plot(ldt_timestamps, sine_slow)
    plt.plot(ldt_timestamps, sine_fast_noise)
    plt.plot(ldt_timestamps, sine_slow_noise)
    plt.ylim(50,150)
    plt.xticks(size='xx-small')
    plt.legend(ls_symbols, loc='best')
    plt.savefig('test.png',format='png')


if __name__ == '__main__':
    main()
