#NAUMAN SHAHZAD

from socket import *
import argparse
from sys import exit

#GLOBAL LISTS OF CLIENT SOCKETS AND ADDRESSES
clientSockets = list()
clientAddresses = list()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Grab command line arguments for machine name/ip address and port_number")
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


if __name__ == "__main__":
    machine_name, port_number = parse_args()
    serverPort = port_number
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((machine_name, serverPort))
    print("Listening on port " + str(port_number) + ", with machine name " + str(machine_name) + ".")
    serverSocket.listen()

    #INFINITE LOOP, SELECT ON EITHER STDIN OR LISTEN SOCKET
    # while True:

