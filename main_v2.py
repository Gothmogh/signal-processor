import tables
import numpy as np
import multiprocessing
import sys
from utils.inputsignal import *


def udp_to_signal_chunk(_udp_packet):
    timestamp = BitArray(_udp_packet[0:4]).int
    readings = []

    for i in range(4, len(_udp_packet), 2):
        data = BitArray(_udp_packet[i:i + 2]).int
        readings.append(data)

    even_readings = readings[0:][::2]
    odd_readings = readings[1:][::2]

    return InputSignalChunk(timestamp, even_readings, odd_readings)


_server_socket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
_server_socket.bind(('', 3500))

MAXSIZE = 64000
TIMEOUT = 1.0
INT = 3.0  # interval in seconds

# create udp_socket
# last = time.time() - INT
# _server_socket.settimeout(TIMEOUT)
i = 0
arr = []
_packets = []

buffer_size = 10
_signal_chunks = []

print("Listening to port 3500")

while True:
    for i in range(buffer_size + 1):
        try:
            _packet = _server_socket.recv(MAXSIZE)
            # _packets.append(_packet)
            signal_chunk = udp_to_signal_chunk(bytearray(_packet))
            _signal_chunks.append(signal_chunk)
        except timeout:
            # handle recv timeout
            continue  # or break, or return
        except OSError:
            # handle recv error (Python 3.3+)
            break  # or continue, or return
        except Exception as err:
            print(err)
            traceback.print_tb(err.__traceback__)
            continue

    millis = int(round(time.time() * 1000))

    print("Saving " + str(i) + " packets with timestamp " + str(millis))

    with open('data/input/' + str(millis), 'wb') as data_file:
        # pickle.dump(_packets, data_file, pickle.HIGHEST_PROTOCOL)
        pickle.dump(_signal_chunks, data_file, pickle.HIGHEST_PROTOCOL)

    _packets = []
    _signal_chunks = []




