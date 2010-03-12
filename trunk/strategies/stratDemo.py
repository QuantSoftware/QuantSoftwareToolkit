import random


# Rudimentary proof-of-concept strategy; takes in a 'portfolio' that is a two-element list; first is a float
# (cash on hand) and second is a list of stocks, organized as follows:
# [$$$$$, [ [symbol, shares], [symbol, shares], [symbol, shares],...] ]

# Note: actual portfolio will be OO


# This demo strategy prints out the current amount of money in the portfolio and adds a random amount 
# (up to 1000) to it, then prints the stocks and volume owned
def myStrategy(portfolio):
    print "This is a strategy."
    rndAdd = random.randint(0,1000)
    print "Currently, you have %f monies.  Adding %d." % (portfolio[0],rndAdd)
    portfolio[0] += rndAdd
    print "Stocks owned:"
    if len(portfolio[1]) == 0:
        print "\tNone"
    else:
        for i in portfolio[1]:
            print "\tCompany: %s\n\t\tShares: %d" % (i[0],i[1])