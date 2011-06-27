import math,random,sys
import numpy

def calcalpha(stateprior,transition,emission,observations,numstates,elem_size=numpy.longdouble):
	alpha = numpy.zeros((len(observations),numstates),dtype=elem_size)
	for x in xrange(numstates):
		alpha[0][x] = stateprior[x]*emission[x][observations[0]]
	for t in xrange(1,len(observations)):
		for j in xrange(numstates):
			for i in xrange(numstates):
				alpha[t][j] += alpha[t-1][i]*transition[i][j]
			alpha[t][j] *= emission[j][observations[t]]
	return alpha

def forward(stateprior,transition,emission,observations,numstates,elem_size=numpy.longdouble):
	#returns the probability of a sequence given a model
	alpha = calcalpha(stateprior,transition,emission,observations,numstates,elem_size)
	return sum(alpha[-1])

def calcbeta(transition,emission,observations,numstates,elem_size=numpy.longdouble):
	beta = numpy.zeros((len(observations),numstates),dtype=elem_size)
	for s in xrange(numstates):
		beta[len(observations)-1][s] = 1.
	for t in xrange(len(observations)-2,-1,-1):
		for i in xrange(numstates):
			for j in xrange(numstates):
				beta[t][i] += transition[i][j]*emission[j][observations[t+1]]*beta[t+1][j]
	return beta

def calcxi(stateprior,transition,emission,observations,numstates,alpha=None,beta=None,elem_size=numpy.longdouble):
	if alpha is None:
		alpha = calcalpha(stateprior,transition,emission,observations,numstates,elem_size)
	if beta is None:
		beta = calcbeta(transition,emission,observations,numstates,elem_size)
	xi = numpy.zeros((len(observations),numstates,numstates),dtype=elem_size)
	for t in xrange(len(observations)-1):
		denom = 0.0
		for i in xrange(numstates):
			for j in xrange(numstates):
				thing = 1.0
				thing *= alpha[t][i]
				thing *= transition[i][j]
				thing *= emission[j][observations[t+1]]
				thing *= beta[t+1][j]
				denom += thing
		for i in xrange(numstates):
			for j in xrange(numstates):
				numer = 1.0
				numer *= alpha[t][i]
				numer *= transition[i][j]
				numer *= emission[j][observations[t+1]]
				numer *= beta[t+1][j]
				xi[t][i][j] = numer/denom
	return xi

def calcgamma(xi,seqlen,numstates, elem_size=numpy.longdouble):
	gamma = numpy.zeros((seqlen,numstates),dtype=elem_size)
	for t in xrange(seqlen):
		for i in xrange(numstates):
			gamma[t][i] = sum(xi[t][i])
	return gamma

def baumwelchstep(stateprior,transition,emission,observations,numstates,numsym,elem_size=numpy.longdouble):
	xi = calcxi(stateprior,transition,emission,observations,numstates,elem_size=elem_size)
	gamma = calcgamma(xi,len(observations),numstates,elem_size)
	newprior = gamma[0]
	newtrans = numpy.zeros((numstates,numstates),dtype=elem_size)
	for i in xrange(numstates):
		for j in xrange(numstates):
			numer = 0.0
			denom = 0.0
			for t in xrange(len(observations)-1):
				numer += xi[t][i][j]
				denom += gamma[t][i]
			newtrans[i][j] = numer/denom
	newemiss = numpy.zeros( (numstates,numsym) ,dtype=elem_size)
	for j in xrange(numstates):
		for k in xrange(numsym):
			numer = 0.0
			denom = 0.0
			for t in xrange(len(observations)):
				if observations[t] == k:
					numer += gamma[t][j]
				denom += gamma[t][j]
			newemiss[j][k] = numer/denom
	return newprior,newtrans,newemiss

