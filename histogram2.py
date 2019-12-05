from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot, QtCore
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import pandas as pd
from utils.inputsignal import *
from memory_profiler import profile


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        data = np.random.normal(size=(10, 1000))

        signal_chunks = self.load_signal_chunks_list('1574634652027')

        wave_pair_wrapper = self.load_wave_pair_wrapper('1574634652027')
        wave_pair_wrappers = (signal_chunk.get_wave_pair_wrapper() for signal_chunk in signal_chunks)
        tension_wave_wrapper = wave_pair_wrapper.get_wave_a_wrapper()
        tension_wave = tension_wave_wrapper.get_wave()
        # tension_data = np.vstack((tension_wave.ts, tension_wave.ys))
        # plot data: x, y values
        self.graphWidget.setLabel('bottom', 'Time (s)', size='30')
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)
        pen = pg.mkPen(color=(0, 0, 255), style=QtCore.Qt.SolidLine)
        # self.graphWidget.plot(tension_wave.ts, tension_wave.ys, pen=pen)
        # tension_curve = self.plot("Tension", 'b')
        curves = []

        chunkSize = 100
        # Remove chunks after we have 10
        maxChunks = 10
        tension_data = np.empty((chunkSize + 1, 2))

        tension_ptr = 0
        startTime = pg.ptime.time()

        def tension_update():
            global tension_curve, tension_data, tension_ptr
            now = pg.ptime.time()
            for c in curves:
                c.setPos(-(now - startTime), 0)

            i = tension_ptr % chunkSize
            if i == 0:
                tension_curve = self.plot()
                curves.append(tension_curve)
                last = tension_data[-1]
                data5 = np.empty((chunkSize + 1, 2))
                data5[0] = last
                while len(curves) > maxChunks:
                    c = curves.pop(0)
                    self.removeItem(c)
            else:
                curve = curves[-1]

            tension_data[i + 1, 0] = now - startTime
            tension_data[i + 1, 1] = np.random.normal()
            curve.setData(x=tension_data[:i + 2, 0], y=tension_data[:i + 2, 1])
            tension_ptr += 1

        timer = QtCore.QTimer()
        # timer.timeout.connect(update)
        timer.timeout.connect(tension_update)
        timer.start(50)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        # self.graphWidget.plot(x, y, name=plotname, pen=pen)
        return self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def start_plot(self, plotname, color):
        pen = pg.mkPen(color=color)
        # self.graphWidget.plot(x, y, name=plotname, pen=pen)
        return self.graphWidget.plot(name=plotname, pen=pen)

    def load_wave_pair_wrapper(self, filename):
        data_location = 'data/input/'

        directory = os.fsencode(data_location)
        _filename = os.fsencode(filename)
        signal_chunks = []

        # for filename in os.listdir(directory):
        #     with open(os.path.join(directory, filename), 'rb') as file:
        #         signal_chunks.extend(pickle.load(file))
        #         file.close()

        with open(os.path.join(directory, _filename), 'rb') as file:
            signal_chunks.extend(pickle.load(file))
            file.close()

        return sum(signal_chunk.get_wave_pair_wrapper() for signal_chunk in signal_chunks)
        # return signal_chunks[0].get_wave_pair_wrapper()

    def load_signal_chunks_list(self, filename):
        data_location = 'data/input/'

        directory = os.fsencode(data_location)
        _filename = os.fsencode(filename)
        signal_chunks = []

        # for filename in os.listdir(directory):
        #     with open(os.path.join(directory, filename), 'rb') as file:
        #         signal_chunks.extend(pickle.load(file))
        #         file.close()

        with open(os.path.join(directory, _filename), 'rb') as file:
            signal_chunks.extend(pickle.load(file))
            file.close()

        return signal_chunks
        # return signal_chunks[0].get_wave_pair_wrapper()

def main():

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
