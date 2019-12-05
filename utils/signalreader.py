import pandas as pd
import utils.thinkdsp as dsp


def read_csv(file="data/sampleSignal.csv", sep=";", header=0, time_col='time', data_col='data', framerate=2000):

    full_input_df = pd.read_csv(file, header=header, sep=sep)

    data = full_input_df.loc[:, [data_col]].transpose().values.flatten()
    time = full_input_df.loc[:, [time_col]].transpose().values.flatten()

    return dsp.Wave(data, ts=time, framerate=framerate)

