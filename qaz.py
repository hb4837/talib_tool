from PyQt4.uic import loadUiType
from spyderlib.widgets import internalshell
from PyQt4 import QtCore, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from hba import *

Ui_MainWindow, QMainWindow = loadUiType('gui.ui')

# matplotlib events:
# ------------------
# button_press_event      MouseEvent - mouse button is pressed
# button_release_event 	MouseEvent - mouse button is released
# draw_event 	            DrawEvent - canvas draw
# key_press_event         KeyEvent - key is pressed
# key_release_event 	    KeyEvent - key is released
# motion_notify_event 	MouseEvent - mouse motion
# pick_event 	            PickEvent - an object in the canvas is selected
# resize_event 	        ResizeEvent - figure canvas is resized
# scroll_event 	        MouseEvent - mouse scroll wheel is rolled
# figure_enter_event 	    LocationEvent - mouse enters a new figure
# figure_leave_event 	    LocationEvent - mouse leaves a figure
# axes_enter_event 	    LocationEvent - mouse enters a new axes
# axes_leave_event 	    LocationEvent - mouse leaves an axes

class Main(QMainWindow, Ui_MainWindow):

    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.toolbar = None

        # Fill the indicators table
        n_rows = 0

#       self.indicator_classes = {}

#       for s in Indicator.get_subclasses():
#           n = s.get_name()
#           if (n != None):
#               self.indicator_classes[n] = s
#               n_rows += 1
#               self.indicators.setRowCount(n_rows)
#               item = QtGui.QTableWidgetItem()
#               item.setCheckState(QtCore.Qt.Unchecked)
#               item.setText(n)
#               self.indicators.setItem(n_rows-1, 0, item)

        # GUI event handlers
        self.symbolsList.itemSelectionChanged.connect(self.changeSymbolHandler)
        self.marketsCombo.currentIndexChanged.connect(self.changeMarketHandler)
        self.actionSma30.triggered.connect(self.actionSma30Handler)
        self.actionSma90.triggered.connect(self.actionSma90Handler)
        self.actionSma200.triggered.connect(self.actionSma200Handler)
        self.actionBollinger.triggered.connect(self.actionBollingerHandler)
#       self.indicators.itemPressed.connect(self.changeIndicatorHandler)
        # TODO: use new notation
        # QtCore.QObject.connect(self.symbolsList, QtCore.SIGNAL('itemSelectionChanged()'), self.changeSymbolHandler)

        self.figure = Figure()
        self.addFig(self.figure)

        pythonshell = internalshell.InternalShell(self.shellWidget, namespace=globals(), \
            commands=[], multithreaded=False)
        pythonshell.resize(self.shellWidget.size())

        #pythonshell.resize(800, 300)
        #shell.setWidget(pythonshell)
        #shell.show()

        self.chart = None


    def on_button_press_event(self, event):
        print "on_button_press_event: [" + str(event.x) + ", " + str(event.y) + "]"


    def on_motion_notify_event(self, event):
        if (self.chart != None):
            self.chart.cursor(event)


    def on_scroll_event(self, event):
        if (event.button == 'up'):
            mode = +1
        elif (event.button == 'down'):
            mode = -1
        self.chart.zoom(mode)
        self.canvas.draw()


    def changeSymbolHandler(self):
        s = str(self.symbolsList.currentItem().text())
        self.quote = Quote(s).load("2015-01-01")

        # Delete figure
        self.plotLayout.removeWidget(self.canvas)
        self.canvas.close()

        # Add new figure
        self.canvas = FigureCanvas(self.figure)
        self.plotLayout.addWidget(self.canvas)

        self.chart = Chart(self.quote, figure=self.figure)
        self.chart.add_item(self.quote)

        self.canvas.draw()

        self.cid = self.figure.canvas.mpl_connect('scroll_event', self.on_scroll_event)
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self.on_button_press_event)
        # self.cid = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion_notify_event)
        self.chart.plot()
        self.canvas.draw()


    def changeIndicatorHandler(self):
        item = self.indicators.currentItem()
        indicator_name = str(item.text())

        if (item.checkState() == QtCore.Qt.Unchecked):
            item.setCheckState(QtCore.Qt.Checked)
            indicator = self.indicator_classes[indicator_name](self.quote)
            self.chart.add_item(indicator)
        elif (item.checkState() == QtCore.Qt.Checked):
            item.setCheckState(QtCore.Qt.Unchecked)
            self.chart.remove_item(indicator_name)
        else:
            print "???????????????"

        #self.chart.add_item(self.quote)
        # Replace figure
        self.figure = self.chart.get_fig()
        self.delFig()
        self.addFig(self.figure)
        self.chart.zoom()
#       # Replace figure
#       self.figure = self.chart.get_fig()
#       self.delFig()
#       self.addFig(self.figure)
#       self.chart.plot()


    def changeMarketHandler(self, index):
        market = MARKET_REFS[index]
        # Replace symbols
        self.symbolsList.clear()
        for s in sorted(market.iterkeys()):
            self.symbolsList.addItem(s)


    def actionSma30Handler(self):
        s = SMA(self.chart.quote, 30)
        self.chart.add_item(s)
        self.chart.plot()
        self.canvas.draw()


    def actionSma90Handler(self):
        s = SMA(self.chart.quote, 90)
        self.chart.add_item(s)
        self.chart.plot()
        self.canvas.draw()


    def actionSma200Handler(self):
        s = SMA(self.chart.quote, 200)
        self.chart.add_item(s)
        self.chart.plot()
        self.canvas.draw()


    def actionBollingerHandler(self):
        s = Bollinger(self.chart.quote)
        self.chart.add_item(s)
        self.chart.plot()
        self.canvas.draw()


    def initMarkets(self):
        for market in MARKET_NAMES:
            self.marketsCombo.addItem(market)


    def addFig(self, fig):
        self.canvas = FigureCanvas(fig)
        self.plotLayout.addWidget(self.canvas)
        #self.canvas.draw()
        self.cid = self.figure.canvas.mpl_connect('scroll_event', self.on_scroll_event)
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self.on_button_press_event)
        # self.cid = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion_notify_event)


    def delFig(self,):
        self.plotLayout.removeWidget(self.canvas)
        self.canvas.close()
#       if (self.toolbar != None):
#           self.plotLayout.removeWidget(self.toolbar)
#           self.toolbar.close()


if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np
    from hba import *

    app = QtGui.QApplication(sys.argv)
    main = Main()

    main.initMarkets()
    main.changeMarketHandler(0)

    main.show()
    sys.exit(app.exec_())

