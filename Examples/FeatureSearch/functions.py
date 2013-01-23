''' Python imports '''
import datetime as dt

''' 3rd party imports '''
import numpy as np
import pandas as pand
import matplotlib.pyplot as plt

''' QSTK imports '''
from QSTK.qstkutil import DataAccess as da
from QSTK.qstkutil import qsdateutil as du

from QSTK.qstkfeat.features import featMA, featRSI, featDrawDown, featRunUp, featVolumeDelta, featAroon
from QSTK.qstkfeat.classes import class_fut_ret
import QSTK.qstkfeat.featutil as ftu	
	
import sys

MAX_ITERATIONS = 500
	
def learnerTest( naTrain, naTest ):
	#create the learner with the train set with K=5
	cLearn = ftu.createKnnLearner( naTrain, lKnn=5 )
	#get the Y values predicted by the learner
	Ypredicted = cLearn.query( naTest[:,:-1] )
	#get the actual Y values
	Y = naTest[:,-1]
	#calculate the correlation coefficient
	corrcoef = np.corrcoef(Y,Ypredicted)[0][1]
	#return the corrcoef
	return corrcoef	

def nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex):
	sys.stdout.write('nextBestFeature\n')
	
	bestFeature = -1
	bestFeatureCorrCoef = 0
	for x in lRemainingFeatures:
		lCurrentFeatureSet = [x]+lSelectedFeatures+[classLabelIndex]
		sys.stdout.write('testing feature set ' +  str(lCurrentFeatureSet))
		currentTrain = naFeatTrain[:,lCurrentFeatureSet]
		currentTest = naFeatTest[:,lCurrentFeatureSet]
		currentCorrCoef = learnerTest(currentTrain,currentTest)
		sys.stdout.write(' :: corr coef = ' + str(currentCorrCoef) + '\n')
		if bestFeature == -1 or bestFeatureCorrCoef < currentCorrCoef:
			bestFeature = x
			bestFeatureCorrCoef = currentCorrCoef
			
	sys.stdout.write('nextBestFeature: ' + str(bestFeature) + '\n')
	sys.stdout.write('bestFeatureCorrCoef: ' + str(bestFeatureCorrCoef) + '\n\n')
	return {'bestFeature':bestFeature,'bestFeatureCorrCoef':bestFeatureCorrCoef}
			
def nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex):
	sys.stdout.write('nextWorstFeature\n')

	if len(lSelectedFeatures) == 1:
		sys.stdout.write('nextWorstFeature: ' + str(lSelectedFeatures[0]) + '\n')
		sys.stdout.write('worstFeatureCorrCoef: ' + str(-999) + '\n\n')
		return {'worstFeature':lSelectedFeatures[0],'worstFeatureCorrCoef':-999}

	worstFeature = -1
	worstFeatureCorrCoef = 0
	for x in lSelectedFeatures:
		lSelectedFeaturesCopy = lSelectedFeatures[:]
		lSelectedFeaturesCopy.remove(x);			
		lCurrentFeatureSet = lSelectedFeaturesCopy + [classLabelIndex]
		sys.stdout.write('testing feature set ' +  str(lCurrentFeatureSet))
		currentTrain = naFeatTrain[:,lCurrentFeatureSet]
		currentTest = naFeatTest[:,lCurrentFeatureSet]
		currentCorrCoef = learnerTest(currentTrain,currentTest)
		sys.stdout.write(' :: corr coef = ' + str(currentCorrCoef) + '\n')
		if worstFeature == -1 or worstFeatureCorrCoef < currentCorrCoef:
			worstFeature = x
			worstFeatureCorrCoef = currentCorrCoef
			
	sys.stdout.write('nextWorstFeature: ' + str(worstFeature) + '\n')
	sys.stdout.write('worstFeatureCorrCoef: ' + str(worstFeatureCorrCoef) + '\n\n')
	return {'worstFeature':worstFeature,'worstFeatureCorrCoef':worstFeatureCorrCoef}

