# We will need the following module to generate randomized lost packets
import random
from socket import *

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 3000))

while True:
    # print ('waiting for a connection')
    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)

    # show who connected to us
    # print ('connection from', address)
    # print ("Message: %s" % message)
    print (message)
    # Capitalize the message from the client
    # # If rand is less is than 4, we consider the packet lost and do notrespond
    # if rand < 4:
    #     continue

    # Otherwise, the server responds
    # serverSocket.sendto(message, address)
