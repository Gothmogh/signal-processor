from utils import thinkdsp
from utils import util
import numpy as np
import math
from scipy.signal import correlate


class WaveWrapper:
    """ Wraps ThinkDSP Wave object """

    def __init__(self, _wave, _fund_freq):
        # if not isinstance(_wave, thinkdsp.Wave):
        #     raise Exception("WaveWrapper must be instanced with a valid Wave object")

        if not isinstance(_fund_freq, float):
            raise Exception("_base_freq must be a float value")

        self.__fund_freq = _wave.make_spectrum().fs[util.find_nearest_idx(_wave.make_spectrum(), _fund_freq, 1)]
        self.__wave = _wave
        # self.__spectrum = _wave.make_spectrum()

    def __add__(self, other):
        if other == 0:
            return self
        if not isinstance(other, WaveWrapper):
            raise Exception("Unsupported operation.")

        new_wave = self.__wave + other.__wave

        return WaveWrapper(new_wave, self.__fund_freq)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def get_wave(self):
        return self.__wave

    def get_fund_freq(self):
        return self.__fund_freq

    def hn_amp(self, n=1):
        if not isinstance(n, int):
            raise Exception("n must be an integer value")
        if n < 1:
            raise Exception("n must be greater than 0")

        h_wave = self.hn_wave(n=n)
        h_spectrum = h_wave.make_spectrum()
        _idx = util.find_nearest_idx(h_spectrum, self.__fund_freq, n)

        return h_spectrum.amps[_idx].item()

    def hn_rms(self, n=1):

        return self.hn_amp(n=n) / math.sqrt(2)

    def t_rms(self):
        # _zero_crossings = np.where(np.diff(np.sign(self.__wave.ys)))[0]
        # if len(_zero_crossings) == 0:
        #     return 1.0
        # _samples_per_period = math.floor(np.mean(np.diff(_zero_crossings)))
        #
        # _full_cycles = len(self.__wave.ys) // _samples_per_period
        #
        # _full_cycles = (_full_cycles // 2) * 2
        #
        # _max_idx = _full_cycles * _samples_per_period
        #
        # _values = self.__wave.ys[:_max_idx]
        _sqr_values = self.__wave.ys ** 2
        _sqr_sum = np.sum(_sqr_values)

        _r = math.sqrt(_sqr_sum / len(_sqr_values))

        return _r

    def hn_wave(self, n=1):
        _spectrum = self.__wave.make_spectrum()
        freq = util.find_nearest_freq(_spectrum, self.__fund_freq, n)
        _spectrum.low_pass(freq)
        _spectrum.high_pass(freq)
        _wave = _spectrum.make_wave()
        _wave.ys = _wave.ys * (len(self.__wave.ys) / 2)

        return _wave

    def t_h_dist(self, n_max=2):
        _temp = []
        for i in range(1, n_max):
            _temp.append(self.hn_rms(i + 1))

        _sqr_h_amps = np.array(_temp) ** 2
        _sqr_sum = np.sum(_sqr_h_amps)
        _fund_rms = self.hn_rms(n=1)
        if _fund_rms == 0:
            _r = "inf"
        else:
            _r = math.sqrt(_sqr_sum) / self.hn_rms(n=1)

        return _r

    def get_fund_wave_wrapper(self):
        _spectrum = self.__wave.make_spectrum()
        _idx = util.find_nearest_idx(_spectrum, self.__fund_freq, 1)
        _approx_freq = _spectrum.fs[_idx]
        _wave = util.extract_harmonic_wave(_spectrum, _approx_freq)
        return WaveWrapper(_wave, _approx_freq)


class WavePairWrapper:
    """ Wraps a pair of ThinkDSP Wave objects """

    def __init__(self, _wave_a, _wave_b):
        # if not isinstance(_wave_a, WaveWrapper) or not isinstance(_wave_b, WaveWrapper):
        #     raise Exception("WavePairWrapper must be instanced with a valid Wave object")
        self._wave_a = _wave_a
        self._wave_b = _wave_b

    def __add__(self, other):
        if other == 0:
            return self
        if not isinstance(other, WavePairWrapper):
            raise Exception("Unsupported operation.")
        new_wave_a = self._wave_a + other._wave_a
        new_wave_b = self._wave_b + other._wave_b

        return WavePairWrapper(new_wave_a, new_wave_b)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
        
    def get_wave_a_wrapper(self):
        return self._wave_a

    def get_wave_b_wrapper(self):
        return self._wave_b

    def time_shift(self):
        _wave_a_ys = self._wave_a.get_wave().ys
        _wave_b_ys = self._wave_b.get_wave().ys
        _ts = self._wave_a.get_wave().ts
        _nsamples = _wave_a_ys.size

        # calculate cross correlation of the two signals
        _xcorr = correlate(_wave_a_ys, _wave_b_ys)
        # _xcorr = correlate(_wave_b_ys, _wave_a_ys)
        # _xcorr = correlate(current_ys, tension_ys)

        # The peak of the cross-correlation gives the shift between the two signals
        # The _xcorr array goes from -nsamples to nsamples
        _dt = np.linspace(-_ts[-1], _ts[-1], 2 * _nsamples - 1)
        _recovered_time_shift = _dt[_xcorr.argmax()]

        return _recovered_time_shift

    def phase_shift(self):
        wave_a_spectrum = self._wave_a.get_wave().make_spectrum()
        wave_a_fund_freq = self._wave_a.get_fund_freq()
        wave_a_freq_idx = util.find_nearest_idx(wave_a_spectrum, wave_a_fund_freq, 1)
        wave_a_fund_phase = wave_a_spectrum.angles[wave_a_freq_idx]
        
        wave_b_spectrum = self._wave_b.get_wave().make_spectrum()
        wave_b_fund_freq = self._wave_b.get_fund_freq()
        wave_b_freq_idx = util.find_nearest_idx(wave_b_spectrum, wave_b_fund_freq, 1)
        wave_b_fund_phase = wave_b_spectrum.angles[wave_b_freq_idx]
        
        return wave_b_fund_phase - wave_a_fund_phase
        # return wave_a_fund_phase - wave_b_fund_phase
        # _period = 1.0 / self._wave_a.get_fund_freq()
        # # force the phase shift to be in [-pi:pi]
        # _recovered_phase_shift = 2 * math.pi * (((0.5 + self.time_shift() / _period) % 1.0) - 0.5)
        # 
        # return _recovered_phase_shift

    def apparent_power_hn(self, n=1):
        _wave_a_hn_rms = self._wave_a.hn_rms(n=n)
        _wave_b_hn_rms = self._wave_b.hn_rms(n=n)

        _r = _wave_a_hn_rms * _wave_b_hn_rms

        return _r

    def reactive_power_hn(self, n=1):
        return math.sin(self.phase_shift()) * self.apparent_power_hn(n=n)

    def apparent_t_power(self):
        _wave_a_t_rms = self._wave_a.t_rms()
        _wave_b_t_rms = self._wave_b.t_rms()

        _r = _wave_a_t_rms * _wave_b_t_rms

        return _r

    def reactive_t_power(self):
        sqr_sum = self.apparent_t_power() ** 2 - self.active_power() ** 2
        if sqr_sum < 0:
            return None
        return math.sqrt(self.apparent_t_power() ** 2 - self.active_power() ** 2)

    def active_power(self):
        return math.cos(self.phase_shift()) * self.apparent_power_hn(1)

    def power_factor(self):
        return self.active_power() / self.apparent_t_power()
