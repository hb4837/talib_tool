"""
Creates SQLite3 database from historical Yahoo data for specified stock quote (or ^GDAXI)
"""
 
import sys
import sqlite3
import matplotlib.finance as mf
from time import *
from datetime import *
from symbols import *
import urllib
 
def usage():
    print "usage: yahoo2db <symbol>"
    sys.exit(1)

def date2str(date):
    return str(datetime.fromordinal(date-1721425))

def getQuote(symbol, startDate=None, endDate=None):
    if(startDate == None):
        startDate = datetime(1900, 1, 1)
    if(endDate == None):
        endDate = datetime.today()
    #endDate = datetime(2012,12,12)
     
    try:
        conn = sqlite3.connect("./db/" + symbol + ".db")

        c = conn.cursor()

        r = c.execute('''SELECT count(*) FROM sqlite_master
                         WHERE type=\'table\' AND name=\'prices\' ''')
        tableExists = r.fetchone()[0] > 0

        if tableExists:
            # Calculate the start date for continuing the history data
            result = c.execute("SELECT min(date), max(date) FROM prices")
            if result:
                firstDate, lastDate = result.fetchone()
                if(firstDate  != None and lastDate != None):
#                   print "Table exists, starting at " + date2str(firstDate) + \
#                       ", ending at " + date2str(lastDate)
                    startDateEpochs = lastDate + 1
                    dt = datetime.fromordinal(startDateEpochs-1721425)
                    startDate = datetime(dt.year, dt.month, dt.day, 00, 00)
        else:
            # No table existing => create one
            c.execute('''CREATE TABLE prices(
                         date integer, o real, h real, l real, c real, v real
                      )''')

        # print "startDate=" + str(startDate)
        # print "endDate=" + str(endDate)
        # print "difference=" + str(endDate-startDate)
        difference = endDate - startDate
        #print "startDate=" + str(startDate)
        #print "endDate=" + str(endDate)
        if difference.days > 0:
            # print "=> " + str(difference.days) + " days"
            try:
                #print "mf.quotes_historical_yahoo(" + str(urllib.quote(symbol)) + \
                      #", " + str(startDate) + ", " + str(endDate) + ")"
                quotes = mf.quotes_historical_yahoo_ohlc(symbol, startDate, endDate)

                if quotes:
                    for q in quotes:
                        c.execute("INSERT INTO prices VALUES("
                                + str(1721425 + q[0]) # date
                                + ", " + str(q[1])    # open
                                + ", " + str(q[2])    # high
                                + ", " + str(q[3])    # low
                                + ", " + str(q[4])    # close
                                + ", " + str(q[5])    # volume
                                + ")")

                    print "Added " + str(len(quotes)) + " items for " + symbol
                else:
                    print "No new data available."
                conn.commit()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print "Error:", sys.exc_info()[0]
        else:
            print "=> nothing to do."

        conn.close()
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print "Error:", sys.exc_info()[0]


def getQuotesForIndex(index, start=None, end=None):
    for symbol in index:
        # print symbol
        try:
            getQuote(symbol, start, end)
        except KeyboardInterrupt:
            sys.exit(0)

def main():
    if len(sys.argv) > 3 and sys.argv[3] != None:
        endDate = sys.argv[3]
    else:
        endDate = None
    if len(sys.argv) > 2 and sys.argv[2] != None:
        startDate = sys.argv[2]
    else:
        startDate = None
    if len(sys.argv) > 1 and sys.argv[1] != None:
        try:
            getQuote(sys.argv[1], startDate, endDate)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        for s in [DAX, MDAX, SDAX, TECDAX, DJI, NDX]:
            getQuotesForIndex(s, startDate, endDate)
        for s in INDEXES:
            getQuote(s, startDate, endDate)
#       getQuotesForIndex(DAX, startDate, endDate)
#       getQuotesForIndex(MDAX, startDate, endDate)
#       getQuotesForIndex(SDAX, startDate, endDate)
#       getQuotesForIndex(TECDAX, startDate, endDate)
#       getQuotesForIndex(DJI, startDate, endDate)
#       getQuotesForIndex(NDX, startDate, endDate)

if __name__ == "__main__":
    main()

# date_raw = datetime.datetime.fromordinal(int(quote[0]))
# year, month, day = date_raw.year, date_raw.month, date_raw.day
# date_string = str(year)+'-'+str(month)+'-'+str(day)

# sqlite3 ^GDAXI.db "select datetime(date) from prices"

