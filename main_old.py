import pandas as pd
import numpy as np
import matplotlib.pyplot as pyplot
from utils import signalreader

from utils.util import cross
# import frequency_estimator as freq_est

csv_file = 'data/sampleSignal.csv'

wave_obj = signalreader.read_csv(csv_file, data_col='tension')

full_input_df = pd.read_csv(csv_file, sep=";")
full_input_df = full_input_df.drop(full_input_df[full_input_df.time == 0].index)


tension_df = full_input_df.loc[:,['time','tension']]
current_df = full_input_df.loc[:,['time','current']]

print('Tensiones')
print(tension_df)
print('Corrientes')
print(current_df)
tension_zero_cross_times = pd.DataFrame(cross(tension_df.set_index('time'),direction='rising')).mean()
print('Cruces por cero tension')
print(tension_zero_cross_times)
avg_period = pd.DataFrame(tension_zero_cross_times).apply(lambda x: x.diff()).dropna(axis=0).mean().item()
print('Periodo promedio (us)')
print(avg_period)
print('Frecuencia promedio')
print(1/(avg_period * 10**-6))

print("=============")
print("Ahora con FFT")
print("=============")

n = len(tension_df.tension)
d = 1.0 / 2000.0
print(n)
print(d)
hs = np.fft.rfft(tension_df.tension) / (n / 2)
# hs = np.fft.shrfft(tension_df.tension) / (n * 2)

fs = np.fft.rfftfreq(n, d)
phase = np.angle(fs)
print("Amplitudes")
# print(hs)
amps = np.abs(hs)
# amps = np.positive(amps)
print(amps)
print("Frecuencias")
print(fs * 50.0)

print("Amplitud senial base")
print(amps[1])
# pyplot.plot(fs, phase)
pyplot.plot(fs, amps)


x_recon = np.fft.irfft(hs) * n
t = np.arange(start=0, stop=(n * d) - d, step=d)
# pyplot.plot(t, x_recon)
pyplot.show()
