"""
Created on March 22, 2011

@author: Tucker Balch
@contact: tucker@cc.gatech.edu

This script generates a list of days on which we expect the NYSE to be
open.  Information is drawn from two websites:

http://www.timeanddate.com/holidays/
http://www.nyse.com/about/newsevents/1176373643795.html
"""

__version__ = "$Revision$"

import numpy as np
from datetime import *


rootday = datetime(2011,1,3) # first monday in 2011
endday = datetime(2031,1,1) # don't go beyond this date
weekdays = [] # all weekdays
oneday = timedelta(1) # length of one day
curr = 0
candidateday = rootday + curr*oneday

#
# create a list of all weekdays
#
while (candidateday < endday):
    # add 5 weekdays to list
    for j in range(5): # 5 days per week
        weekdays.append(rootday + curr*oneday)
        curr = curr+1
    curr = curr+2 # skip the weekend
    candidateday = rootday + curr*oneday

#
# Create a list of all NYSE observed holidays (from NYSE's website)
# The dates are confirmed through 2013, and estimated thereafter.
#
NYSEholidays = []

# New Year's Day
NYSEholidays.append(datetime(2011,1,1))
NYSEholidays.append(datetime(2012,1,2))
NYSEholidays.append(datetime(2013,1,1))
NYSEholidays.append(datetime(2014,1,1))
NYSEholidays.append(datetime(2015,1,1))
NYSEholidays.append(datetime(2016,1,1))
NYSEholidays.append(datetime(2017,1,2))
NYSEholidays.append(datetime(2018,1,1))
NYSEholidays.append(datetime(2019,1,1))
NYSEholidays.append(datetime(2020,1,1))
NYSEholidays.append(datetime(2021,1,1))
NYSEholidays.append(datetime(2022,1,1))
NYSEholidays.append(datetime(2023,1,2))
NYSEholidays.append(datetime(2024,1,1))
NYSEholidays.append(datetime(2025,1,1))
NYSEholidays.append(datetime(2026,1,1))
NYSEholidays.append(datetime(2027,1,1))
NYSEholidays.append(datetime(2028,1,1))
NYSEholidays.append(datetime(2029,1,1))
NYSEholidays.append(datetime(2030,1,1))
NYSEholidays.append(datetime(2031,1,1))



# MLK Day
NYSEholidays.append(datetime(2011,1,17))
NYSEholidays.append(datetime(2012,1,16))
NYSEholidays.append(datetime(2013,1,21))
NYSEholidays.append(datetime(2014,1,20))
NYSEholidays.append(datetime(2015,1,19))
NYSEholidays.append(datetime(2016,1,18))
NYSEholidays.append(datetime(2017,1,16))
NYSEholidays.append(datetime(2018,1,15))
NYSEholidays.append(datetime(2019,1,21))
NYSEholidays.append(datetime(2020,1,20))
NYSEholidays.append(datetime(2021,1,18))
NYSEholidays.append(datetime(2022,1,17))
NYSEholidays.append(datetime(2023,1,16))
NYSEholidays.append(datetime(2024,1,15))
NYSEholidays.append(datetime(2025,1,20))
NYSEholidays.append(datetime(2026,1,19))
NYSEholidays.append(datetime(2027,1,18))
NYSEholidays.append(datetime(2028,1,17))
NYSEholidays.append(datetime(2029,1,15))
NYSEholidays.append(datetime(2030,1,21))



# Washington's Birthday
NYSEholidays.append(datetime(2011,2,21))
NYSEholidays.append(datetime(2012,2,20))
NYSEholidays.append(datetime(2013,2,18))
NYSEholidays.append(datetime(2014,2,17))
NYSEholidays.append(datetime(2015,2,16))
NYSEholidays.append(datetime(2016,2,15))
NYSEholidays.append(datetime(2017,2,20))
NYSEholidays.append(datetime(2018,2,19))
NYSEholidays.append(datetime(2019,2,18))
NYSEholidays.append(datetime(2020,2,17))
NYSEholidays.append(datetime(2021,2,15))
NYSEholidays.append(datetime(2022,2,21))
NYSEholidays.append(datetime(2023,2,20))
NYSEholidays.append(datetime(2024,2,19))
NYSEholidays.append(datetime(2025,2,17))
NYSEholidays.append(datetime(2026,2,16))
NYSEholidays.append(datetime(2027,2,15))
NYSEholidays.append(datetime(2028,2,21))
NYSEholidays.append(datetime(2029,2,19))
NYSEholidays.append(datetime(2030,2,18))