class HMMLearner:
	def __init__(self,num_states,num_symbols,init_type='uniform',precision=numpy.longdouble):
		self.num_states = num_states
		self.num_symbols = num_symbols
		self.precision = precision
		self.reset(init_type=init_type)
	
	def reset(self, init_type='uniform'):
		if init_type == 'uniform':
			self.prior = numpy.ones( (self.num_states), dtype=self.precision) *(1.0/self.num_states)
			self.transition_matrix = numpy.ones( (self.num_states,self.num_states), dtype=self.precision)*(1.0/self.num_states)
			self.emission_matrix = numpy.ones( (self.num_states,self.num_symbols), dtype=self.precision)*(1.0/self.num_symbols)
	
	def sequenceProb(self, newData):
		if len(newData.shape) == 1:
			return forward(	self.prior,\
							self.transition_matrix,\
							self.emission_matrix,\
							newData,\
							self.num_states,\
							self.precision)
		elif len(newData.shape) == 2:
			return [forward(self.prior,self.transition_matrix,self.emission_matrix,newSeq,self.num_states,self.precision) for newSeq in newData]

	def addEvidence(self, newData, iterations=1,epsilon=0.0):
		if len(newData.shape) == 1:
			for i in xrange(iterations):
				newp,newt,newe = baumwelchstep(	self.prior, \
												self.transition_matrix, \
												self.emission_matrix, \
												newData, \
												self.num_states, \
												self.num_symbols,\
												self.precision)
				pdiff = sum([abs(np-op) for np in newp for op in self.prior])
				tdiff = sum([sum([abs(nt-ot) for nt in newti for ot in oldt]) for newti in newt for oldt in self.transition_matrix])
				ediff = sum([sum([abs(ne-oe) for ne in newei for oe in olde]) for newei in newe for olde in self.emission_matrix])
				if(pdiff < epsilon) and (tdiff < epsilon) and (ediff < epsilon):
					break
				self.prior = newp
				self.transition_matrix = newt
				self.emission_matrix = newe
		else:
			for i in xrange(iterations):
				for sequence in newData:
					newp,newt,newe = baumwelchstep(	self.prior, \
													self.transition_matrix, \
													self.emission_matrix, \
													sequence, \
													self.num_states, \
													self.num_symbols,\
													self.precision)
					self.prior = newp
					self.transition_matrix = newt
					self.emission_matrix = newe
				pdiff = sum([abs(np-op) for np in newp for op in self.prior])
				tdiff = sum([sum([abs(nt-ot) for nt in newti for ot in oldt]) for newti in newt for oldt in self.transition_matrix])
				ediff = sum([sum([abs(ne-oe) for ne in newei for oe in olde]) for newei in newe for olde in self.emission_matrix])
				if(pdiff < eps) and (tdiff < eps) and (ediff < eps):
					break
				self.prior = newp
				self.transition_matrix = newt
				self.emission_matrix = newe

def test():
	#an unfair coinflip, simpler than unfair casino
	#symbols: 0 = heads, 1 = tails
	#states: 0 = fair coin, 1 = heads weighted coin
	stateprior = (0.8,0.2)
	transition = ((0.9,0.1),(0.3,0.7))
	emission = ((0.5,0.5),(0.9,0.1))
	ob1 = (0,1,0,1,0,1,0,1,0,1,0,1)
	ob2 = (0,0,0,0,0,0,1,1,1,1,1,1)
	ob3 = (1,1,1,1,1,1,1,1,1,1,1,1)
	ob4 = (0,0,0,0,0,0,0,0,0,0,0,0)
	print "Pr(",ob1,") = ",forward(stateprior,transition,emission,ob1,2)
	print "Pr(",ob2,") = ",forward(stateprior,transition,emission,ob2,2)
	print "Pr(",ob3,") = ",forward(stateprior,transition,emission,ob3,2)
	print "Pr(",ob4,") = ",forward(stateprior,transition,emission,ob4,2)
	print
	xi = calcxi(stateprior,transition,emission,ob2,2)
	gamma = calcgamma(xi,len(ob2),2)
	for t in xrange(len(ob2)):
		print gamma[t]
	print
	ob5 = (0,1,2,3,0,1,2,3,0,1,2,3)
	print "Doing Baum-welch"
	my_hmm = HMMLearner(2,2)
	my_hmm.addEvidence(numpy.array(ob3*10),100)
	print "Prior",my_hmm.prior
	print "Transition",my_hmm.transition_matrix
	print "Emission", my_hmm.emission_matrix
	
	
if __name__=="__main__":
	test()
