import threading
import traceback
import numpy as np
from socket import *
from utils import thinkdsp
from utils import wavewrapper
from utils import util
from bitstring import BitArray
from matplotlib import pyplot
import struct
import math
import time
import curses
import os
import matplotlib
tension_multiplier = 1.0
current_multiplier = 1.0
frame_rate = 2000
fund_freq = 50.0
# matplotlib.use('Agg')


class InputSignalStream:
    """ Represents a 'continuous' stream of both signals """

    def __init__(self):
        self.__chunks_array = []

    def add_chunk(self, chunk):
        self.__chunks_array.append(chunk)

    def get_chunks(self):
        __ret = self.__chunks_array
        self.__chunks_array = []
        return __ret


class InputSignalChunk:
    """ Wraps WaveWrappersObjects """

    def __init__(self, _timestamp, _tension_data, _current_data, _scale_factor):
        if not isinstance(_timestamp, int):
            raise Exception("_timestamp must be an integer")

        if not isinstance(_tension_data, list):
            raise Exception("_tension_data must be a ndarray")

        if not isinstance(_current_data, list):
            raise Exception("_current_data must be a ndarray")

        if not len(_tension_data) == len(_current_data):
            raise Exception("_tension_data and _current_data must")
        self.__timestamp = _timestamp
        # self.__tension_data = ((np.asanyarray(_tension_data) * 3.3 / 4096) - 1.65) * (220.0 / 1.025)
        self.__tension_data = ((np.asanyarray(_tension_data) * 3.3 / 4095) - 1.645) * (215.2 / 1.012)
        # self.__tension_data = ((np.asanyarray(_tension_data) * 3.3 / 4095) - 1.65) * (220.0 / 0.456)
        # self.__current_data = ((np.asanyarray(_current_data) * 3.3 / 4096) - 1.65) * 5
        self.__current_data = ((np.asanyarray(_current_data) * 3.3 / 4095) - 1.645) * 5
        # self.__current_data = ((np.asanyarray(_current_data) * 3.3 / 4095) - 1.65) * (5 / 0.456)
        self.__frame_rate = frame_rate
        self.__sample_period = 1 / self.__frame_rate
        self.__frames = len(_tension_data)
        self.__scale_factor = _scale_factor
        _start = self.__timestamp
        _step = self.__frame_rate * (10 ** 6)
        _end = self.__timestamp + self.__frames * _step
        self.__ts = np.arange(_start, _end, step=_step)
        self.__generate_wave_pair_wrapper()
        # _tension_wave = thinkdsp.Wave(self.__tension_data, ts=_ts, framerate=self.__frame_rate)
        # _tension_wave_wrapper = wavewrapper.WaveWrapper(_tension_wave, util.find_nearest_freq(_tension_wave.make_spectrum(), fund_freq, 1), _scale_factor)
        # _current_wave = thinkdsp.Wave(self.__current_data, ts=_ts, framerate=self.__frame_rate)
        # _current_wave_wrapper = wavewrapper.WaveWrapper(_current_wave, util.find_nearest_freq(_current_wave.make_spectrum(), fund_freq, 1), _scale_factor)
        #
        # plot_duration = 0.125
        # # pyplot.close('all')
        # # #
        # # pyplot.subplot(4, 1, 1)
        # # # tension_segment = _tension_wave.segment(start=0, duration=plot_duration)
        # # # tension_segment.plot()
        # # _tension_wave.plot()
        # # pyplot.subplot(4, 1, 2)
        # # _tension_wave.make_spectrum().plot()
        # #
        # # pyplot.subplot(4, 1, 3)
        # # _current_wave.plot()
        # # pyplot.subplot(4, 1, 4)
        # # # current_segment = _current_wave.segment(start=0, duration=plot_duration)
        # # # current_segment.plot()
        # # _current_wave.make_spectrum().plot()
        # #
        # # pyplot.show()
        #
        # self._wave_pair = wavewrapper.WavePairWrapper(_tension_wave_wrapper, _current_wave_wrapper)

    def __generate_wave_pair_wrapper(self):
        _tension_wave = thinkdsp.Wave(self.__tension_data, ts=self.__ts, framerate=self.__frame_rate)
        _tension_wave_wrapper = wavewrapper.WaveWrapper(_tension_wave, util.find_nearest_freq(_tension_wave.make_spectrum(), fund_freq, 1), self.__scale_factor)
        _current_wave = thinkdsp.Wave(self.__current_data, ts=self.__ts, framerate=self.__frame_rate)
        _current_wave_wrapper = wavewrapper.WaveWrapper(_current_wave, util.find_nearest_freq(_current_wave.make_spectrum(), fund_freq, 1), self.__scale_factor)
        self._wave_pair = wavewrapper.WavePairWrapper(_tension_wave_wrapper, _current_wave_wrapper)

    def wave_pair_wrapper(self):
        return self._wave_pair

    def append(self, _signal_chunk):
        if not isinstance(_signal_chunk, InputSignalChunk):
            raise Exception("_signal_chunk must be an InputSignalChunk")
        np.append(self.__tension_data, _signal_chunk.__tension_data)
        np.append(self.__current_data, _signal_chunk.__current_data)
        np.append(self.__ts, _signal_chunk.__ts)
        self.__frames = len(self.__tension_data)


