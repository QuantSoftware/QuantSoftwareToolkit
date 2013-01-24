#
# Example use of the event profiler
#
import QSTK.qstkstudy.Events as ev
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
import numpy as np

if __name__ == '__main__':

    ls_symbols = np.loadtxt('symbol-set1.txt',dtype='S10',comments='#')
    dt_start = dt.datetime(2008,1,1)
    dt_end = dt.datetime(2009,12,31)
    ldt_timestamps = du.getNYSEdays( dt_start, dt_end, dt.timedelta(hours=16) )

    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    eventMatrix = ev.find_events(ls_symbols,d_data,verbose=True)
    ep.eventprofiler(eventMatrix, d_data,
            i_lookback=20,i_lookforward=20,
            s_filename="MyEventStudy")
