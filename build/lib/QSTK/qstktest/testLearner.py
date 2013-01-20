#
# How to plot 2D data for learning
#
# by Tucker Balch
# September 2010
#

#
# imports
#
import numpy as np
import matplotlib.pyplot as plt
import QSTK.qstklearn.kdtknn as kdt
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
import datetime as dt

#
# Choose colors
#
def findcolors(Y):
	miny = min(Y)
	maxy = max(Y)
	tY = (Y-miny)/(maxy-miny)
	colors =[]
	for i in tY:
		if (i>0.66):
			j = min(1,(i-.66)*3)
			colors.append([1,(1-j),0])
		elif (i<=.66) and (i>.33):
			j = (i-.33)*3
			colors.append([j,1,0])
		else:
			j = i*3
			colors.append([0,j,1])
		#print i,j
	return colors

def main():
	#
	# read in and slice up the data
	#
	#data = np.loadtxt('data-classification-prob.csv',delimiter=',',skiprows=1)
	data = np.loadtxt('data-ripple-prob.csv',delimiter=',',skiprows=1)
	X1 = data[:,0]
	X2 = data[:,1]
	Y  = data[:,2]
	colors = findcolors(Y)
	
	#
	# scatter plot X1 vs X2 and colors are Y
	#
	plt.clf()
	fig = plt.figure()
	fig1 = fig.add_subplot(221)
	plt.scatter(X1,X2,c=colors,edgecolors='none')
	plt.xlabel('X1')
	plt.ylabel('X2')
	plt.xlim(-1,1)	# set x scale
	plt.ylim(-1,1)	# set y scale
	plt.title('Training Data 2D View',fontsize=12)
	
	# plot the 3d view
	ax = fig.add_subplot(222,projection='3d')
	ax.scatter(X1,X2,Y,c=colors,edgecolors='none')
	#ax.scatter(X1,X2,Y,c=colors)
	ax.set_xlabel('X1')
	ax.set_ylabel('X2')
	ax.set_zlabel('Y')
	ax.set_xlim3d(-1,1)
	ax.set_ylim3d(-1,1)
	ax.set_zlim3d(-1,1)
	plt.title('Training Data 3D View',fontsize=12)
	
	##########
	# OK, now create and train a learner
	#
	learner = kdt.kdtknn(k=30,method='mean')
	numpoints = X1.shape[0]
	dataX = np.zeros([numpoints,2])
	dataX[:,0] = X1
	dataX[:,1] = X2
	
	trainsize = floor(dataX.shape[0] * .6)
	learner.addEvidence(dataX[0:trainsize],dataY=Y[0:trainsize])
	steps = 50.0
	stepsize = 2.0/steps
	
	Xtest = np.zeros([steps*steps,2])
	count = 0
	for i in np.arange(-1,1,stepsize):
		for j in np.arange(-1,1,stepsize):
			Xtest[count,0] = i + stepsize/2
			Xtest[count,1] = j + stepsize/2
			count = count+1
	Ytest = learner.query(Xtest) # to check every point
	
	#
	# Choose colors
	#
	colors = findcolors(Ytest)
	
	#
	# scatter plot X1 vs X2 and colors are Y
	#
	fig1 = fig.add_subplot(223)
	plt.scatter(Xtest[:,0],Xtest[:,1],c=colors,edgecolors='none')
	plt.xlabel('X1')
	plt.ylabel('X2')
	plt.xlim(-1,1)	# set x scale
	plt.ylim(-1,1)	# set y scale
	plt.title('Learned Model 2D',fontsize=12)
	
	# plot the 3d view
	ax = fig.add_subplot(224,projection='3d')
	ax.scatter(Xtest[:,0],Xtest[:,1],Ytest,c=colors,edgecolors='none')
	#X1 = Xtest[:,0]
	#X2 = Xtest[:,1]
	#X1 = np.reshape(X1,(steps,steps))
	#X2 = np.reshape(X2,(steps,steps))
	#Ytest = np.reshape(Ytest,(steps,steps))
	ax.set_xlabel('X1')
	ax.set_ylabel('X2')
	ax.set_zlabel('Y')
	ax.set_xlim3d(-1,1)
	ax.set_ylim3d(-1,1)
	ax.set_zlim3d(-1,1)
	plt.title('Learned Model 3D',fontsize=12)
	savefig("scatterdata3D.png", format='png')
	plt.close()
	
	#
	# Compare to ground truth
	#
	print 'trainsize ' + str(trainsize)
	Ytruth = Y[-trainsize:]
	print 'Ytruth.shape ' + str(Ytruth.shape)
	Xtest = dataX[-trainsize:,:]
	print 'Xtest.shape ' + str(Xtest.shape)
	Ytest = learner.query(Xtest) # to check every point
	print 'Ytest.shape ' + str(Ytest.shape)
	
	plt.clf()
	plt.scatter(Ytruth,Ytest,edgecolors='none')
	plt.xlim(-1.2,1.2)	# set x scale
	plt.ylim(-1.2,1.2)	# set y scale
	plt.xlabel('Ground Truth')
	plt.ylabel('Estimated')
	savefig("scatterdata.png", format='png')
	
	print corrcoef(Ytruth,Ytest)

if __name__ == '__main__':
	main()
