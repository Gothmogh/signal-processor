from numbers import Number

from bitstring import BitArray

from inputsignal import *
from signalreader import read_csv
from main_window_ui import *
import pyqtgraph as pg
import os
import pickle

from wavewrapper import *


def udp_parse(_udp_packet):
    timestamp = BitArray(_udp_packet[0:4]).uint
    readings = []

    for i in range(4, len(_udp_packet), 2):
        data = BitArray(_udp_packet[i:i + 2]).uint
        readings.append(data)

    even_readings = readings[0:][::2]
    odd_readings = readings[1:][::2]

    return timestamp, even_readings, odd_readings


def udp_data_transform(timestamp, tension_data, current_data, frame_rate):
    if tension_data is None or not isinstance(tension_data, list):
        raise Exception("_tension_data must be a ndarray")

    if current_data is None or not isinstance(current_data, list):
        raise Exception("_current_data must be a ndarray")

    if not len(tension_data) == len(current_data):
        raise Exception("_tension_data and _current_data must be same length")

    tension_data = ((np.asanyarray(tension_data) * 3.3 / 4096) - 1.65)
    current_data = ((np.asanyarray(current_data) * 3.3 / 4096) - 1.65)

    sample_period = 1 / frame_rate
    frames = len(tension_data)

    step = sample_period
    end = frames * step
    ts = np.add(np.arange(0, end, step=step), timestamp / (10 ** 6))

    return ts, tension_data, current_data


def udp_to_signal_chunk(_udp_packet):
    timestamp = BitArray(_udp_packet[0:4]).int
    readings = []

    for i in range(4, len(_udp_packet), 2):
        data = BitArray(_udp_packet[i:i + 2]).uint
        readings.append(data)

    even_readings = readings[0:][::2]
    odd_readings = readings[1:][::2]

    return InputSignalChunk(timestamp, even_readings, odd_readings)


