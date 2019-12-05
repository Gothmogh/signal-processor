from socket import *
import struct

import pandas as pd
from bitstring import BitArray

import numpy as np


def csv_to_udp_packet_array(file="../data/sampleSignal.csv", sep=";", header=0, time_col='time', framerate=2000):

    frames_per_packet = 123

    full_input_df = pd.read_csv(file, header=header, sep=sep)

    tension = full_input_df.loc[:, ['tension']].transpose().values.flatten()
    current = full_input_df.loc[:, ['current']].transpose().values.flatten()
    time = full_input_df.loc[:, [time_col]].transpose().values.flatten()

    # tension_int = np.trunc((tension + 1.65) * 4096 / 3.3)
    # current_int = np.trunc((current + 1.65) * 4096 / 3.3)
    tension_int = np.trunc((tension * (220.0 / 9.0) * (3.3 / 4096.0)) + 1.65)
    current_int = np.trunc((current * (220.0 / 9.0) * (3.3 / 4096.0)) + 1.65)
    time_int = time * (10 ** 6)

    total_data = len(time) - (len(time) % frames_per_packet)

    packets = []

    for i in range(0, total_data, frames_per_packet):
        _packet = create_udp_packet(time_int[i], tension_int[i:i+frames_per_packet], current_int[i:i+frames_per_packet])
        packets.append(_packet)

    return packets


def create_udp_packet(timestamp, tension_data, current_data):
    packet_data = np.empty((tension_data.size + current_data.size,), dtype=tension_data.dtype)
    packet_data[0::2] = tension_data
    packet_data[1::2] = current_data
    # bits = np.unpackbits(np.arange(2, dtype=np.uint16).view(np.uint8))
    timestamp_bit = "{:032b}".format(int(np.trunc(timestamp)))
    # timestamp_bit = format(timestamp, '#032b')
    _packet = struct.pack(timestamp_bit, packet_data)
    return _packet


packets = csv_to_udp_packet_array()
for packet in packets:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(packet, ('localhost', 3500))