class InputSignalServer(threading.Thread):

    def __init__(self, _input_signal_stream, _scale_factor):
        threading.Thread.__init__(self)
        self.__input_signal_stream = _input_signal_stream
        self.__scale_factor = _scale_factor

    def run(self):
        _server_socket = socket(AF_INET, SOCK_DGRAM)

        # Assign IP address and port number to socket
        _server_socket.bind(('', 3000))

        # while True:
        #     received = _server_socket.recv(1024)
        #     test = binascii.hexlify(received)
        #     time.sleep(1)
        #     print '=========================='
        #     print test
        #     print '=========================='

        MAXSIZE = 64000
        TIMEOUT = 1.0
        INT = 3.0  # interval in seconds

        # create udp_socket
        # last = time.time() - INT
        # _server_socket.settimeout(TIMEOUT)
        i = 0
        arr = []
        _packets = []

        buffer_size = 1

        # while True:
        total_signal_chunks = None
        for i in range(0, buffer_size):
            try:
                _packet = _server_socket.recv(MAXSIZE)

                # _packets.append(bytearray(_packet))
                #
                # new_file = open(file='package' + str(i), mode='wb')
                # new_file.write(_packet)
                # new_file.close()
                # # print '=========================='
                # # print '--> ' + str(i)
                # # print '--------------------------'
                # # print test
                # # print '=========================='
                # i += 1
                # # arr.append(time.asctime())
                # # time.sleep(1)

                signal_chunk = self.__udp_to_signal_chunk(bytearray(_packet), self.__scale_factor)
                if total_signal_chunks is None:
                    total_signal_chunks = signal_chunk
                else:
                    total_signal_chunks.append(signal_chunk)

                # curses.wrapper(self.calculate_and_print, wave_pair_wrapper)
                # chunk = self.__udp_to_signal_chunk(bytearray(_packet), self.__scale_factor)
                # chunk.wave_pair_wrapper().get_wave_a_wrapper().get_fund_wave_wrapper().get_wave().make_spectrum().plot()
                # pyplot.show()
            except _server_socket.gettimeout():
                # handle recv timeout
                continue  # or break, or return
            except OSError:
                # handle recv error (Python 3.3+)
                break  # or continue, or return
            except Exception as err:
                print(err)
                traceback.print_tb(err.__traceback__)
                continue
            # now = time.time()
            # print time.asctime()
            # if now - last >= INT:
            #     # process the packet
            #     last = now

        self.calculate_and_print(total_signal_chunks.wave_pair_wrapper())

        # print(np.array(arr))
        # for _packet in _packets:
        #     self.calculate_and_print(self.__udp_to_signal_chunk(_packet, self.__scale_factor).wave_pair_wrapper())
            # self.__input_signal_stream.add_chunk(self.__udp_to_signal_chunk(_packet))

        # print np.diff(arr).mean()

    @staticmethod
    def __udp_to_signal_chunk(_udp_packet, _scale_factor):
        # print(len(_udp_packet))
        timestamp = struct.unpack_from('I', _udp_packet[0:4])[0]
        # iterator = struct.iter_unpack('H', _udp_packet[4:6])
        readings = []

        # print(np.array(list(iterator)).flatten())
        # for element in iterator:
        #     print(element)

        # print readings
        # bitarray = BitArray(_udp_packet[0:4])

        # data = BitArray(_udp_packet[4:])
        # print(data.bin)
        for i in range(4, len(_udp_packet), 2):
            data = BitArray(_udp_packet[i:i + 2])
            int_data = int(data.bin, 2)
            # print(int_data)
            readings.append(int_data)
        # print(len(_udp_packet))

        even_readings = readings[0:][::2]
        odd_readings = readings[1:][::2]
        # print(even_readings)
        # print(odd_readings)

        return InputSignalChunk(timestamp, even_readings, odd_readings, _scale_factor)
        # return InputSignalChunk(timestamp, odd_readings, even_readings, _scale_factor)

    def get_input_signal_stream(self):
        return self.__input_signal_stream

    @staticmethod
    def calculate_and_print(_wave_pair_wrapper):
        if not isinstance(_wave_pair_wrapper, wavewrapper.WavePairWrapper):
            raise Exception("_wave_pair_wrapper must be an WavePairWrapper")

        tension_wrapper = _wave_pair_wrapper.get_wave_a_wrapper()
        base_tension_wrapper = tension_wrapper.get_fund_wave_wrapper()
        current_wrapper = _wave_pair_wrapper.get_wave_b_wrapper()
        base_current_wrapper = current_wrapper.get_fund_wave_wrapper()

        _wave_pair_wrapper = wavewrapper.WavePairWrapper(tension_wrapper, current_wrapper)
        # base_pair_wrapper = wavewrapper.WavePairWrapper(base_tension_wrapper, base_current_wrapper)

        signal_output_template = """
            =======================================
            Senial                          : %(signal)s
            =======================================
            Valor eficaz total              : %(t_rms)s
            ---------------------------------------
            Amplitud fundamental            : %(h1_amp)s
            Valor eficaz fundamental        : %(h1_rms)s
            Amplitud 2do armonico           : %(h2_amp)s
            Valor eficaz 2do armonico       : %(h2_rms)s
            Amplitud 3er armonico           : %(h3_amp)s
            Valor eficaz 3er armonico       : %(h3_rms)s
            ---------------------------------------
            Distorsion armonica total       : %(t_h_dist)s
            =======================================
            """

        power_output_template = """
            =======================================
            Potencia
            =======================================
            Phi                             : %(phi)s PI
            Cos(phi)                        : %(cos_phi)s
            Potencia activa                 : %(p)s
            Potencia aparente fundamental   : %(s_h1)s
            Potencia reactiva fundamental   : %(q_h1)s
            Potencia aparente total         : %(s_t)s
            Potencia reactiva total         : %(q_t)s
            Factor de potencia              : %(power_factor)s
            =======================================
            """

        tension_output = {'signal': 'Tension', 't_rms': tension_wrapper.t_rms(), 'h1_amp': tension_wrapper.hn_amp(),
                          'h1_rms': tension_wrapper.hn_rms(), 'h2_amp': tension_wrapper.hn_amp(n=2),
                          'h2_rms': tension_wrapper.hn_rms(n=2), 'h3_amp': tension_wrapper.hn_amp(n=3),
                          'h3_rms': tension_wrapper.hn_rms(n=3), 't_h_dist': tension_wrapper.t_h_dist(n_max=3)}

        current_output = {'signal': 'Corriente', 't_rms': current_wrapper.t_rms(), 'h1_amp': current_wrapper.hn_amp(),
                          'h1_rms': current_wrapper.hn_rms(), 'h2_amp': current_wrapper.hn_amp(n=2),
                          'h2_rms': current_wrapper.hn_rms(n=2), 'h3_amp': current_wrapper.hn_amp(n=3),
                          'h3_rms': current_wrapper.hn_rms(n=3), 't_h_dist': current_wrapper.t_h_dist(n_max=3)}

        phi = _wave_pair_wrapper.phase_shift()
        p = _wave_pair_wrapper.active_power()

        power_output = {'phi': phi, 'cos_phi': math.cos(phi), 's_h1': _wave_pair_wrapper.apparent_power_hn(n=1),
                        'q_h1': _wave_pair_wrapper.reactive_power_hn(n=1), 'p': p,
                        's_t': _wave_pair_wrapper.apparent_t_power(), 'q_t': _wave_pair_wrapper.reactive_t_power(),
                        'power_factor': _wave_pair_wrapper.power_factor()}

        # output = signal_output_template % tension_output
        # window.addstr(str(output))
        # window.refresh()
        os.system('clear')
        print(signal_output_template % tension_output)
        print(signal_output_template % current_output)
        print(power_output_template % power_output)

        pyplot.close('all')
        #
        pyplot.subplot(4, 1, 1)
        # tension_segment = _tension_wave.segment(start=0, duration=plot_duration)
        # tension_segment.plot()
        tension_wrapper.get_wave().plot()
        pyplot.subplot(4, 1, 2)
        tension_wrapper.get_wave().make_spectrum().plot()

        pyplot.subplot(4, 1, 3)
        current_wrapper.get_wave().plot()
        pyplot.subplot(4, 1, 4)
        # current_segment = _current_wave.segment(start=0, duration=plot_duration)
        # current_segment.plot()
        current_wrapper.get_wave().make_spectrum().plot()

        pyplot.show()
