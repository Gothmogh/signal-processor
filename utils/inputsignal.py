import collections
import math
import os
import pickle
import threading
import time
import traceback
from socket import *

import numpy as np

from utils import thinkdsp
from utils import util
from utils import wavewrapper

tension_multiplier = (230.0 * math.sqrt(2) / 1.6)
tension_percent_error = 0.07
current_multiplier = 5.0
current_percent_error = 0.02

frame_rate = 2000
fund_freq = 50.0


class InputSignalChunk:
    """ Wraps WaveWrappersObjects """
    def reload(self):
        return InputSignalChunk(self.__timestamp, self.__tension_data.tolist(), self.__current_data.tolist())

    def __init__(self, _timestamp, _tension_data=None, _current_data=None, _data_array=None):

        if not isinstance(_timestamp, int):
            raise Exception("_timestamp must be an integer")

        self.__timestamp = _timestamp
        self.__frame_rate = frame_rate
        self.__sample_period = 1 / self.__frame_rate

        if _data_array is None:
            if _tension_data is None or not isinstance(_tension_data, list):
                raise Exception("_tension_data must be a ndarray")

            if _current_data is None or not isinstance(_current_data, list):
                raise Exception("_current_data must be a ndarray")

            if not len(_tension_data) == len(_current_data):
                raise Exception("_tension_data and _current_data must be same length")

            self.__frames = len(_tension_data)

            self.__tension_data = ((np.asanyarray(_tension_data) * (3.3 / 4096)) - 1.65) * tension_multiplier * (1 + tension_percent_error)
            self.__current_data = ((np.asanyarray(_current_data) * (3.3 / 4096)) - 1.635) * current_multiplier * (1 + current_percent_error)

            # self.__tension_data = ((np.asanyarray(_tension_data) * (3.3 / 4096)) - 1.65) * tension_multiplier
            # self.__current_data = ((np.asanyarray(_current_data) * (3.3 / 4096)) - 1.65) * current_multiplier

            _step = self.__sample_period
            _end = self.__frames * _step
            self.__ts = np.add(np.arange(0, _end, step=_step), self.__timestamp / (10 ** 6))

            wtype = np.dtype([('ts', float), ('tension', float), ('current', float)])
            length = max((len(self.__ts), len(self.__tension_data), len(self.__current_data)))
            w = np.empty(length, dtype=wtype)
            w['ts'] = self.__ts
            w['tension'] = self.__tension_data
            w['current'] = self.__current_data

            self._data_array = w
        else:
            self.__frames = len(_data_array)
            self.__ts = _data_array['ts']
            self.__tension_data = _data_array['tension']
            self.__current_data = _data_array['current']
            self._data_array = _data_array

        # _start = self.__timestamp / (10 ** 6)
        # # _step = self.__frame_rate * (10 ** 6)
        # _step = self.__sample_period
        # _end = _start + self.__frames * _step
        # _ts = np.arange(_start, _end, step=_step)
        # _tension_wave = thinkdsp.Wave(self.__tension_data, ts=_ts, framerate=self.__frame_rate)
        # _tension_wave_wrapper = wavewrapper.WaveWrapper(_tension_wave, util.find_nearest_freq(_tension_wave.make_spectrum(), fund_freq, 1), _scale_factor)
        # _current_wave = thinkdsp.Wave(self.__current_data, ts=_ts, framerate=self.__frame_rate)
        # _current_wave_wrapper = wavewrapper.WaveWrapper(_current_wave, util.find_nearest_freq(_current_wave.make_spectrum(), fund_freq, 1), _scale_factor)

        plot_duration = 0.125
        # pyplot.close('all')
        # #
        # pyplot.subplot(4, 1, 1)
        # # tension_segment = _tension_wave.segment(start=0, duration=plot_duration)
        # # tension_segment.plot()
        # _tension_wave.plot()
        # pyplot.subplot(4, 1, 2)
        # _tension_wave.make_spectrum().plot()
        #
        # pyplot.subplot(4, 1, 3)
        # _current_wave.plot()
        # pyplot.subplot(4, 1, 4)
        # # current_segment = _current_wave.segment(start=0, duration=plot_duration)
        # # current_segment.plot()
        # _current_wave.make_spectrum().plot()
        #
        # pyplot.show()

        # self._wave_pair_wrapper = wavewrapper.WavePairWrapper(_tension_wave_wrapper, _current_wave_wrapper)

    def _ts(self):

        if not hasattr(self, '__ts') or self.__ts is None:

            _start = self.__timestamp / (10 ** 6)
            # _step = self.__frame_rate * (10 ** 6)
            _step = self.__sample_period
            _end = _start + self.__frames * _step
            self.__ts = np.arange(_start, _end, step=_step)
            while len(self.__ts) > self.__frames:
                self.__ts = self.__ts[:-1]

        return self.__ts

    def get_wave_pair_wrapper(self):
        _scale_factor = 1.0

        _tension_wave = thinkdsp.Wave(self.__tension_data, ts=self._ts(), framerate=self.__frame_rate)
        _tension_wave_wrapper = wavewrapper.WaveWrapper(_tension_wave, util.find_nearest_freq(_tension_wave.make_spectrum(), fund_freq, 1))
        _current_wave = thinkdsp.Wave(self.__current_data, ts=self._ts(), framerate=self.__frame_rate)
        _current_wave_wrapper = wavewrapper.WaveWrapper(_current_wave, util.find_nearest_freq(_current_wave.make_spectrum(), fund_freq, 1))

        return wavewrapper.WavePairWrapper(_tension_wave_wrapper, _current_wave_wrapper)

    def __add__(self, other):
        if other == 0:
            return self
        if not isinstance(other, InputSignalChunk):
            raise Exception("Unsupported operation.")
        if self.__frame_rate != other.__frame_rate:
            raise Exception("Unsupported operation.")

        new_data_array = np.hstack((self._data_array, other._data_array))
        new_data_array.sort(order='ts')

        return InputSignalChunk(min(self.__timestamp, other.__timestamp), _data_array=new_data_array)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


