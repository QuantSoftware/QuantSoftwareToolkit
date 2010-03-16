import models.PortfolioModel, models.PositionModel, models.OrderModel, models.StockPriceModel
import tables as pt
from optparse import OptionParser
import sys, time




class Simulator():
    portfolio=None; position=None; order=None; stockPrice=None
    portfolioFile=None; positionFile=None; orderFile=None; stockPriceFile=None
    def __init__(self, initialPortfolio, strategy, startTime, endTime, interval):
        # NOTE: As written currently, strategy is a method
        self.strategy = strategy
        
        self.portfolioFile = pt.openFile('PortfolioModel.h5', mode = "w")
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.orderFile = pt.openFile('OrderModel.h5', mode = "w")
        self.stockPriceFile = pt.openFile('StockPriceModel.h5', mode = "w")
        
        self.portfolio = portfolioFile.createTable('/', 'portfolio', self.PortfolioModel)
        self.position = positionFile.createTable('/', 'position', self.PositionModel)
        self.order = orderFile.createTable('/', 'order', self.OrderModel)
        self.stockPrice = stockPriceFile.createTable('/', 'stockPrice', self.StockPriceModel)
    
    def execute(self,commands):
        pass
    
    def run(self):
        currTime = startTime
        while currTime < endTime and currTime < time.time():
            self.execute(self.strategy(currtime, self.portfolio))
            currTime += timeStep
        
    def close(self):
        self.portfolioFile.close()
        self.positionFile.close()
        self.orderFile.close()
        self.stockPriceFile.close()



cash = 0; comPerShare = 0.0; minCom = 0.; startTime = 0; endTime = 0; timeStep = 0; maxEffect = 0.; decayCycles = 0
noisy = False

def main():
    global cash,comPerShare,minCom,startTime,endTime,timeStep,maxEffect,decayCycles,noisy
    # NOTE: the OptionParser class is currently not necessary, as we can just access sys.argv[1:], but if we
    # want to implement optional arguments, this will make it considerably easier.
    parser = OptionParser()
    
    # parser.parse_args() returns a tuple of (options, args)
    # As of right now, we don't have any options for our program, so we only care about the three arguments:
    # config file, strategy module name, strategy main function name
    args = parser.parse_args()[1]
    
    if len(args) != 3 and len(args) != 2:
        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING INCOMPETENT USER."
        return
    
    configFile = args[0]
    if len(args) == 3:
        stratName = args[2]
    else:
        stratName = "strategyMain"
    f = open(configFile, 'r')
    g = open("default.ini", 'r')
    
    for thisFile in [g,f]:
        for line in thisFile.readlines():
            # Separate the command in the config file from the arguments
            if not ('#' in line):
                line = line.strip().split('=')
                command = line[0].strip().upper()
                if len(line)>1:
                    vals = line[1].upper().split()
                else:
                    vals = []
                # Parse commands, look for correct number of arguments, do rudimentary error checking, apply to simulator as appropriate
                if command == 'CASH':
                    if len(vals) != 1:
                        print "WRONG NUMBER OF ARGUMENTS FOR CASH!!  RAAAAWR!"
                    else:
                        try:
                            cash = float(vals[0])
                        except ValueError:
                            print "ARGUMENT FOR CASH IS NOT A FLOAT!! RAAAWR!"
                
                # Code for handling stocks in a starting portfolio.  Implementation not correct; removing for the time being.
#                elif command == "STOCK":
#                    if len(vals) != 2:
#                        print "WRONG NUMBER OF ARGUMENTS FOR STOCK!!  RAAAAWR!  ALSO, I NEED TO LEARN TO THROW ERRORS!"
#                    else:
#                        try:
#                            stocks.append([vals[0],int(vals[1])])
#                        except:
#                            print "STOCK TAKES IN A STOCK NAME AND AN INT!  AND DON'T YOU FORGET IT!"
                elif command == "COMPERSHARE":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR COMMISSIONS PER SHARE."
                    else:
                        try:
                            comPerShare = float(vals[0])
                        except ValueError:
                            print "COMMISSIONS PER SHARE REQUIRES A FLOAT INPUT"
                elif command == "MINCOM":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR MINIMUM COMMISSION."
                    else:
                        try:
                            minCom = float(vals[0])
                        except ValueError:
                            print "MINIMUM COMMISSIONS REQUIRES A FLOAT INPUT"
                elif command == "STARTTIME":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR START TIME."
                    else:
                        try:
                            startTime = long(vals[0])
                        except ValueError:
                            print "START TIME REQUIRES A LONG INPUT"
                elif command == "ENDTIME":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR END TIME."
                    else:
                        try:
                            endTime = long(vals[0])
                        except ValueError:
                            print "END TIME REQUIRES A LONG INPUT"
                elif command == "TIMESTEP":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR TIME STEP."
                    else:
                        try:
                            timeStep = long(vals[0])
                        except ValueError:
                            print "TIME STEP REQUIRES A LONG INPUT"
                elif command == "MAXMARKETEFFECT":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR MAX MARKET EFFECT."
                    else:
                        try:
                            maxEffect = float(vals[0])
                        except ValueError:
                            print "MAX MARKET EFFECT REQUIRES A FLOAT INPUT"
                elif command == "DECAYCYCLES":
                    if len(vals) != 1:
                        print "NEED EXACTLY ONE PARAMETER FOR DECAY CYCLES."
                    else:
                        try:
                            decayCycles = int(vals[0])
                        except ValueError:
                            print "DECAY CYCLES REQUIRES AN INTEGER INPUT"
                elif command == "NOISY":
                    noisy = True
                elif command != '':
                        print "Unrecognized command '%s'.  Note: some commands may not yet be implemented.  E-mail pdohogne3@gatech.edu if a command is missing." % command
    f.close()
    g.close()
    if noisy:
        print "Config file parsed successfully.  Starting simulation."
    
    # CREATE PORTFOLIO HERE
    myPort = None
    
    # Add the strategies subdirectory to the system path so Python can find the module
    sys.path.append(sys.path[0] + '/strategies')
    myStrategy = eval("__import__('%s').%s" % (args[1],stratName) )
    
    mySim = Simulator(myPort, myStrategy, startTime, endTime, timeStep)
    mySim.run()

# This ensures the main function runs automatically when the program is run from the command line, but 
# not if the file somehow gets imported from something else.  Nifty, eh?
if __name__ == "__main__":
    main()