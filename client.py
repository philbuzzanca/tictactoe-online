from socket import *
import argparse
from sys import exit, stdin, stdout
import select
import _thread
from protocol import ClientMessage, ParseServerMessage

userId = None
serverPort = None

def prompt():
    stdout.write('$: ')
    stdout.flush()

def readingFromStdin(buff):
    buff = stdin.readline()
    buff = buff.rstrip()
    length = 0
    try:
        buff = buff.split(' ')
        length = len(buff)
    except:
        buff = (str(buff), 0)
        length = 1
    while (length > 2) :
        stdout.write('Input cannot exceed two arguments. Please try again')
        buff = stdin.readline()
        buff = buff.rstrip()
        try:
            buff = buff.split(' ')
            length = len(buff)
        except:
            buff = (str(buff), 0)
            length = 1

    return buff

def sendDataToServer(socket, buff, log=True):
    global userId
    global serverPort
    #message = None
    print(buff)
    if(buff[0] == 'login'):
        if (log != True):
            if(len(buff) > 1):
                userId = buff[1]
                message = ClientMessage(userId, serverPort, buff[0]).toString()
                sendToServer(socket, message)
                select.select([socket], [], [], None)
                serverPacket = ParseServerMessage(socket.recv(1024).decode())
                if(serverPacket.status == 400):
                    stdout.write('login failed')
                else:
                    stdout.write(serverPacket.message+"> ")
                    stdout.flush()
                    input = stdin.readline()
                    input = input.rstrip()
                    message = ClientMessage(userId, serverPort, input).toString()
                    sendToServer(socket, message)
            else:
                print("MISSING ARGUMENT")
                dohelp()
        else:
            print("You are already logged in. Enter a different command")
    elif (buff[0] == 'help'):
        dohelp()
    elif (buff[0] == 'exit'):
        message = ClientMessage(userId, serverPort, buff[0]).toString()
        sendToServer(socket, message)
        print('exiting ...')
        socket.close()
        exit()
    elif (buff[0] == 'place'):
        if (len(buff) > 1):
            message = ClientMessage(userId, serverPort, buff[0], buff[1]).toString()
            sendToServer(message)
        else:
            print("MISSING ARGUMENT")
            dohelp()
    else:
        print("INVALID COMMAND")
        dohelp()
def dohelp():
    print ("\nWelcome to tictactoe commands")
    print("\nhelp:\tfor help\n")
    print('''login:\tthis command takes one argument, your name. A player name is a userid that
uniquely identifies a player\n
place:\tthis command issues a move. It takes one argument n, which is between 1 and 9 inclusive.
It identify a cell that the player chooses to occupy at this move.\n
exit:\tthe player exits the game. It takes no argument. A player can issue this command at any
time\n
games:\tthis command triggers a query sent to the server. A list of current ongoing games is returned. For each game, the
game ID and game players are listed.\n
who:\tthis command has no argument.It triggers a query message that is sent to the server; a list of players who are
currently logged - in and available to play is retrieved and displayed.\n
play:\tthis command take one argument, the name of a player X you'd like to play a game with. A message is sent
to the server indicating that you'd like to play with X. After receiving this message, if X is available,
the server starts a new game between you and X. If X is not available, the server replies you that X is no longer
available. You may then choose another player instead.
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

#IGNORE FLUFF, JUST THERE TO GET _thread.start_new TO WORK
def serverHandler(clientSocket, fluff):
    while True:
        #SELECT AND WAIT ON CLIENT SOCKET
        select.select([clientSocket], [], [], None)

        serverPacket = clientSocket.recv(1024).decode()

        serverMessage = ParseServerMessage(serverPacket)

        print(serverPacket)
#---------------------------------------------
# main ()
#
#---------------------------------------------

def main():
    #GRAB COMMAND LINE ARGUMENTS
    userInput = ''   # to grab user's input
    #userId = ''
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
    prompt()
    userInput = readingFromStdin(userInput)
    sendDataToServer(clientSocket, userInput, False)   #False means user is not logged in yet.
    #login_procedure(clientSocket)

    #INITIALIZE A THREAD TO LISTEN ON INPUT FROM SERVER
    server_thread = _thread.start_new(serverHandler, (clientSocket, ' '))

    #THIS THREAD WILL JUST LISTEN ON STDIN
    while True:
        prompt()
        readingFromStdin(userInput)
        sendDataToServer(clientSocket, userInput)

        #REMOVE THE NEWLINE CHARACTER
        #line = line[0:-1]

        if userInput[0] == 'exit':
            message = ClientMessage(userId, serverPort, userInput[0])
            sendToServer(message)
            clientSocket.close()
            exit()

        elif userInput[0] == 'help':
            dohelp()
if __name__ == "__main__":
    main()



