from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot, QtCore
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import pandas as pd
from utils.inputsignal import *
from memory_profiler import profile


class WaveWidget():

    def __init__(self, *args, **kwargs):

        self.graphWidget = pg.PlotWidget()

        pg.setConfigOptions(antialias=True)

        data = np.random.normal(size=(10, 1000))

        wave_pair_wrapper = self.load_wave_pair_wrapper('1574634652027')
        tension_wave_wrapper = wave_pair_wrapper.get_wave_a_wrapper()
        tension_wave = tension_wave_wrapper.get_wave()
        current_wave_wrapper = wave_pair_wrapper.get_wave_b_wrapper()
        current_wave = current_wave_wrapper.get_wave()
        # plot data: x, y values
        self.graphWidget.setLabel('bottom', 'Time (s)', size='30')
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)
        pen = pg.mkPen(color=(0, 0, 255), style=QtCore.Qt.SolidLine)
        # self.graphWidget.plot(tension_wave.ts, tension_wave.ys, pen=pen)
        pen = pg.mkPen(color='b')
        self.graphWidget.plot(tension_wave.ts, tension_wave.ys, name="Tension", pen=pen)

    def getPlotWidget(self):
        return self.graphWidget

    @staticmethod
    def load_wave_pair_wrapper(filename):
        data_location = 'data/input/'

        directory = os.fsencode(data_location)
        _filename = os.fsencode(filename)
        signal_chunks = []

        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename), 'rb') as file:
                signal_chunks.extend(pickle.load(file))
                file.close()

        # signal_chunks = signal_chunks.map(lambda x: x.reload())
        # with open(os.path.join(directory, _filename), 'rb') as file:
        #     signal_chunks.extend(pickle.load(file))
        #     file.close()

        # return sum(signal_chunks)
        big_signal_chunk = sum(signal_chunk.reload() for signal_chunk in signal_chunks)
        return big_signal_chunk.get_wave_pair_wrapper()
        # return signal_chunks[0].get_wave_pair_wrapper()