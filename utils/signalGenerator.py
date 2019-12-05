import math
import thinkdsp as thinkdsp
import matplotlib.pyplot as pyplot

base_sig_freq = 50.0
base_sig_w = base_sig_freq * thinkdsp.PI2
base_sig_period = 1.0 / base_sig_freq

sample_rate = 2000.0
sample_rate_w = sample_rate * thinkdsp.PI2
sample_rate_period = 1.0 / sample_rate

initial_phase_deg = -90.0
initial_phase_rad = thinkdsp.PI2 * initial_phase_deg / 360.0

base_sig_amp_ef = 220.0
base_sig_amp = base_sig_amp_ef * math.sqrt(2)

first_harm_amp_ef = 100.0
first_harm_amp = first_harm_amp_ef * math.sqrt(2)

second_harm_amp_ef = 50.0
second_harm_amp = second_harm_amp_ef * math.sqrt(2)

base_sig = thinkdsp.SinSignal(freq=base_sig_freq, amp=base_sig_amp, offset=initial_phase_rad)
first_harm_sig = thinkdsp.SinSignal(freq=base_sig_freq * 2, amp=first_harm_amp, offset=initial_phase_rad)
second_harm_sig = thinkdsp.SinSignal(freq=base_sig_freq * 3, amp=second_harm_amp, offset=initial_phase_rad)
mix = base_sig + first_harm_sig + second_harm_sig
wave = mix.make_wave(duration=10, start=0, framerate=sample_rate)

# wave.write('sampleSignal.wav')
# period = mix.period
# segment = wave.segment(start=0, duration=period * 3)
#
# def stretch(wave, factor=1.0):
#     wave.ts = wave.ts * factor
#     wave.framerate = wave.framerate * factor
#     return wave
#
#
# # stretched = stretch(segment, 1.5)
# # stretched.plot()
#
spectrum = wave.make_spectrum()
spectrum.plot()
pyplot.show()
#
#
# def extract_harmonic_wave(_spectrum, _base_freq, n=1):
#     if not isinstance(_spectrum, thinkdsp.Spectrum):
#         raise Exception("extract_harmonic method expects Spectrum object.")
#     if _base_freq <= 0.0:
#         raise Exception("base_freq must be a positive number.")
#     freq = _base_freq * n
#     _spectrum.low_pass(freq)
#     _spectrum.high_pass(freq)
#     return _spectrum.make_wave()
#
#
# pyplot.subplot(4, 1, 1)
# segment.plot()
# pyplot.ylabel("Signal amp (V)")
#
# base_wave = extract_harmonic_wave(wave.make_spectrum(), base_sig_freq)
# base_segment = base_wave.segment(start=0, duration=period * 3)
# pyplot.subplot(4, 1, 2)
# base_segment.plot()
# pyplot.ylabel("B-freq amp (V)")
#
# first_harm_wave = extract_harmonic_wave(wave.make_spectrum(), base_sig_freq, 2)
# first_harm_segment = first_harm_wave.segment(start=0, duration=period * 3)
# pyplot.subplot(4, 1, 3)
# first_harm_segment.plot()
# pyplot.ylabel("1-harm amp (V)")
#
# second_harm_wave = extract_harmonic_wave(wave.make_spectrum(), base_sig_freq, 3)
# second_harm_segment = second_harm_wave.segment(start=0, duration=period * 3)
# pyplot.subplot(4, 1, 4)
# second_harm_segment.plot()
# pyplot.ylabel("2-harm amp (V)")
#
# # pyplot.title('Full signal and decomposition')
# pyplot.show()
