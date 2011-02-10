import cPickle

fund_file=fopen(sys.argv[0],'rb')
funds=cPickle.load(fund_file)

plt.plot(funds.index, funds.values)

