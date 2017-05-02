from socket import *
import argparse
from sys import exit, stdin, stdout
import select
import _thread

def dohelp():
    print ("\nWelcome to tictactoe commands")
    print("\nhelp: for help\n")
    print('''login: this command takes one argument, your name. A player name is a userid that
uniquely identifies a player\n
place: this command issues a move. It takes one argument n, which is between 1 and 9 inclusive.
It identify a cell that the player chooses to occupy at this move.\n
exit: the player exits the game. It takes no argument. A player can issue this command at any
time
    ''')

def sendToServer(clientSocket, sentence):
    clientSocket.send(sentence.encode())

def parse_args():
    parser = argparse.ArgumentParser(
        description="Grab command line arguments for machine name/ip address and port_number")
    parser.add_argument('-m', help="Machine name/ip address on which the server is.")
    parser.add_argument('-p', type=int, help="Port number for the server.")
    args = parser.parse_args()

    if args.m == None:
        print("No machine name given, exiting.")
        exit()
    if args.p == None:
        print("No port number given, exiting.")
        exit()

    return args.m, args.p

def login_procedure(clientSocket):
    clientSocket.send('WOLFIE'.encode())

    select.select([clientSocket], [], [], None)
    serverPacket = clientSocket.recv(1024).decode()

    if serverPacket != 'EIFLOW':
        print('Error in login procedure with server, shutting down client program now.')
        exit()

#IGNORE FLUFF, JUST THERE TO GET _thread.start_new TO WORK
def serverHandler(clientSocket, fluff):
    while True:
        #SELECT AND WAIT ON CLIENT SOCKET
        select.select([clientSocket], [], [], None)

        serverPacket = clientSocket.recv(1024).decode()

        print(serverPacket)

def main():
    #GRAB COMMAND LINE ARGUMENTS
    serverName, serverPort = parse_args()

    #TRY CATCH BLOCK IN CASE ERROR IN ESTABLISHING SOCKET
    try:
        #SET UP SOCKET AND CONNECTION WITH SERVER
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
    except:
        print("Error establishing socket with server, exiting client program.")
        exit()

    #LOGIN PROCEDURE WITH SERVER FIRST BEFORE PROCEEDING
    login_procedure(clientSocket)

    #INITIALIZE A THREAD TO LISTEN ON INPUT FROM SERVER
    server_thread = _thread.start_new(serverHandler, (clientSocket, ' '))

    #THIS THREAD WILL JUST LISTEN ON STDIN
    while True:
        stdout.write('$:')
        stdout.flush()
        line = stdin.readline()

        #REMOVE THE NEWLINE CHARACTER
        line = line[0:-1]

        if line == 'exit':
            sendToServer(clientSocket, 'EXIT')
            clientSocket.close()
            exit()

        elif line == 'help':
            dohelp()



if __name__ == "__main__":
    main()



