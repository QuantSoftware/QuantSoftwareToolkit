'''
Created on Oct 7, 2010

@author: Tucker Balch
@contact: tucker@cc.@gatech.edu
'''

import os
import pandas as pandas
from qstkutil import DataAccess as da
from qstkutil import timeutil as tu

__version__ = "$Revision: 156 $"

def getDataMatrixFromData(dataname,partname,symbols,tsstart,tsend):
	pathpre = os.environ.get('QSDATA') + "/Processed"
	if dataname == "Norgate":
		pathsub = "/Norgate/Equities"
		paths=list()
		paths.append(pathpre + pathsub + "/US_NASDAQ/")
		paths.append(pathpre + pathsub + "/US_NYSE/")
		paths.append(pathpre + pathsub + "/US_NYSE Arca/")
		paths.append(pathpre + pathsub + "/OTC/")
		datastr1 = "/StrategyData"
		datastr2 = "StrategyData"
	else:
		raise Exception("unknown dataname " + str(dataname))

	data = da.DataAccess(True, paths, datastr1, datastr2,
       		False, symbols, tsstart, tsend)
	tss = list(data.getTimestampArray())
	start_time = tss[0]
	end_time = tss[-1]
	dates = []
	for ts in tss:
		dates.append(tu.epoch2date(ts))
	vals = data.getMatrixBetweenTS(symbols,partname,
		start_time,end_time)
	syms = list(data.getListOfSymbols())
	del data

	return(pandas.DataMatrix(vals,dates,syms))
# end getTSFromData