# Good Friday
NYSEholidays.append(datetime(2011,4,22))
NYSEholidays.append(datetime(2012,4,6))
NYSEholidays.append(datetime(2013,3,29))
NYSEholidays.append(datetime(2014,4,18))
NYSEholidays.append(datetime(2015,4,3))
NYSEholidays.append(datetime(2016,3,25))
NYSEholidays.append(datetime(2017,4,14))
NYSEholidays.append(datetime(2018,3,30))
NYSEholidays.append(datetime(2019,4,19))
NYSEholidays.append(datetime(2020,4,10))
NYSEholidays.append(datetime(2021,4,2))
NYSEholidays.append(datetime(2022,4,15))
NYSEholidays.append(datetime(2023,4,7))
NYSEholidays.append(datetime(2024,3,29))
NYSEholidays.append(datetime(2025,4,18))
NYSEholidays.append(datetime(2026,4,3))
NYSEholidays.append(datetime(2027,3,26))
NYSEholidays.append(datetime(2028,4,14))
NYSEholidays.append(datetime(2029,3,30))
NYSEholidays.append(datetime(2030,4,19))

# Memorial Day
NYSEholidays.append(datetime(2011,5,30))
NYSEholidays.append(datetime(2012,5,28))
NYSEholidays.append(datetime(2013,5,27))
NYSEholidays.append(datetime(2014,5,26))
NYSEholidays.append(datetime(2015,5,25))
NYSEholidays.append(datetime(2016,5,30))
NYSEholidays.append(datetime(2017,5,29))
NYSEholidays.append(datetime(2018,5,28))
NYSEholidays.append(datetime(2019,5,27))
NYSEholidays.append(datetime(2020,5,25))
NYSEholidays.append(datetime(2021,5,31))
NYSEholidays.append(datetime(2022,5,30))
NYSEholidays.append(datetime(2023,5,29))
NYSEholidays.append(datetime(2024,5,27))
NYSEholidays.append(datetime(2025,5,26))
NYSEholidays.append(datetime(2026,5,25))
NYSEholidays.append(datetime(2027,5,31))
NYSEholidays.append(datetime(2028,5,29))
NYSEholidays.append(datetime(2029,5,28))
NYSEholidays.append(datetime(2030,5,27))


# Independance Day
NYSEholidays.append(datetime(2011,7,4))
NYSEholidays.append(datetime(2012,7,4))
NYSEholidays.append(datetime(2013,7,4))
NYSEholidays.append(datetime(2014,7,4))
NYSEholidays.append(datetime(2015,7,3))
NYSEholidays.append(datetime(2016,7,4))
NYSEholidays.append(datetime(2017,7,4))
NYSEholidays.append(datetime(2018,7,4))
NYSEholidays.append(datetime(2019,7,4))
NYSEholidays.append(datetime(2020,7,3))
NYSEholidays.append(datetime(2021,7,5))
NYSEholidays.append(datetime(2022,7,4))
NYSEholidays.append(datetime(2023,7,4))
NYSEholidays.append(datetime(2024,7,4))
NYSEholidays.append(datetime(2025,7,4))
NYSEholidays.append(datetime(2026,7,3))
NYSEholidays.append(datetime(2027,7,5))
NYSEholidays.append(datetime(2028,7,4))
NYSEholidays.append(datetime(2029,7,4))
NYSEholidays.append(datetime(2030,7,4))



