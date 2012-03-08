'''
Created on Nov 7, 2011

@author: John Cornwell
@contact: JohnWCornwellV@gmail.com
@summary: File containing various classification functions

'''

''' 3rd Party Imports '''
import pandas as pand
import numpy as np

def classFutRet( dData, lLookforward=21, sRel=None, bUseOpen=False ):
	'''
	@summary: Calculate classification, uses future returns 
	@param dData: Dictionary of data to use
	@param lLookforward: Number of days to look in the future
	@param sRel: Stock symbol that this should be relative to, ususally $SPX.
	@param bUseOpen: If True, stock will be purchased at T+1 open, sold at T+lLookforawrd close
	@return: DataFrame containing values
	'''
	
	dfClose = dData['close']
	
	''' Class DataFrame will be 1:1, we can use the price as a template, need to copy values '''
	dfRet = pand.DataFrame( index=dfClose.index, columns=dfClose.columns, data=np.copy(dfClose.values) ) 
	
	''' If we want market relative, calculate those values now '''
	if not sRel == None:
		lLen = len(dfClose[sRel].index)
		''' Loop over time '''
		for i in range(lLen):
			
			if i + lLookforward >= lLen:
				dfRet[sRel][i] = float('nan')
				continue
			
			''' We either buy on todays close or tomorrows open '''
			if bUseOpen:
				dfOpen = dData['open']
				fBuy = dfOpen[sRel][i+1]
			else:
				fBuy = dfRet[sRel][i]
				
				
			dfRet[sRel][i] = (dfRet[sRel][i+lLookforward] - fBuy) / fBuy
	
	''' Loop through stocks '''
	for sStock in dfClose.columns:
		
		''' We have already done this stock '''
		if sStock == sRel:
			continue
		
		lLen = len(dfClose[sStock].index)
		''' Loop over time '''
		for i in range(lLen):
			
			if i + lLookforward >= lLen:
				dfRet[sStock][i] = float('nan')
				continue
			
			''' We either buy on todays close or tomorrows open '''
			if len( dfOpen.index ) == 0:
				fBuy = dfRet[sStock][i]
			else:
				fBuy = dfOpen[sStock][i+1]
			
			dfRet[sStock][i] = (dfRet[sStock][i+lLookforward] - fBuy) / fBuy
			
			''' Make market relative '''
			if not sRel == None:
				dfRet[sStock][i] -= dfRet[sRel][i]
			
	return dfRet
		

if __name__ == '__main__':
	pass
