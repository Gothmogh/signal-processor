from utils.inputsignal import *
from utils.signalprocessor import *
# from utils.artist import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

c = threading.Condition()
flag = 0      #shared between Thread_A and Thread_B
val = 20
amplitude_scale_factor = 0.01
# amplitude_scale_factor = 1.0 / 10000.0


print("Starting UDP reading...")

input_signal_stream = InputSignalStream()

server = InputSignalServer(input_signal_stream)
processor = SignalStreamProcessor(_input_signal_stream=input_signal_stream)
# plotter = SignalShapePlotter(input_signal_stream)
server.start()
processor.start()
# plotter.start()
# server.join()
# processor.join()
# plotter.join()


# csv_file = '../data/sampleSignal3.csv'
#
# full_input_df = pd.read_csv(csv_file, sep=";")

# tension_df = full_input_df.loc[:, ['time', 'tension']]
# current_df = full_input_df.loc[:, ['time', 'current']]

# time.sleep(5)
#
# wave_pair_wrapper = input_signal_stream.get_full_wave_pair_wrapper()
#
# tension_wave_wrapper = wave_pair_wrapper.get_wave_a_wrapper()
# tension_wave = tension_wave_wrapper.get_wave()
# tension_np = np.column_stack((tension_wave.ts, tension_wave.ys))
# tension_df = pd.DataFrame({'time': tension_np[:, 0], 'tension': tension_np[:, 1]})
#
# print(tension_df)
#
#
# def data_gen(t=0):
#     for chunk in np.array_split(tension_df, len(tension_df) // 40):
#         yield chunk.loc[:, ['time']], chunk.loc[:, ['tension']]
#     # for chunk in np.array_split(current_df, len(current_df) // 40):
#     #     yield chunk.loc[:, ['time']], chunk.loc[:, ['current']]
#
#
# def init():
#     ax.set_ylim(-500, 500)
#     del x_data[:]
#     del y_data[:]
#     # line.set_data(x_data, y_data)
#     return line
#
#
# fig, ax = plt.subplots()
# line = ax.plot([], [], lw=2)
# ax.grid()
# x_data, y_data = [], []
#
#
# def run(data):
#     # update the data
#     t, y = data
#     xdata = t
#     ydata = y
#     # print(ydata[1:-1])
#     # print("==========")
#     # print(ydata.iloc[[0], [0]].values)
#     # print("==========")
#     # print(ydata.iloc[[-1], [0]].values)
#     # print("==========")
#     # ax.set_ylim(np.amin(ydata), np.amax(ydata))
#     ax.set_xlim(xdata.iloc[[0], [0]].values, xdata.iloc[[-1], [0]].values)
#     line.set_data(xdata, ydata)
#
#     return line
#
#
# # plt.ion()
#
#
# ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=20, repeat=False, init_func=init)
# #
# plt.show()
