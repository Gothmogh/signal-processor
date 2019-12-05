import math
import threading

from utils import inputsignal
from utils import wavewrapper
from matplotlib import pyplot

base_sig_freq = 50.0
amplitude_scale_factor = 0.01
# amplitude_scale_factor = 1.0 / 10000.0


class SignalStreamProcessor(threading.Thread):

    def __init__(self, _input_signal_stream=None, _buffer_size=500):
        if not isinstance(_input_signal_stream, inputsignal.InputSignalStream):
            raise Exception("_input_signal_stream must be an InputSignalStream")
        if not isinstance(_buffer_size, int):
            raise Exception("_buffer_size must be an integer")
        threading.Thread.__init__(self)
        self.__input_signal_stream = _input_signal_stream
        self.__buffer_size = _buffer_size
        self.__buffer = []
        self.__results = []

    def set_input_signal_stream(self, _input_signal_stream):
        self.__input_signal_stream = _input_signal_stream

    def run(self):
        while True:
            _wave_pair_wrappers = []
            while len(_wave_pair_wrappers):
                _wave_pair_wrappers.append(self.__input_signal_stream.get_chunks().wave_pair_wrapper)
                # pd.DataFrame(data=_chunks[0:, 1:], index=_chunks[0:, 0])
                for _wave_pair_wrapper in _wave_pair_wrappers:
                    self.calculate_and_print(_wave_pair_wrapper)

    @staticmethod
    def calculate_and_print(_wave_pair_wrapper):
        if not isinstance(_wave_pair_wrapper, wavewrapper.WavePairWrapper):
            raise Exception("_wave_pair_wrapper must be an WavePairWrapper")

        tension_wrapper = _wave_pair_wrapper.get_wave_a_wrapper()
        current_wrapper = _wave_pair_wrapper.get_wave_b_wrapper()

        _wave_pair_wrapper = wavewrapper.WavePairWrapper(tension_wrapper, current_wrapper)

        signal_output_template = """
        
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
                          'h1_rms': tension_wrapper.hn_rms(), 'h2_amp': tension_wrapper.hn_amp(n=2, ),
                          'h2_rms': tension_wrapper.hn_rms(n=2, ), 'h3_amp': tension_wrapper.hn_amp(n=3, ),
                          'h3_rms': tension_wrapper.hn_rms(n=3, ), 't_h_dist': tension_wrapper.t_h_dist(n_max=3, )}

        current_output = {'signal': 'Corriente', 't_rms': current_wrapper.t_rms(), 'h1_amp': current_wrapper.hn_amp(),
                          'h1_rms': current_wrapper.hn_rms(), 'h2_amp': current_wrapper.hn_amp(n=2, ),
                          'h2_rms': current_wrapper.hn_rms(n=2, ), 'h3_amp': current_wrapper.hn_amp(n=3, ),
                          'h3_rms': current_wrapper.hn_rms(n=3, ), 't_h_dist': current_wrapper.t_h_dist(n_max=3, )}

        power_output = {}

        phi = _wave_pair_wrapper.phase_shift()
        power_output['phi'] = phi
        power_output['cos_phi'] = math.cos(phi)

        p = _wave_pair_wrapper.active_power()

        power_output['s_h1'] = _wave_pair_wrapper.apparent_power_hn(n=1, )
        power_output['q_h1'] = _wave_pair_wrapper.reactive_power_hn(n=1, )
        power_output['p'] = p

        power_output['s_t'] = _wave_pair_wrapper.apparent_t_power()
        power_output['q_t'] = _wave_pair_wrapper.reactive_t_power()

        power_output['power_factor'] = _wave_pair_wrapper.power_factor()

        print(signal_output_template % tension_output)
        print(signal_output_template % current_output)
        print(power_output_template % power_output)



        # plot_duration = 0.125
        #
        # segment = tension_wave.segment(start=0, duration=plot_duration)
        # pyplot.subplot(5, 1, 1)
        # segment.plot()
        # pyplot.ylabel("Signal amp (V)")
        #
        # base_sig_freq = 50
        #
        # base_wave = util.extract_harmonic_wave(tension_wave.make_spectrum(), base_sig_freq)
        # base_segment = base_wave.segment(start=0, duration=plot_duration)
        # pyplot.subplot(5, 1, 2)
        # base_segment.plot()
        # pyplot.ylabel("B-freq amp (V)")
        #
        # first_harm_wave = util.extract_harmonic_wave(tension_wave.make_spectrum(), base_sig_freq, 2)
        # first_harm_segment = first_harm_wave.segment(start=0, duration=plot_duration)
        # pyplot.subplot(5, 1, 3)
        # first_harm_segment.plot()
        # pyplot.ylabel("1-harm amp (V)")
        #
        # second_harm_wave = util.extract_harmonic_wave(tension_wave.make_spectrum(), base_sig_freq, 3)
        # second_harm_segment = second_harm_wave.segment(start=0, duration=plot_duration)
        # pyplot.subplot(5, 1, 4)
        # second_harm_segment.plot()
        # pyplot.ylabel("2-harm amp (V)")

        # tension_spectrum = tension_wave.make_spectrum()
        # tension_spectrum.plot()
        # pyplot.title('Full signal and decomposition')

        #
        # pyplot.show()
