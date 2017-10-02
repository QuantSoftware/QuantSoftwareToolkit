import random
def gendata(N,d,bounds,clsses,fname):
	outf = open(fname,'w')
	for i in range(N):
		pnt = [None,]*(d+1)
		for x in range(d):
			pnt[x] = random.uniform(bounds[x][0],bounds[x][1])
		pnt[d] = random.choice(clsses)
		outf.write(", ".join(map(str,pnt))+"\n")
	outf.close()
def gensingle(d,bounds,clsses):
	pnt = [None,]*(d+1)
	for x in range(d):
		pnt[x] = random.uniform(bounds[x][0],bounds[x][1])
	pnt[d] = random.choice(clsses)
	return pnt