def load_wave_pair_wrapper_from_udp_packets(buffer_size=10):
    MAXSIZE = 64000
    TIMEOUT = 1
    INT = 3.0  # interval in seconds

    _server_socket = socket(AF_INET, SOCK_DGRAM)
    # Assign IP address and port number to socket
    _server_socket.bind(('', 3500))
    _server_socket.settimeout(TIMEOUT)


    # create udp_socket
    # last = time.time() - INT
    # _server_socket.settimeout(TIMEOUT)
    i = 0
    arr = []
    _packets = []


    signal_chunks = []

    print("Listening to port 3500")



    frame_rate = 2000
    fund_freq = 50.0

    for i in range(buffer_size):
        try:
            _packet = _server_socket.recv(MAXSIZE)
            signal_chunk = udp_to_signal_chunk(_packet)
            signal_chunks.append(signal_chunk)
            # _packets.append(_packet)
            print('Reading... ' + str(i) + '\r')
        except timeout:
            # handle recv timeout
            continue  # or break, or return
        except OSError:
            # handle recv error (Python 3.3+)
            break  # or continue, or return
        except Exception as err:
            print(err)
            traceback.print_tb(err.__traceback__)
            continue

    _server_socket.close()

    millis = int(round(time.time() * 1000))

    print("Received " + str(i) + " packets with timestamp " + str(millis))

    big_signal_chunk = sum(signal_chunks)
    return big_signal_chunk.get_wave_pair_wrapper()

    # ts_cumm = []
    # tension_data_cumm = []
    # current_data_cumm = []
    #
    # for _packet in _packets:
    #     timestamp, even_readings, odd_readings = udp_parse(_packet)
    #     ts, tension_data, current_data = udp_data_transform(timestamp, even_readings, odd_readings, frame_rate)
    #     ts_cumm.extend(ts)
    #     tension_data_cumm.extend(tension_data)
    #     current_data_cumm.extend(current_data)
    #
    # millis = int(round(time.time() * 1000))
    #
    # print("Processed " + str(i) + " packets with timestamp " + str(millis))
    # # ts_cumm = np.sort(ts_cumm)
    # tension_wave = Wave(ys=tension_data_cumm, ts=ts_cumm, framerate=frame_rate)
    # tension_wave_wrapper = WaveWrapper(tension_wave, fund_freq)
    # current_wave = Wave(ys=current_data_cumm, ts=ts_cumm, framerate=frame_rate)
    # current_wave_wrapper = WaveWrapper(current_wave, fund_freq)
    #
    # wave_pair_wrapper = WavePairWrapper(tension_wave_wrapper, current_wave_wrapper)
    #
    # return wave_pair_wrapper


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # self.__wave_pair_wrapper = self.load_wave_pair_wrapper_csv('data/', 'sampleSignal.csv')
        self.__wave_pair_wrapper = load_wave_pair_wrapper_from_udp_packets(1)
        self.draw_contents()

        # self.loadExampleCsv()
        # self.tensionValuesWidget = pg.PlotWidget()

        pg.setConfigOptions(antialias=True)
        # self.loadExampleCsv.clicked.connect(self.load_example_csv)
        # self.loadUdpPackets.clicked.connect(self.record_n_packets)

    def record_n_packets(self):
        self.__wave_pair_wrapper = load_wave_pair_wrapper_from_udp_packets(self.packetNumber.value())
        self.draw_contents()

    def load_example_csv(self):
        self.__wave_pair_wrapper = self.load_wave_pair_wrapper_csv('data/', 'sampleSignal.csv')
        self.draw_contents()


    def draw_contents(self):
        spectrum_limit_mult = 4

        # self.__wave_pair_wrapper = self.load_wave_pair_wrapper_csv('data/', 'sampleSignal.csv')
        # self.__wave_pair_wrapper = load_wave_pair_wrapper_from_udp_packets()
        tension_wave_wrapper = self.__wave_pair_wrapper.get_wave_a_wrapper()
        tension_wave = tension_wave_wrapper.get_wave()
        tension_spectrum = tension_wave.make_spectrum()
        tension_wave = tension_wave_wrapper.get_wave()
        tension_fund_freq = tension_wave_wrapper.get_fund_freq()
        tension_values = {'t_rms': tension_wave_wrapper.t_rms(), 'h1_amp': tension_wave_wrapper.hn_amp(),
                          'h1_rms': tension_wave_wrapper.hn_rms(), 'h2_amp': tension_wave_wrapper.hn_amp(n=2, ),
                          'h2_rms': tension_wave_wrapper.hn_rms(n=2, ), 'h3_amp': tension_wave_wrapper.hn_amp(n=3, ),
                          'h3_rms': tension_wave_wrapper.hn_rms(n=3, ), 't_h_dist': tension_wave_wrapper.t_h_dist(n_max=3, )}

        current_wave_wrapper = self.__wave_pair_wrapper.get_wave_b_wrapper()
        current_wave = current_wave_wrapper.get_wave()
        current_spectrum = current_wave.make_spectrum()
        current_fund_freq = current_wave_wrapper.get_fund_freq()
        current_values = {'t_rms': current_wave_wrapper.t_rms(), 'h1_amp': current_wave_wrapper.hn_amp(),
                          'h1_rms': current_wave_wrapper.hn_rms(), 'h2_amp': current_wave_wrapper.hn_amp(n=2, ),
                          'h2_rms': current_wave_wrapper.hn_rms(n=2, ), 'h3_amp': current_wave_wrapper.hn_amp(n=3, ),
                          'h3_rms': current_wave_wrapper.hn_rms(n=3, ), 't_h_dist': current_wave_wrapper.t_h_dist(n_max=3, )}


        # plot data: x, y values
        # self.tensionWaveWidget.plotItem.close()
        # self.tensionSpectrumWidget.plotItem.close()
        # self.currentWaveWidget.plotItem.close()
        # self.currentSpectrumWidget.plotItem.close()

        self.plot_wave(self.tensionWaveWidget, tension_wave, 'Tension', 'Tension [V]', 'Time [s]', 'b')
        self.plot_spectrum(self.tensionSpectrumWidget, tension_spectrum, 'Tension', 'Amplitude [Vp]', 'Frequency [Hz]', 'b', limit=tension_fund_freq * spectrum_limit_mult)
        self.plot_values(self, tension_values, 'tension')

        self.plot_wave(self.currentWaveWidget, current_wave, 'Current', 'Current [A]', 'Time [s]', 'r')
        self.plot_spectrum(self.currentSpectrumWidget, current_spectrum, 'Current', 'Amplitude [Ap]', 'Frequency [Hz]', 'r', limit=current_fund_freq * spectrum_limit_mult)
        self.plot_values(self, current_values, 'current')

    @staticmethod
    def plot_wave(plot_widget, wave, name, left_label, bottom_label, color):
        plot_widget.setTitle(name + ' wave')
        plot_widget.setLabel('left', left_label, size='30')
        plot_widget.setLabel('bottom', bottom_label, size='30')
        plot_widget.setBackground('w')
        plot_widget.showGrid(x=True, y=True)
        pen = pg.mkPen(color)
        plot_widget.plot(wave.ts, wave.ys, name=name, pen=pen)

    @staticmethod
    def plot_spectrum(plot_widget, spectrum, name, left_label, bottom_label, color, limit=None):
        plot_widget.setTitle(name + ' spectrum')
        plot_widget.setLabel('left', left_label, size='30')
        plot_widget.setLabel('bottom', bottom_label, size='30')
        plot_widget.setBackground('w')
        plot_widget.showGrid(x=True, y=True)
        # pen = pg.mkPen(brush=color)
        # pg.BarGraphItem(x=spectrum.fs, height=spectrum.amps, width=0.6, )
        limit = util.find_nearest_idx(spectrum, limit, 1)
        if limit is None:
            bar_graph = pg.BarGraphItem(x=spectrum.fs, width=2.5, height=spectrum.amps, brush=color)
            plot_widget.addItem(bar_graph)
        else:
            bar_graph = pg.BarGraphItem(x=spectrum.fs[:limit], width=2.5, height=spectrum.amps[:limit], brush=color)
            plot_widget.addItem(bar_graph)

    @staticmethod
    def plot_values(window, values, name):
        window.round_dictionary(values, 2)
        getattr(window, name + 'TotalRmsValue').display(values['t_rms'])
        getattr(window, name + 'TotalHarmDistValue').display(values['t_h_dist'])
        getattr(window, name + 'FirstHarmRmsValue').display(values['h1_rms'])
        getattr(window, name + 'FirstHarmAmpValue').display(values['h1_amp'])
        getattr(window, name + 'SecondHarmRmsValue').display(values['h2_rms'])
        getattr(window, name + 'SecondHarmAmpValue').display(values['h2_amp'])
        getattr(window, name + 'ThirdHarmRmsValue').display(values['h3_rms'])
        getattr(window, name + 'ThirdHarmAmpValue').display(values['h3_amp'])

    @staticmethod
    def load_wave_pair_wrapper_csv(data_location, filename):
        directory = os.fsencode(data_location)
        _filename = os.fsencode(filename)
        filepath = data_location + filename

        tension_wave = read_csv(filepath, data_col='tension')
        current_wave = read_csv(filepath, data_col='current')
        tension_wave_wrapper = WaveWrapper(tension_wave, 50.0)
        current_wave_wrapper = WaveWrapper(current_wave, 50.0)
        return WavePairWrapper(tension_wave_wrapper, current_wave_wrapper)

    @staticmethod
    def load_wave_pair_wrapper_chunkfile(data_location, filename):
        # data_location = 'data/input/'

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
        big_signal_chunk = sum(signal_chunks)
        return big_signal_chunk.get_wave_pair_wrapper()
        # return signal_chunks[0].get_wave_pair_wrapper()





    @staticmethod
    def round_dictionary(dictionary, digits=0):
        for k, v in dictionary.items():
            if isinstance(v, Number):
                dictionary[k] = round(v, digits)
