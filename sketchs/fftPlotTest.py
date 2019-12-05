import numpy as np
import matplotlib.pyplot as plt

t = np.arange(256)
print(np.sin(t))
sp = np.fft.fft(np.sin(t))
freq = np.fft.fftfreq(t.shape[-1])
plt.plot(freq, sp.real, freq, sp.imag)

plt.show()