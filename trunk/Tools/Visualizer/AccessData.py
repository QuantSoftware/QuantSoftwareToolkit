#created by Sourabh Bajaj
#email: sourabhbajaj90@gmail.com

#import libraries
import numpy as np
import time
import qstkutil.dateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import qstkfeat.featutil as feat
import datetime as dt
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
from pandas import *


# Changes made in the featutil file are : Edited the getFeatureFuncs()


def ReadData(DataFile='AllData', TimeTag='TimeStamps.txt', IDTag='Symbols.csv', FactorTag='Features.csv'):

	#Reading the timestamps from a text file.
	timestamps=[]
	file = open(TimeTag, 'r')
	for onedate in file.readlines():
		timestamps.append(dt.datetime.strptime(onedate, "%Y-%m-%d\n"))
	file.close()

	# Reading the ID Tag
	symbols=np.loadtxt(IDTag,dtype='S5',comments='#',skiprows=1,)

	# Reading the Data Values
	Numpyarray=pickle.load(open( DataFile, 'rb' ))
	
	for i in range(0,len(Numpyarray)):
		tsu.fillforward(Numpyarray[i])
		tsu.fillbackward(Numpyarray[i])

	# Reading the Factor Tags
	featureslist= np.loadtxt(FactorTag,dtype='S',comments='#',skiprows=1,)

	PandasObject= Panel(Numpyarray, items=featureslist, major_axis=timestamps, minor_axis=symbols)

	return (PandasObject, featureslist, symbols, timestamps)

def DataParameter(PandasObject, featureslist, symbols, timestamps):
	
	startday=timestamps[0]
	endday=timestamps[-1]
	MinFeat=[]
	MaxFeat=[]

	for feature in featureslist:
		MinFeat.append(np.amin(np.min(PandasObject[feature], axis=0)))
		MaxFeat.append(np.amax(np.max(PandasObject[feature], axis=0)))

	dMinFeat=dict(zip(featureslist, MinFeat))
	dMaxFeat=dict(zip(featureslist, MaxFeat))
	
	return(dMinFeat, dMaxFeat, startday, endday)

def inrange(x, minx, maxx):
	if x>minx and x<maxx: return x
	else: return np.NAN

def scale(x, minx, maxx):
	if x>maxx: print x
	return (599*((x-minx)/(maxx-minx))+10)

def PlotParam(PandasObject, dayofplot, XFeat,XMin, XMax, YFeat,YMin, YMax, ZFeat,ZMin, ZMax, SizeFeat, smin, smax, ColorFeat):

	xs=PandasObject[XFeat].xs(dayofplot)
	ys=PandasObject[YFeat].xs(dayofplot)
	zs=PandasObject[ZFeat].xs(dayofplot)
	print xs
	print XMax
	print XMin
	
	size=PandasObject[SizeFeat].xs(dayofplot)
	color=PandasObject[SizeFeat].xs(dayofplot)
	
	xs1 = [inrange(x, XMin, XMax) for x in xs]
	ys1 = [inrange(y, YMin, YMax) for y in ys]
	zs1 = [inrange(z, ZMin, ZMax) for z in zs]

	s1= [scale(s, smin, smax) for s in size]

	fig = figure()
	ax = fig.gca(projection='3d')

	ax.scatter(xs1,ys1,zs1,marker='o', alpha=0.5, c=s1, s=s1)

	ax.set_xlim(XMin, XMax)
	ax.set_ylim(YMin, YMax)
	ax.set_zlim(ZMin, ZMax)	
	
	ax.set_xlabel(XFeat)
	ax.set_ylabel(YFeat)
	ax.set_zlabel(ZFeat)

	plt.show()

def main():
	(PandasObject, featureslist, symbols, timestamps)=ReadData()
	(dMinFeat, dMaxFeat, startday, endday)=DataParameter(PandasObject, featureslist, symbols, timestamps)
	PlotParam(PandasObject, timestamps[16], featureslist[2], dMinFeat[featureslist[2]], dMaxFeat[featureslist[2]], featureslist[8], dMinFeat[featureslist[8]], dMaxFeat[featureslist[8]],featureslist[9], dMinFeat[featureslist[9]], dMaxFeat[featureslist[9]], featureslist[0],dMinFeat[featureslist[0]], dMaxFeat[featureslist[0]], featureslist[5])
	
if __name__ == '__main__':
	main()

