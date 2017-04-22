#NAUMAN SHAHZAD

from socket import *
import argparse
from sys import exit
import select
import _thread

#GLOBAL LISTS OF CLIENT SOCKETS AND ADDRESSES
#GLOBAL LIST OF CLIENT THREADS THAT ARE ACTIVE
clientSockets = list()
clientAddresses = list()
clientNames = list()
# clientThreads = list()

def parse_args():
    parser = argparse.ArgumentParser(description="Grab command line arguments for machine name/ip address and port_number")
    parser.add_argument('machine_name', help="Machine name/ip address on which to set up the socket to listen on.")
    parser.add_argument('port_number', type=int, help="Port number on which to listen on.")
    args = parser.parse_args()

    if args.machine_name == None:
        print("No machine name given, exiting.")
        exit()
    if args.port_number == None:
        print("No port number given, exiting.")
        exit()

    return args.machine_name, args.port_number

def handle_client(connectionSocket, addr):
    while True:
        select.select([connectionSocket], [], [])
        buffer = connectionSocket.recv(1024).decode()

        if buffer == "EXIT":
            print("Exiting this thread")
            exit()

        elif buffer == "":
            print("Client just disconnected, closing that connection socket now.")
            exit()



if __name__ == "__main__":
    machine_name, port_number = parse_args()
    serverPort = port_number
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((machine_name, serverPort))
    print("Listening on port " + str(port_number) + ", with machine name " + str(machine_name) + ".")
    serverSocket.listen()

    #INFINITE LOOP, SELECT ON EITHER STDIN OR LISTEN SOCKET
    while True:
        reading_list = select.select([serverSocket], [], [], None)

        print("Time to accept a connection")
        connectionSocket, addr = serverSocket.accept()
        clientSockets.append(connectionSocket)
        clientAddresses.append(addr)

        _thread.start_new(handle_client, (connectionSocket, addr))




