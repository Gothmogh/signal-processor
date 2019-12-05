import numpy as np
from utils import thinkdsp as dsp


def extract_harmonic_wave(_spectrum, _base_freq, n=1):
    if not isinstance(_spectrum, dsp.Spectrum):
        raise Exception("extract_harmonic method expects Spectrum object.")
    if _base_freq <= 0.0:
        raise Exception("base_freq must be a positive number.")
    freq = _base_freq * n
    _spectrum.low_pass(freq)
    _spectrum.high_pass(freq)
    return _spectrum.make_wave()


def find_nearest_idx(spectrum, fund_freq, n):
    _idx = (np.abs(spectrum.fs - fund_freq * n)).argmin()
    return _idx


def find_nearest_freq(spectrum, fund_freq, n):
    _idx = find_nearest_idx(spectrum, fund_freq, n)
    return spectrum.fs[_idx]


def cross(series, cross=0, direction='cross'):
    """
    Given a Series returns all the index values where the data values equal 
    the 'cross' value. 

    Direction can be 'rising' (for rising edge), 'falling' (for only falling 
    edge), or 'cross' for both edges
    """
    # Find if values are above or bellow yvalue crossing:
    above=series.values > cross
    below=np.logical_not(above)
    left_shifted_above = above[1:]
    left_shifted_below = below[1:]
    x_crossings = []
    # Find indexes on left side of crossing point
    if direction == 'rising':
        idxs = (left_shifted_above & below[0:-1]).nonzero()[0]
    elif direction == 'falling':
        idxs = (left_shifted_below & above[0:-1]).nonzero()[0]
    else:
        rising = left_shifted_above & below[0:-1]
        falling = left_shifted_below & above[0:-1]
        idxs = (rising | falling).nonzero()[0]

    # Calculate x crossings with interpolation using formula for a line:
    x1 = series.index.values[idxs]
    x2 = series.index.values[idxs+1]
    y1 = series.values[idxs]
    y2 = series.values[idxs+1]
    x_crossings = (cross-y1)*(x2-x1)/(y2-y1) + x1

    return x_crossings