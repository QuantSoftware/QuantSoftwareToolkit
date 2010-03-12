from optparse import OptionParser
import sys

def main():
    # NOTE: the OptionParser class is currently not necessary, as we can just access sys.argv[1:], but if we
    # want to implement optional arguments, this will make it considerably easier.
    parser = OptionParser()
    
    # parser.parse_args() returns a tuple of (options, args)
    # As of right now, we don't have any options for our program, so we only care about the three arguments:
    # config file, strategy module name, strategy main function name
    args = parser.parse_args()[1]
    
    if len(args) != 3:
        print "FAILURE TO INCLUDE THE CORRECT NUMBER OF ARGUMENTS; TERMINATING INCOMPETENT USER."
        return
    
    configFile = args[0]
    
    f = open(configFile, 'r')
    stocks = []
    cash = 0
    for line in f.readlines():
        # Separate the command in the config file from the arguments
        line = line.strip().split('=')
        command = line[0].strip().upper()
        if len(line)>1:
            vals = line[1].upper().split()
        else:
            vals = []
        # Parse commands, look for correct number of arguments, do rudimentary error checking, apply to simulator as appropriate
        if command == 'CASH':
            if len(vals) != 1:
                print "WRONG NUMBER OF ARGUMENTS FOR CASH!!  RAAAAWR!  ALSO, I NEED TO LEARN TO THROW ERRORS!"
            else:
                try:
                    cash = float(vals[0])
                    print "You have %f monies in your portfolio." % cash
                except:
                    print "ARGUMENT FOR CASH IS NOT A FLOAT!! RAAAWR!"
        elif command == "STOCK":
            if len(vals) != 2:
                print "WRONG NUMBER OF ARGUMENTS FOR STOCK!!  RAAAAWR!  ALSO, I NEED TO LEARN TO THROW ERRORS!"
            else:
                try:
                    stocks.append([vals[0],int(vals[1])])
                except:
                    print "STOCK TAKES IN A STOCK NAME AND AN INT!  AND DON'T YOU FORGET IT!"
        elif command != '':
                print "Unrecognized command '%s'.  Note: many commands not yet implemented due to lack of information from Tucker." % command
    f.close()
    # Print stocks.  Not necessary; for demoing purposes, but may keep anyway
    print "Stocks owned:"
    if len(stocks) == 0:
        print "\tNone"
    else:
        for i in stocks:
            print "\tCompany: %s\n\t\tShares: %d" % (i[0],i[1])
    
    
    
    # rudimentary demonstration of how to run strategies
    
    # This line currently has a warning because we use 'portfolio' in the eval function when we run the
    # strategy, and thus it is never run in 'actual' code, thus the warning is for an unused variable
    portfolio = [cash,stocks]
    # Add the strategies subdirectory to the system path so Python can find the module
    sys.path.append(sys.path[0] + '/strategies')
    for i in range(8):
        # Note: may need to append strategy location to sys.path
        eval("__import__('%s').%s(portfolio)" % (args[1],args[2]) )

# This ensures the main function runs automatically when the program is run from the command line, but 
# not if the file somehow gets imported from something else.  Nifty, eh?
if __name__ == "__main__":
    main()


