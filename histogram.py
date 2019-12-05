from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot, QtCore
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import pandas as pd
from views import wavewidget as ww
from utils.inputsignal import *
from memory_profiler import profile


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = ww.WaveWidget()
        self.setCentralWidget(self.graphWidget.getPlotWidget())

def main():

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