# Labor Day
NYSEholidays.append(datetime(2011,9,5))
NYSEholidays.append(datetime(2012,9,3))
NYSEholidays.append(datetime(2013,9,2))
NYSEholidays.append(datetime(2014,9,1))
NYSEholidays.append(datetime(2015,9,7))
NYSEholidays.append(datetime(2016,9,5))
NYSEholidays.append(datetime(2017,9,4))
NYSEholidays.append(datetime(2018,9,3))
NYSEholidays.append(datetime(2019,9,2))
NYSEholidays.append(datetime(2020,9,7))
NYSEholidays.append(datetime(2021,9,6))
NYSEholidays.append(datetime(2022,9,5))
NYSEholidays.append(datetime(2023,9,4))
NYSEholidays.append(datetime(2024,9,2))
NYSEholidays.append(datetime(2025,9,1))
NYSEholidays.append(datetime(2026,9,7))
NYSEholidays.append(datetime(2027,9,6))
NYSEholidays.append(datetime(2028,9,4))
NYSEholidays.append(datetime(2029,9,3))
NYSEholidays.append(datetime(2030,9,2))



# Thanksgiving Day
NYSEholidays.append(datetime(2011,11,24))
NYSEholidays.append(datetime(2012,11,22))
NYSEholidays.append(datetime(2013,11,28))
NYSEholidays.append(datetime(2014,11,27))
NYSEholidays.append(datetime(2015,11,26))
NYSEholidays.append(datetime(2016,11,24))
NYSEholidays.append(datetime(2017,11,23))
NYSEholidays.append(datetime(2018,11,22))
NYSEholidays.append(datetime(2019,11,28))
NYSEholidays.append(datetime(2020,11,26))
NYSEholidays.append(datetime(2021,11,25))
NYSEholidays.append(datetime(2022,11,24))
NYSEholidays.append(datetime(2023,11,23))
NYSEholidays.append(datetime(2024,11,28))
NYSEholidays.append(datetime(2025,11,27))
NYSEholidays.append(datetime(2026,11,26))
NYSEholidays.append(datetime(2027,11,25))
NYSEholidays.append(datetime(2028,11,23))
NYSEholidays.append(datetime(2029,11,22))
NYSEholidays.append(datetime(2030,11,28))


# Christmas
NYSEholidays.append(datetime(2011,12,26))
NYSEholidays.append(datetime(2012,12,25))
NYSEholidays.append(datetime(2013,12,25))
NYSEholidays.append(datetime(2014,12,25))
NYSEholidays.append(datetime(2015,12,25))
NYSEholidays.append(datetime(2016,12,26))
NYSEholidays.append(datetime(2017,12,25))
NYSEholidays.append(datetime(2018,12,25))
NYSEholidays.append(datetime(2019,12,25))
NYSEholidays.append(datetime(2020,12,25))
NYSEholidays.append(datetime(2021,12,24))
NYSEholidays.append(datetime(2022,12,26))
NYSEholidays.append(datetime(2023,12,25))
NYSEholidays.append(datetime(2024,12,25))
NYSEholidays.append(datetime(2025,12,25))
NYSEholidays.append(datetime(2026,12,25))
NYSEholidays.append(datetime(2027,12,24))
NYSEholidays.append(datetime(2028,12,25))
NYSEholidays.append(datetime(2029,12,25))
NYSEholidays.append(datetime(2030,12,25))

# Holidays due to unexpected event
# Sandy Storm
NYSEholidays.append(datetime(2012,10,29))
NYSEholidays.append(datetime(2012,10,30))


#
# Now we use Python's set magic to remove the holidays
#
setweekdays = set(weekdays) # convert weekdays to a set
setNYSEholidays = set(NYSEholidays)
newdays = set.difference(setweekdays,NYSEholidays) # remove holidays
newdays = sorted(list(newdays)) # convert back to sorted list

log = []
# print it out
for i in newdays:
    print i.strftime("%m/%d/%Y")
    log.append(i.strftime("%m/%d/%Y"))

np.savetxt('NYSE_dates.csv', log, fmt='%s', delimiter=',') 
