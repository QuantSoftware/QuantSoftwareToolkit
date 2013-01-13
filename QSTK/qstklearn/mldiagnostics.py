# (c) 2011, 2012 Georgia Tech Research Corporation
# This source code is released under the New BSD license.  Please see
# http://wiki.quantsoftware.org/index.php?title=QSTK_License
# for license details.
#
# Created on Month day, Year
#
# @author: Vishal Shekhar
# @contact: mailvishalshekhar@gmail.com
# @summary: ML Algo Diagnostic Utility (plots performance of the Algo on Train Vs CV sets)
#

import copy
import numpy as np
import matplotlib.pyplot as plt
from pylab import *

class MLDiagnostics:
	"""
	This class can be used to produce learning curves.
	These are plots of evolution of Training Error and Cross Validation Error across lambda(in general a control param for model complexity).
	This plot can help diagnose if the ML algorithmic model has high bias or a high variance problem and can
	thus help decide the next course of action.
	In general, ML Algorithm is of the form,
		Y=f(t,X) + lambdaVal*|t|
		where Y is the output, t is the model parameter vector, lambdaVal is the regularization parameter.
		|t| is the size of model parameter vector.
	"""
	def __init__(self,learner,Xtrain,Ytrain,Xcv,Ycv,lambdaArray):
		self.learner = learner
		self.Xtrain = Xtrain
		self.Ytrain = Ytrain
		self.Xcv = Xcv
		self.Ycv = Ycv
		self.lambdaArray = lambdaArray
		self.ErrTrain = np.zeros((len(lambdaArray),1))
		self.ErrCV = copy.copy(self.ErrTrain)

	def avgsqerror(self,Y,Ypred):
		return np.sum((Y-Ypred)**2)/len(Y)
	
	def plotCurves(self,filename):
		Xrange = [i*self.step for i in range(1,len(self.ErrTrain)+1)]
		plt.plot(Xrange,self.ErrTrain,label = "Train Error")
		plt.plot(Xrange,self.ErrCV,label="CV Error")
		plt.title('Learning Curves')
		plt.xlabel('# of Training Examples')
		plt.ylabel('Average Error')
		plt.draw()
		savefig(filename,format='pdf')

	def runDiagnostics(self,filename):
		for i,lambdaVal in zip(range(len(self.lambdaArray)),self.lambdaArray):
			learner = copy.copy(self.learner())# is deep copy required
			# setLambda needs to be a supported function for all ML strategies.
			learner.setLambda(lambdaVal)
			learner.addEvidence(self.Xtrain,self.Ytrain)
			YtrPred = learner.query(self.Xtrain)
			self.ErrTrain[i] = self.avgsqerror(self.Ytrain,YtrPred)
			YcvPred = learner.query(self.Xcv)
			self.ErrCV[i] = self.avgsqerror(self.Ycv,YcvPred)
		self.plotCurves(filename)
