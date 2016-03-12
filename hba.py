# $Id: hba.py,v 1.3 2013/01/15 10:33:27 bab Exp bab $

import sys
import os
import platform
import sqlite3
import numpy
import talib
from symbols import *
from datetime import *

import matplotlib
import matplotlib.colors as colors
import matplotlib.finance as finance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as pyplot
import matplotlib.gridspec as gridspec
from matplotlib.finance import candlestick2_ohlc

from IPython.utils.coloransi import TermColors

####################################################################################################
#                                                                                                  #
# Utilities                                                                                        #
#                                                                                                  #
####################################################################################################

#
# Utilities
#

# First, convert Julian (days since 4713 bc) to Gregorian date
# Then, convert to datetime representation (yy, mm, dd, ...)
def num2date(x):
    return mdates.num2date(x-1721425)

def num2datestr(x):
    return mdates.num2date(x-1721425).strftime('%Y-%m-%d')

def datestr2num(x):
    return mdates.date2num(datetime.strptime(x, '%Y-%m-%d')) + 1721425.0

def is_number(x):
    return(isinstance(x, (int, float)))

def is_array(x):
    return(isinstance(x, (list, tuple)))

def is_quote(x):
    return(isinstance(x, Quote))

def is_indicator(x):
    return(isinstance(x, Indicator))

def is_overlay(x):
    return(isinstance(x, Overlay))

def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses

def in_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

def info(msg):
    if (in_ipython()):
        print '{0}Info: {1}{2}'.format(TermColors.Green, msg, TermColors.Normal)
    else:
        print 'Info: {1}'.format(msg)

def warning(msg):
    if (in_ipython()):
        print '{0}Warning: {1}{2}'.format(TermColors.Yellow, msg, TermColors.Normal)
    else:
        print 'Info: {1}'.format(msg)

def error(msg):
    if (in_ipython()):
        print '{0}Error: {1}{2}'.format(TermColors.Red, msg, TermColors.Normal)
    else:
        print 'Info: {1}'.format(msg)

####################################################################################################

#
# Locators and Formatters for the x axis
#

class DayLocator(mticker.Locator):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self):
        dmin, dmax = self.axis.get_data_interval()
        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        ticks = []
        i = 0
        for date in self.dates:
            ticks.append(i)
            i += 1
        return ticks


class MondayLocator(mticker.Locator):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self):
        dmin, dmax = self.axis.get_data_interval()
        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        ticks = []
        i = 0
        prev = 6
        for date in self.dates:
            weekday = date.weekday()
            if(weekday < prev):
                ticks.append(i)
            i += 1
            prev = weekday
        return ticks


class MonthLocator(mticker.Locator):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self):
        dmin, dmax = self.axis.get_data_interval()
        #print "MonthLocator: interval=" + str([dmin, dmax])
        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        ticks = []
        i = 0
        prev = 31
        for date in self.dates:
            # Add a tick for every 1st day of month
            if(date.day < prev):
                ticks.append(i)
            i += 1
            prev = date.day
        #print "MonthLocator: ticks=" + str(ticks)
        return ticks


class QuarterLocator(mticker.Locator):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self):
        dmin, dmax = self.axis.get_data_interval()
        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        ticks = []
        i = 0
        prev = 31
        for date in self.dates:
            # Add a tick for every 1st day of month
            if (date.month == 4 or date.month == 7 or date.month == 10 or date.month == 1):
                if(date.day < prev):
                    ticks.append(i)
            i += 1
            prev = date.day
        return ticks


class YearLocator(mticker.Locator):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self):
        dmin, dmax = self.axis.get_data_interval()
        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        ticks = []
        i = 0
        prev = 12
        for date in self.dates:
            if(date.month < prev):
                ticks.append(i)
            i = i + 1
            prev = date.month
        return ticks


# From: IndexDateFormatter
class IndexDateFormatter(mticker.Formatter):
    '''
    Use with :class:`~matplotlib.ticker.IndexLocator` to cycle format
    strings by index.
    '''
    def __init__(self, t, fmt):
        '''
        *t* is a sequence of dates (floating point days).  *fmt* is a
        :func:`strftime` format string.
        '''
        self.t = t
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time *x* at position *pos*'
        ind = int(round(x))
        if ind >= len(self.t) or ind <= 0:
            return ''
        dt = num2date(self.t[ind])
        return mdates.cbook.unicode_safe(dt.strftime(self.fmt))

####################################################################################################