# class InputSignalStream:
#     """ Represents a 'continuous' stream of both signals """
#
#     def __init__(self):
#         self.__chunks_buffer = 1
#         self.__chunks_array = collections.deque([], self.__chunks_buffer)
#
#     def add_chunk(self, chunk):
#         self.__chunks_array.append(chunk)
#
#     def get_chunks(self):
#         return self.__chunks_array
#
#     def get_full_wave_pair_wrapper(self):
#         chunks_list = list(self.__chunks_array)
#         wave_pair_wrappers = []
#         for chunk in chunks_list:
#             wave_pair_wrappers.append(chunk.get_wave_pair_wrapper())
#         total_wave_pair_wrapper = None
#         for wave_pair_wrapper in wave_pair_wrappers:
#             if total_wave_pair_wrapper is None:
#                 total_wave_pair_wrapper = wave_pair_wrapper
#             else:
#                 total_wave_pair_wrapper = total_wave_pair_wrapper + wave_pair_wrapper
#
#         return total_wave_pair_wrapper

# class InputSignalServer(threading.Thread):
#
#     def __init__(self, _input_signal_stream):
#         threading.Thread.__init__(self)
#         self.__input_signal_stream = _input_signal_stream
#
#     def run(self):
#         _server_socket = socket(AF_INET, SOCK_DGRAM)
#
#         # Assign IP address and port number to socket
#         _server_socket.bind(('', 3500))
#
#         MAXSIZE = 64000
#         TIMEOUT = 1.0
#         INT = 3.0  # interval in seconds
#
#         # create udp_socket
#         # last = time.time() - INT
#         # _server_socket.settimeout(TIMEOUT)
#         i = 0
#         arr = []
#         _packets = []
#
#         buffer_size = 10
#         _signal_chunks = []
#
#         print("Listening to port 3500")
#
#         while True:
#             for i in range(buffer_size + 1):
#                 try:
#                     _packet = _server_socket.recv(MAXSIZE)
#                     # _packets.append(_packet)
#                     signal_chunk = udp_to_signal_chunk(bytearray(_packet))
#                     _signal_chunks.append(signal_chunk)
#                 except timeout:
#                     # handle recv timeout
#                     continue  # or break, or return
#                 except OSError:
#                     # handle recv error (Python 3.3+)
#                     break  # or continue, or return
#                 except Exception as err:
#                     print(err)
#                     traceback.print_tb(err.__traceback__)
#                     continue
#
#             millis = int(round(time.time() * 1000))
#
#             print("Saving " + str(i) + " packets with timestamp " + str(millis))
#
#             with open('data/input/' + str(millis), 'wb') as data_file:
#                 # pickle.dump(_packets, data_file, pickle.HIGHEST_PROTOCOL)
#                 pickle.dump(_signal_chunks, data_file, pickle.HIGHEST_PROTOCOL)
#
#             _packets = []
#             _signal_chunks = []
#
#
#     def get_input_signal_stream(self):
#         return self.__input_signal_stream
#
#     @staticmethod
#     def calculate_and_print(_wave_pair_wrapper):
#         if not isinstance(_wave_pair_wrapper, wavewrapper.WavePairWrapper):
#             raise Exception("_wave_pair_wrapper must be an WavePairWrapper")
#
#         tension_wrapper = _wave_pair_wrapper.get_wave_a_wrapper()
#         base_tension_wrapper = tension_wrapper.get_fund_wave_wrapper()
#         current_wrapper = _wave_pair_wrapper.get_wave_b_wrapper()
#         base_current_wrapper = current_wrapper.get_fund_wave_wrapper()
#
#         _wave_pair_wrapper = wavewrapper.WavePairWrapper(tension_wrapper, current_wrapper)
#         # base_pair_wrapper = wavewrapper.WavePairWrapper(base_tension_wrapper, base_current_wrapper)
#
#         signal_output_template = """
#             =======================================
#             Senial                          : %(signal)s
#             =======================================
#             Valor eficaz total              : %(t_rms)s
#             ---------------------------------------
#             Amplitud fundamental            : %(h1_amp)s
#             Valor eficaz fundamental        : %(h1_rms)s
#             Amplitud 2do armonico           : %(h2_amp)s
#             Valor eficaz 2do armonico       : %(h2_rms)s
#             Amplitud 3er armonico           : %(h3_amp)s
#             Valor eficaz 3er armonico       : %(h3_rms)s
#             ---------------------------------------
#             Distorsion armonica total       : %(t_h_dist)s
#             =======================================
#             """
#
#         power_output_template = """
#             =======================================
#             Potencia
#             =======================================
#             Phi                             : %(phi)s PI
#             Cos(phi)                        : %(cos_phi)s
#             Potencia activa                 : %(p)s
#             Potencia aparente fundamental   : %(s_h1)s
#             Potencia reactiva fundamental   : %(q_h1)s
#             Potencia aparente total         : %(s_t)s
#             Potencia reactiva total         : %(q_t)s
#             Factor de potencia              : %(power_factor)s
#             =======================================
#             """
#
#         tension_output = {'signal': 'Tension', 't_rms': tension_wrapper.t_rms(), 'h1_amp': tension_wrapper.hn_amp(),
#                           'h1_rms': tension_wrapper.hn_rms(), 'h2_amp': tension_wrapper.hn_amp(n=2),
#                           'h2_rms': tension_wrapper.hn_rms(n=2), 'h3_amp': tension_wrapper.hn_amp(n=3),
#                           'h3_rms': tension_wrapper.hn_rms(n=3), 't_h_dist': tension_wrapper.t_h_dist(n_max=3)}
#
#         current_output = {'signal': 'Corriente', 't_rms': current_wrapper.t_rms(), 'h1_amp': current_wrapper.hn_amp(),
#                           'h1_rms': current_wrapper.hn_rms(), 'h2_amp': current_wrapper.hn_amp(n=2),
#                           'h2_rms': current_wrapper.hn_rms(n=2), 'h3_amp': current_wrapper.hn_amp(n=3),
#                           'h3_rms': current_wrapper.hn_rms(n=3), 't_h_dist': current_wrapper.t_h_dist(n_max=3)}
#
#         phi = _wave_pair_wrapper.phase_shift()
#         p = _wave_pair_wrapper.active_power()
#
#         power_output = {'phi': phi, 'cos_phi': math.cos(phi), 's_h1': _wave_pair_wrapper.apparent_power_hn(n=1),
#                         'q_h1': _wave_pair_wrapper.reactive_power_hn(n=1), 'p': p,
#                         's_t': _wave_pair_wrapper.apparent_t_power(), 'q_t': _wave_pair_wrapper.reactive_t_power(),
#                         'power_factor': _wave_pair_wrapper.power_factor()}
#
#         # output = signal_output_template % tension_output
#         # window.addstr(str(output))
#         # window.refresh()
#         os.system('clear')
#         print(signal_output_template % tension_output)
#         print(signal_output_template % current_output)
#         print(power_output_template % power_output)
#
#         #
#         #
#         # pyplot.subplot(4, 1, 1)
#         # # tension_segment = _tension_wave.segment(start=0, duration=plot_duration)
#         # # tension_segment.plot()
#         # tension_wrapper.get_wave().plot()
#         # pyplot.subplot(4, 1, 2)
#         # tension_wrapper.get_wave().make_spectrum().plot()
#         #
#         # pyplot.subplot(4, 1, 3)
#         # current_wrapper.get_wave().plot()
#         # pyplot.subplot(4, 1, 4)
#         # # current_segment = _current_wave.segment(start=0, duration=plot_duration)
#         # # current_segment.plot()
#         # current_wrapper.get_wave().make_spectrum().plot()
#         #
#         # pyplot.show()
#         # time.sleep(2)
#         # # pyplot.gcf().clear()
#         # # pyplot.clf()
#         # # pyplot.cla()
#         # # pyplot.close()