def sequentialForwardSelection(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	lSelectedFeatures = list()
	lRemainingFeatures = lFeatures[:]
	lCorrCoef = list();
	while len(lRemainingFeatures) > 0:
		sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
		sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
		sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
		retValue = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
		lSelectedFeatures.append(retValue['bestFeature'])
		lRemainingFeatures.remove(retValue['bestFeature'])
		lCorrCoef.append(retValue['bestFeatureCorrCoef'])
		
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(lSelectedFeatures[0:maxlCorrCoefIndex+1]+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef

def sequentialBackwardSelection(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	lSelectedFeatures = lFeatures[:]
	lCorrCoef = list()
	lRemovedFeatures = list()
	while len(lSelectedFeatures) > 0:
		sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
		sys.stdout.write('lRemovedFeatures: ' + str(lRemovedFeatures) + '\n')
		sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
		retValue = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
		lSelectedFeatures.remove(retValue['worstFeature'])
		lCorrCoef.append(retValue['worstFeatureCorrCoef'])
		lRemovedFeatures.append(retValue['worstFeature'])
		
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	lBestSet = list(set(lFeatures) - set(lRemovedFeatures[0:maxlCorrCoefIndex+1]))
	sys.stdout.write('best feature set is ' + str(lBestSet+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef

def sequentialFloatingForwardSelection(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = list()
	lRemainingFeatures = lFeatures[:]
	lCorrCoef = list()
	lSeenStates = list()
	while len(lRemainingFeatures) > 0:
		sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
		sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
		sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
		retValue = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
		lSelectedFeatures.append(retValue['bestFeature'])
		lSeenStates.append(set(lSelectedFeatures))
		lRemainingFeatures.remove(retValue['bestFeature'])
		lCorrCoef.append(retValue['bestFeatureCorrCoef'])
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
			if lCorrCoef[-1] < retValue2['worstFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.remove(retValue2['worstFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not removed b/c state already seen. \n\n')
					break
				lSelectedFeatures.remove(retValue2['worstFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.append(retValue2['worstFeature'])
				lCorrCoef.append(retValue2['worstFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not removed b/c corr not higher. \n\n')
				break
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef
	
def sequentialFloatingBackwardSelection(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = lFeatures[:]
	lRemainingFeatures = list()
	lCorrCoef = list()
	lSeenStates = list()
	while len(lSelectedFeatures) > 0:
		sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
		sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
		sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
		retValue = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
		lSelectedFeatures.remove(retValue['worstFeature'])
		lSeenStates.append(set(lSelectedFeatures))
		lRemainingFeatures.append(retValue['worstFeature'])
		lCorrCoef.append(retValue['worstFeatureCorrCoef'])
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
			if lCorrCoef[-1] < retValue2['bestFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.add(retValue2['bestFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not added b/c state already seen. \n\n')
					break
				lSelectedFeatures.append(retValue2['bestFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.remove(retValue2['bestFeature'])
				lCorrCoef.append(retValue2['bestFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not added b/c corr not higher. \n\n')
				break
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef
	
def sequentialFloatingForwardSelectionNew(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = list()
	lRemainingFeatures = lFeatures[:]
	lCorrCoef = list()
	lSeenStates = list()
	
	retValue = 0
	while len(lRemainingFeatures) > 0:
		change = False
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
			if len(lCorrCoef)==0 or lCorrCoef[-1] < retValue['bestFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.add(retValue['bestFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not added b/c state already seen. \n\n')
					break
				lSelectedFeatures.append(retValue['bestFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.remove(retValue['bestFeature'])
				lCorrCoef.append(retValue['bestFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not added b/c corr not higher. \n\n')
				break
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
			if lCorrCoef[-1] < retValue2['worstFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.remove(retValue2['worstFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not removed b/c state already seen. \n\n')
					break
				lSelectedFeatures.remove(retValue2['worstFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.append(retValue2['worstFeature'])
				lCorrCoef.append(retValue2['worstFeatureCorrCoef'])
				change = True
			else:
				sys.stdout.write('feature not removed b/c corr not higher. \n\n')
				break
		if not change:
			lSelectedFeatures.append(retValue['bestFeature'])
			lSeenStates.append(set(lSelectedFeatures))
			lRemainingFeatures.remove(retValue['bestFeature'])
			lCorrCoef.append(retValue['bestFeatureCorrCoef'])
			sys.stdout.write('feature added b/c no features were removed. \n\n')
			
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef

def sequentialFloatingBackwardSelectionNew(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = lFeatures[:]
	lRemainingFeatures = list()
	lCorrCoef = list()
	lSeenStates = list()
	
	retValue = 0
	while len(lSelectedFeatures) > 0:
		change = False
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
			if len(lCorrCoef)==0 or lCorrCoef[-1] < retValue['worstFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.remove(retValue['worstFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not removed b/c state already seen. \n\n')
					break
				lSelectedFeatures.remove(retValue['worstFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.append(retValue['worstFeature'])
				lCorrCoef.append(retValue['worstFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not removed b/c corr not higher. \n\n')
				break
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
			if lCorrCoef[-1] < retValue2['bestFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.add(retValue2['bestFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not added b/c state already seen. \n\n')
					break
				lSelectedFeatures.append(retValue2['bestFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.remove(retValue2['bestFeature'])
				lCorrCoef.append(retValue2['bestFeatureCorrCoef'])
				change = True
			else:
				sys.stdout.write('feature not added b/c corr not higher. \n\n')
				break
		if not change:
			lSelectedFeatures.remove(retValue['worstFeature'])
			lSeenStates.append(set(lSelectedFeatures))
			lRemainingFeatures.append(retValue['worstFeature'])
			lCorrCoef.append(retValue['worstFeatureCorrCoef'])
			sys.stdout.write('feature removed b/c no features were added. \n\n')
			
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef
	
def sequentialFloatingForwardSelectionNew_Max(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = list()
	lRemainingFeatures = lFeatures[:]
	lCorrCoef = list()
	lSeenStates = list()
	maxCorrCoef = -100
	
	retValue = 0
	while len(lRemainingFeatures) > 0:
		change = False
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
			if len(lCorrCoef)==0 or maxCorrCoef < retValue['bestFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.add(retValue['bestFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not added b/c state already seen. \n\n')
					break
				lSelectedFeatures.append(retValue['bestFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.remove(retValue['bestFeature'])
				lCorrCoef.append(retValue['bestFeatureCorrCoef'])
				maxCorrCoef = max(maxCorrCoef,retValue['bestFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not added b/c corr not higher. \n\n')
				break
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
			if maxCorrCoef < retValue2['worstFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.remove(retValue2['worstFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not removed b/c state already seen. \n\n')
					break
				lSelectedFeatures.remove(retValue2['worstFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.append(retValue2['worstFeature'])
				lCorrCoef.append(retValue2['worstFeatureCorrCoef'])
				maxCorrCoef = max(maxCorrCoef,retValue2['worstFeatureCorrCoef'])
				change = True
			else:
				sys.stdout.write('feature not removed b/c corr not higher. \n\n')
				break
		if not change:
			lSelectedFeatures.append(retValue['bestFeature'])
			lSeenStates.append(set(lSelectedFeatures))
			lRemainingFeatures.remove(retValue['bestFeature'])
			lCorrCoef.append(retValue['bestFeatureCorrCoef'])
			maxCorrCoef = max(maxCorrCoef,retValue['bestFeatureCorrCoef'])
			sys.stdout.write('feature added b/c no features were removed. \n\n')
			
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef

def sequentialFloatingBackwardSelectionNew_Max(naFeatTrain,naFeatTest,lFeatures,classLabelIndex):
	global MAX_ITERATIONS
	lSelectedFeatures = lFeatures[:]
	lRemainingFeatures = list()
	lCorrCoef = list()
	lSeenStates = list()
	maxCorrCoef = -100
	
	retValue = 0
	while len(lSelectedFeatures) > 0:
		change = False
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue = nextWorstFeature(naFeatTrain,naFeatTest,lSelectedFeatures,classLabelIndex)
			if len(lCorrCoef)==0 or maxCorrCoef < retValue['worstFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.remove(retValue['worstFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not removed b/c state already seen. \n\n')
					break
				lSelectedFeatures.remove(retValue['worstFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.append(retValue['worstFeature'])
				lCorrCoef.append(retValue['worstFeatureCorrCoef'])
				maxCorrCoef = max(maxCorrCoef,retValue['worstFeatureCorrCoef'])
			else:
				sys.stdout.write('feature not removed b/c corr not higher. \n\n')
				break
		while True:
			sys.stdout.write('lSelectedFeatures: ' + str(lSelectedFeatures) + '\n')
			sys.stdout.write('lRemainingFeatures: ' + str(lRemainingFeatures) + '\n')
			sys.stdout.write('lCorrCoef: ' + str(lCorrCoef) + '\n')
			retValue2 = nextBestFeature(naFeatTrain,naFeatTest,lSelectedFeatures,lRemainingFeatures,classLabelIndex)
			if maxCorrCoef < retValue2['bestFeatureCorrCoef']:
				newState = set(lSelectedFeatures)
				newState.add(retValue2['bestFeature'])
				if newState in lSeenStates:
					sys.stdout.write('feature not added b/c state already seen. \n\n')
					break
				lSelectedFeatures.append(retValue2['bestFeature'])
				lSeenStates.append(set(lSelectedFeatures))
				lRemainingFeatures.remove(retValue2['bestFeature'])
				lCorrCoef.append(retValue2['bestFeatureCorrCoef'])
				maxCorrCoef = max(maxCorrCoef,retValue2['bestFeatureCorrCoef'])
				change = True
			else:
				sys.stdout.write('feature not added b/c corr not higher. \n\n')
				break
		if not change:
			lSelectedFeatures.remove(retValue['worstFeature'])
			lSeenStates.append(set(lSelectedFeatures))
			lRemainingFeatures.append(retValue['worstFeature'])
			lCorrCoef.append(retValue['worstFeatureCorrCoef'])
			maxCorrCoef = max(maxCorrCoef,retValue['worstFeatureCorrCoef'])
			sys.stdout.write('feature removed b/c no features were added. \n\n')
	
		if len(lSeenStates) >= MAX_ITERATIONS:
			sys.stdout.write('QUITTING B/C len(lSeenStates) >= MAX_ITERATIONS: ' + str(len(lSeenStates)) + '\n\n')
			break
	
	maxlCorrCoef = max(lCorrCoef)
	maxlCorrCoefIndex = lCorrCoef.index(maxlCorrCoef)
	sys.stdout.write('best feature set is ' + str(list(lSeenStates[maxlCorrCoefIndex])+[classLabelIndex]) + '\n')
	sys.stdout.write('corr coef = ' + str(maxlCorrCoef))
	return maxlCorrCoef