class Quote:

    def __init__(self, symbol='^GDAXI', start=None, end=None):
        self._symbol = symbol
        self._data = None
        self._index = None
        self._jdate = None
        self._dtime = None
        self._o = None
        self._h = None
        self._l = None
        self._c = None
        self.v = None
        self._color = 'b'
        self.load(start, end)


    @property
    def symbol(self):
        return self._symbol


    @property
    def color(self):
        return self._color


    def load(self, start=None, end=None):
        if (not 'MY_DB' in os.environ.keys()):
            os.environ['MY_DB'] = os.getcwd() + os.path.sep + 'db'
            warning('Could not find environment variable MY_DB.\n' +\
                    'Setting MY_DB to \'' + os.environ['MY_DB'] + '\'')
        dbPath = os.environ['MY_DB']

        if end == None:
            self.endDate = datetime.today()
        else:
            self.endDate = datetime.strptime(end, '%Y-%m-%d')

        if start == None:
            #start = str(self.endDate.year) + '-01-01'
            start = '1900-01-01'
        self.startDate = datetime.strptime(start, '%Y-%m-%d')
        # print 'startDate=' + str(self.startDate)

        #
        # Query database
        #
        path = dbPath + os.path.sep + self.symbol + '.db'

        if(not os.path.isfile(path)):
            raise Exception('Database file ' + path + ' does not exist.')

        conn = sqlite3.connect(path)
        c = conn.cursor()

        cmd = 'SELECT date,o,h,l,c,v FROM prices'

        # start_day = ...

        if(start != None):
            cmd += ' WHERE date>=julianday(\'' + str(start) + '\')'

        if(end != None):
            cmd += ' AND date<=julianday(\'' + str(end) + '\')'

        rows = c.execute(cmd).fetchall()
        dt = [('d', numpy.float),
              ('o', numpy.float),
              ('h', numpy.float),
              ('l', numpy.float),
              ('c', numpy.float),
              ('v', numpy.float)]
        conn.close()

        self._ohlc = []
#       for row in rows:
#           self._ohlc.append([row[0], row[1], row[2], row[3], row[4]])

        self._data = numpy.array(rows, dtype=dt)
        self._jdate = self._data['d']
        self._dtime = [num2date(jd) for jd in self._jdate]
        self._index = range(len(self._jdate))
        self._o = self._data['o']
        self._h = self._data['h']
        self._l = self._data['l']
        self._c = self._data['c']
        self._v = self._data['v']

# !!!   self.firstDate = num2datestr(self.d[0])
# !!!   self.lastDate = num2datestr(self.d[-1])
# !!!   print self.symbol + ': loaded ' + str(len(rows)) + ' values from ' + \
# !!!       str(self.firstDate) + ' to ' + str(self.lastDate) + '.'

        if (len(self._data) < 1):
            print "Warning: no data found in \"" + self.symbol + ".db\""
        return self


    @property
    def values(self):
        return self._c

    @property
    def o(self):
        return self._o

    @property
    def h(self):
        return self._h

    @property
    def l(self):
        return self._l

    @property
    def c(self):
        return self._c

    @property
    def ohlc(self):
        return self._ohlc

    @property
    def jdate(self):
        return self._jdate

    @property
    def dtime(self):
        return self._dtime


    def verify_data(self):
        for d, o, h, l, c, v in self._data:
            if(c < l):
                raise Exception('At ' + num2datestr(d) + ': c < l: ' + 'c=' + str(c) + \
                        ' l=' + str(l))
            elif(o < l):
                raise Exception('At ' + num2datestr(d) + ': o < l: ' + 'o=' + str(o) + \
                        ' l=' + str(l))
            elif(c > h):
                raise Exception('At ' + num2datestr(d) + ': c > h: ' + 'c=' + str(c) + \
                        ' h=' + str(h))
            elif(o > h):
                raise Exception('At ' + num2datestr(d) + ': o > h: ' + 'o=' + str(o) + \
                        ' h=' + str(h))
            elif(l > h):
                raise Exception('At ' + num2datestr(d) + ': l > h: ' + 'l=' + str(l) + \
                        ' h=' + str(h))


    def cat(self):
        for d, o, h, l, c, v in self._data:
            #print num2datestr(d) + ' ' + str(o) + ' ' + str(h) + ' ' + str(l) + ' ' + str(c)
            print '{0:12.2f} {1}{2:8.2f}{3:8.2f}{4:8.2f}{5:8.2f}{6:12d}'.format(d, num2datestr(d), \
                    o, h, l, c, int(v))

####################################################################################################

class Indicator(object):

