#Thierno Bah

from socket import *
import argparse
from sys import exit, stdin, stdout
import select
import _thread
from protocol import ClientMessage, ParseServerMessage

userId = None
userNumber = None
turnNumber = None
serverPort = None
ticTactToeBoard = None

def prompt():
    stdout.write('$: ')
    stdout.flush()

def displayMessage(message):
    stdout.write(message)
    stdout.flush()

def displayBoard(board):
    print("Board:")
    for i in range(len(board)):
        if i > 0 and i % 3 == 0:
            print()
        print(board[i], end=' ')
    print()
def isValidMove(move):
    intMov = None
    try:
        intMov = int(move)
        if(intMov < 1 or intMov > 9):
            return False
    except ValueError:
        return False
    return True
def readingFromStdin(buff):
    buff = stdin.readline()
    buff = buff.rstrip()
    print(buff)
    length = 0
    try:
        buff = buff.split(' ')
        length = len(buff)
    except:
        buff = (str(buff), 0)
        length = 1
    while (length > 2) :
        displayMessage('Input cannot exceed two arguments. Please try again')
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
                    displayMessage('login failed')
                else:
                    displayMessage(serverPacket.message+"> ")
                    input = stdin.readline()
                    input = input.rstrip()
                    message = ClientMessage(userId, serverPort, 'matchmake', input).toString()
                    sendToServer(socket, message)
            else:
                displayMessage("MISSING ARGUMENT")
                dohelp()
        else:
            displayMessage("You are already logged in. Enter a different command")
    elif (buff[0] == 'help'):
        dohelp()
    elif (buff[0] == 'exit'):
        message = ClientMessage(userId, serverPort, buff[0]).toString()
        sendToServer(socket, message)
        displayMessage('exiting ...')
        socket.close()
        exit()
    elif (buff[0] == 'place'):
        if (len(buff) > 1):
            if (isValidMove(buff[1])):
                message = ClientMessage(userId, serverPort, buff[0], buff[1]).toString()
                sendToServer(socket, message)
            else:
                print("INVALID MOVE")
        else:
            print("MISSING ARGUMENT")
            dohelp()
    elif (buff[0] == 'who'):
        message = ClientMessage(userId, serverPort, buff[0]).toString()
        sendToServer(socket, message)
    elif (buff[0] == 'play'):
        if(len(buff) > 1):
            message = ClientMessage(userId, serverPort, buff[0], buff[1]).toString()
            sendToServer(socket, message)

    elif (buff[0] == 'games'):
        message = ClientMessage(userId, serverPort, buff[0].toString())
        #games
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
    global userNumber, ticTactToeBoard
    while True:
        #SELECT AND WAIT ON CLIENT SOCKET
        select.select([clientSocket], [], [], None)
        serverPacket = ParseServerMessage(clientSocket.recv(1024).decode())

        #MEANING SERVER SENT AN OK MESSAGE
        if (serverPacket.status == 200):
            # print(serverPacket.message)

            if serverPacket.gameState == 1 or serverPacket.gameState == 2:
                if serverPacket.message == 'You are player 1':
                    userNumber = 1
                elif serverPacket.message == 'You are player 2':
                    userNumber = 2
                else:
                    place = int(serverPacket.message)
                    ticTactToeBoard[place-1] = serverPacket.gameState
                    displayBoard(ticTactToeBoard)
            elif serverPacket.gameState == 3:
                print(serverPacket.message)
                #RESET BOARD ON END OF GAME
                ticTactToeBoard = [0 for i in range(0,9)]
            else:
                displayMessage(serverPacket.message)
        #ELSE WAS 400 NOT OK MESSAGE
        else:
            if(serverPacket.message == 'Opponent disconnected'):
                print(serverPacket.message)
                displayMessage("I suppose you are the winner.")
                ticTactToeBoard = [0 for i in range(0, 9)]
#---------------------------------------------
# main ()
#
#---------------------------------------------

def main():
    global ticTactToeBoard
    #GRAB COMMAND LINE ARGUMENTS
    userInput = ''   # to grab user's input
    #userId = ''
    ticTactToeBoard = [0 for i in range(0,9)]
    displayBoard(ticTactToeBoard)
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
        userInput = readingFromStdin(userInput)
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