#   @classmethod
#   def create(cls, name):
#       pass

    def __init__(self, quote):
        self._quote = quote

    def __str__(self):
        return str(self._values)

    def __get__(self, instance, owner):
        return self._quote

    @property
    def is_price(self):
        return self._is_price

    @property
    def is_overlay(self):
        return self._is_overlay

    @property
    def is_band(self):
        return self._is_band

    @property
    def date(self):
        return self._quote._jdate

    @property
    def close(self):
        return self._quote._c

    @property
    def values(self):
        return self._values

    @property
    def color(self):
        return self._color

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            for s in subclass.get_subclasses():
                yield s
            yield subclass

    @classmethod
    def get_name(cls):
        return None

####################################################################################################

class PriceIndicator(Indicator):

    def __init__(self, quote, n=30):
        Indicator.__init__(self, quote)

####################################################################################################

class SMA(PriceIndicator):

    def __init__(self, quote, n=30):
        PriceIndicator.__init__(self, quote)
        self._values = talib.SMA(quote.c, n)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return None

####################################################################################################

class SMA30(PriceIndicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = talib.SMA(quote.c, 30)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "SMA30"

####################################################################################################

class SMA90(PriceIndicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = talib.SMA(quote.c, 90)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "SMA90"

####################################################################################################

class SMA200(PriceIndicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = talib.SMA(quote.c, 200)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "SMA200"

####################################################################################################

class EMA(PriceIndicator):

    def __init__(self, quote, n=30):
        Indicator.__init__(self, quote)
        self._values = talib.EMA(quote.c, n)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "EMA"

####################################################################################################

class KAMA(PriceIndicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = talib.KAMA(quote.c, 30)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "KAMA"

####################################################################################################

class LINREG(PriceIndicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = talib.LINEARREG(quote.c, 90)
        self._is_price = True

    @classmethod
    def get_name(cls):
        return "LINREG"

####################################################################################################

class Overlay(Indicator):

    def __init__(self, quote):
        Indicator.__init__(self, quote)
        self._values = None
        self._is_price = False
        self._is_band = True

    @property
    def lower(self):
        return self._values[0]

    @property
    def upper(self):
        return self._values[2]

####################################################################################################

class Bollinger(Overlay):

    def __init__(self, quote):
        Overlay.__init__(self, quote)
        self._values = talib.BBANDS(quote.c, 20, 2)

    @classmethod
    def get_name(cls):
        return "Bollinger"

####################################################################################################

class Chart:

    def __init__(self, items=[], start_date=None, figure=None):
        if (is_quote(items)):
            self.items = [items]
        else:
            self.items = items

        # Suppress RuntimeWarnings during plotting
        numpy.seterr(invalid='ignore')

        # Calculate the grid specs
#       n = 0
#       for item in items:
#           if(item.__class__.__name__ == 'Quote'):
#               n += 1
#           elif(not item.is_overlay()):
#               n += 1

        for i in self.items:
            if (is_quote(i)):
                self.quote = i

        self.gs = gridspec.GridSpec(1, 1)

        if (figure != None):
            self.figure = figure
            self.embedded = True 
        else:
            self.embedded = False 
            self.figure = pyplot.figure(facecolor='white')
            self.figure.set_size_inches(12, 3, forward=True)

        self.lines = []
        self.collections = []

        # Number of graphs in the chart
        self.n_graphs = 0
        self.price_axis = None
        self.indicators = []
        if (start_date != None):
            self.start_date = start_date
            start_jdate = datestr2num(start_date)
            self.start_index = 0
            if (self.quote._jdate[0] > start_jdate):
                warning('No data available for specified start_date: ' + str(start_date))
            elif (self.quote._jdate[-1] < start_jdate):
                warning('No data available for specified start_date: ' + str(start_date))
            else:
                for i in self.quote._index:
                    if (self.quote._jdate[i] >= start_jdate):
                        self.start_index = i
                        break
        else:
            self.start_date = None
            self.start_index = 0
        self.start_zoom = 0
        self._colors = ['k', 'r', 'g', 'b', 'c', 'm', 'y',
                        'k', 'r', 'g', 'b', 'c', 'm', 'y',
                        'k', 'r', 'g', 'b', 'c', 'm', 'y',
                        'k', 'r', 'g', 'b', 'c', 'm', 'y',
                        'k', 'r', 'g', 'b', 'c', 'm', 'y']

        if (len(self.items) > 0):
            self.plot()

        if (not self.embedded):
            pyplot.close(self.figure)


    def get_figure(self):
        return self.figure


    def add_item(self, item):
        if(item.__class__.__name__ == 'Quote'):
            self.quote = item
        self.items.append(item)

    def remove_item(self, name):
        for i in self.items:
            if(i.__class__.__name__ == name):
                self.items.remove(i)

    def format_date(self, jdate, dtime):
        diff = dtime[-1] - dtime[0]
        if(diff.days > 1200):
            majloc = YearLocator(dtime)
            majfmt = IndexDateFormatter(jdate, '%Y')
            minloc = None
        elif(diff.days > 350):
            majloc = QuarterLocator(dtime)
            majfmt = IndexDateFormatter(jdate, '%b-%y')
            minloc = MonthLocator(dtime)
        elif(diff.days > 81):
            majloc = MonthLocator(dtime)
            majfmt = IndexDateFormatter(jdate, '%b-%y')
            minloc = MondayLocator(dtime)
        elif(diff.days > 21):
            majloc = MondayLocator(dtime)
            majfmt = IndexDateFormatter(jdate, '%d-%b')
            minloc = DayLocator(dtime)
        else:
            majloc = DayLocator(dtime)
            majfmt = IndexDateFormatter(jdate, '%d-%b')
            minloc = DayLocator(dtime)
        self.price_axis.xaxis.set_major_locator(majloc)
        if (minloc != None):
            self.price_axis.xaxis.set_minor_locator(minloc)
        self.price_axis.xaxis.set_major_formatter(majfmt)


    def clear_lines(self):
        for line in self.lines:
            if (line != None):
                line.remove()
        self.lines = []


    def clear_collections(self):
        for collection in (self.collections):
            self.collections.remove(collection)
        self.collections = []


    def plot(self):
        self.price_axis = pyplot.subplot(self.gs[self.n_graphs:self.n_graphs+1, 0])
        self.price_axis.grid(True, which='major', color='0.25', linestyle='-')
        self.price_axis.grid(True, which='minor', color='0.25', linestyle='-.')

        self.price_axis.xaxis.set_visible(True)

        self.price_axis.set_title(self.quote.symbol)
        self.price_axis.set_ylabel('Close')

        self.start_zoom = 0
        self.zoom(0)


    def zoom(self, mode=None):
        # Calculate zoom step size
        n_points = len(self.quote._jdate)
        if (n_points < 1):
            return
        delta = int(0.02 * n_points)
        if (mode == 1):
            if (self.start_zoom < n_points - delta):
                self.start_zoom += delta
        elif (mode == -1):
            if (self.start_zoom > delta):
                self.start_zoom -= delta
        elif (mode == 0):
            self.start_zoom = 0
        else:
            # Leave start_zoom unchanged
            pass

        if (self.start_zoom > 0):
            jdate = self.quote.jdate[self.start_zoom:]
            dtime = self.quote.dtime[self.start_zoom:]
        else:
            jdate = self.quote.jdate[self.start_index:]
            dtime = self.quote.dtime[self.start_index:]
        x = range(len(jdate))

        # self.clear_lines()
        for line in self.lines:
            if (line != None):
                line.remove()
        self.lines = []

        if (len(self.price_axis.collections) > 0):
            self.price_axis.collections.pop()

        i = 0
        for item in self.items:
            i += 1

            if (self.start_zoom > 0):
                y = item.values[self.start_zoom:]
            else:
                y = item.values[self.start_index:]

            if (is_overlay(item)):
                if (self.start_zoom > 0):
                    u = item.upper[self.start_zoom:]
                    l = item.lower[self.start_zoom:]
                else:
                    u = item.upper[self.start_index:]
                    l = item.lower[self.start_index:]
                #line, = self.price_axis.plot(x, u, 'c-')
                #self.lines.append(line)
                #line, = self.price_axis.plot(x, l, 'c-')
                #self.lines.append(line)
                collection = self.price_axis.fill_between(x, u, l, alpha=0.25)
                self.collections.append(collection)
            else:
                line, = self.price_axis.plot(x, y, self._colors[i])
                self.lines.append(line)

            self.format_date(jdate, dtime)

        # This requires that no set_xlim is used
        self.price_axis.relim()
        self.price_axis.autoscale_view()

        if (not self.embedded):
            pyplot.show()
        else:
            self.figure.show()


    def cursor(self, event):
        if (self.price_axis != None):
            inv = self.price_axis.transData.inverted()
            (x, y) = inv.transform((event.x, event.y))
            imax = len(self.quote.dtime)
            i = int(x)
            if (i < imax):
                jdate = self.quote.jdate[int(x)]
                price = self.quote.c[int(x)]
                print "[" + str(x) + ", " + str(y) + "] => " + str(price)
                self.price_axis.axvline(x)



if __name__ == '__main__':
    pass
