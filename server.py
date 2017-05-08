#NAUMAN SHAHZAD

from socket import *
import argparse
from sys import exit
import select
import _thread
from protocol import ParseClientMessage, ServerMessage
import threading

#LOCKS FOR SHARED LISTS
playerListLock = threading.Lock()
gameListLock = threading.Lock()

#CLASSES FOR GAMES AND PLAYERS
class Game(object):
    player1 = None
    player2 = None
    board = None
    turn = 1

    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2
        self.board = [0 for i in range(0,9)]

class Player(object):
    name = None
    connectionSocket = None
    isAvailable = False
    autoMatch = False
    playerNum = None
    game = None


    def __init__(self, name=None, connectionSocket=None):
        self.name = name
        self.connectionSocket = connectionSocket

#GLOBAL LISTS OF CLIENT SOCKETS AND ADDRESSES
#GLOBAL LIST OF CLIENT THREADS THAT ARE ACTIVE
serverPort = None
clientSockets = list()
clientAddresses = list()
playerList = list()
gameList = list()

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

def send(clientSocket, playerName, destinationPort, status, gameState, message):
    message = ServerMessage(playerName, destinationPort, status, gameState, message).toString()
    clientSocket.send(message.encode())

def clientExit(player, game):
    playerListLock.acquire(blocking=True, timeout=-1)
    playerList.remove(player)
    playerListLock.release()

    #CASE OF DISCONNECT MID GAME
    if player.game is not None:
        gameListLock.acquire(blocking=True, timeout=-1)
        gameList.remove(player.game)
        gameListLock.release()

        if player.game.player1 == player:
            p = player.game.player2
            p.isAvailable = True
            send(p.connectionSocket, p.name, serverPort, 400, 0, "Opponent disconnected")
            p.game = None
        else:
            p = player.game.player1
            p.isAvailable = True
            send(p.connectionSocket, p.name, serverPort, 400, 0, "Opponent disconnected")
            p.game = None


    exit()

def checkWinner(board):
    #CHECK ROWS FIRST
    if board[0] == 1 and board[1] == 1 and board[2] == 1:
        return 2
    elif board[0] == 2 and board[1] == 2 and board[2] == 2:
        return 1
    elif board[3] == 1 and board[4] == 1 and board[5] == 1:
        return 2
    elif board[3] == 2 and board[4] == 2 and board[5] == 2:
        return 1
    elif board[6] == 1 and board[7] == 1 and board[8] == 1:
        return 2
    elif board[6] == 2 and board[7] == 2 and board[8] == 2:
        return 1

    #CHECK COLUMNS NEXT
    elif board[0] == 1 and board[3] == 1 and board[6] == 1:
        return 2
    elif board[0] == 2 and board[3] == 2 and board[6] == 2:
        return 1
    elif board[1] == 1 and board[4] == 1 and board[7] == 1:
        return 2
    elif board[1] == 2 and board[4] == 2 and board[7] == 2:
        return 1
    elif board[2] == 1 and board[5] == 1 and board[8] == 1:
        return 2
    elif board[2] == 2 and board[5] == 2 and board[8] == 2:
        return 1

    #CHECK FOR DIAGNOLS NOW
    elif board[0] == 1 and board[4] == 1 and board[8] == 1:
        return 2
    elif board[0] == 2 and board[4] == 2 and board[8] == 2:
        return 1
    elif board[2] == 1 and board[4] == 1 and board[6] == 1:
        return 2
    elif board[2] == 2 and board[4] == 2 and board[6] == 2:
        return 1

    #CHECK IF BOARD IS FILLED, IN WHICH CASE IS A DRAW
    #3 IS A DRAW
    #0 IS GAME IS STILL ON
    for cell in board:
        if cell == 0:
            return 0
    return 3



def handle_client(connectionSocket, addr):
    player = Player(None, connectionSocket)
    playerListLock.acquire(blocking=True, timeout=-1)
    playerList.append(player)
    playerListLock.release()

    game = Game(None, None)

    while True:
        select.select([connectionSocket], [], [])

        try:
            buffer = connectionSocket.recv(1024).decode()
        except ConnectionResetError:
            print('Client just disconnected, closing that connection socket now')
            connectionSocket.close()
            clientExit(player, game)

        #INITIALLY CHECK FOR EMPTY PACKET
        if buffer == "":
            print("Client just disconnected, closing that connection socket now.")
            connectionSocket.close()
            clientExit(player, game)

        clientMessage = ParseClientMessage(buffer)

        #CLIENT EXITING CASES
        if clientMessage.command == "exit":
            print("Exiting this thread")
            clientExit(player, game)

        #HANDLE CLIENT LOGIN
        elif clientMessage.command == "login" and clientMessage.userid != None:
            print("New User: ", clientMessage.userid)
            player.name = clientMessage.userid
            player.isAvailable = True
            message = ServerMessage(player.name,serverPort,'200',0,'Auto-matchmake? (Y/N)').toString()
            connectionSocket.send(message.encode())

        #HANDLE PLAY PLAYER FROM CLIENT
        elif clientMessage.command == "play" and clientMessage.arg is not None:
            playerListLock.acquire(blocking=True, timeout=-1)
            flag = True
            for p in playerList:
                if p.name == clientMessage.arg and p.isAvailable and p.name is not player.name:
                    flag = False
                    p.isAvailable = False
                    player.isAvailable = False

                    p.playerNum = 1
                    player.playerNum = 2

                    game = Game(p, player)
                    gameListLock.acquire(blocking=True, timeout=-1)
                    gameList.append(game)
                    gameListLock.release()

                    p.game = game
                    player.game = game

                    send(p.connectionSocket, p.name, serverPort, 200, 1, 'You are player 1')
                    send(player.connectionSocket, player.name, serverPort, 200, 1, 'You are player 2')
                    break
            playerListLock.release()

            if flag:
                send(player.connectionSocket, player.name, serverPort, 400, 0, 'Player either does not exist or is not available. Or you weirdly wanted to play yourself...')

        #RESPOND TO QUERY REQUEST OF WHO'S ON AND WHO IS AVAILABLE
        elif clientMessage.command == "who":
            availablePlayers = list()
            playerListLock.acquire(blocking=True, timeout=-1)
            for p in playerList:
                if p.isAvailable:
                    availablePlayers.append(p)
            playerListLock.release()

            if len(availablePlayers) == 0:
                send(connectionSocket, player.name, serverPort, '200', 0, 'No online players')
            else:
                players = ""
                for p in availablePlayers:
                    players += str(p.name) + "\n"
                send(connectionSocket, player.name, serverPort, '200', 0, players)

        #RESPOND TO QUERY REQUEST OF ONGOING GAMES
        elif clientMessage.command == "games":
            gameListLock.acquire(blocking=True, timeout=-1)
            message = ""
            i = 0
            for game in gameList:
                message += 'Game ' + str(i) + ' - '
                message += game.player1.name + ', ' + game.player2.name + '\n'
                i += 1
            if message == "":
                message = "No Games currently.\n"
            gameListLock.release()

            send(player.connectionSocket, player.name, serverPort, 200, 0, message)

        #RESPONSD TO ANSWER OF AUTOMATCH Y/N
        elif clientMessage.command == "matchmake":
            if clientMessage.arg == None:
                send(connectionSocket, player.name, serverPort,'400', 0, 'matchmake')

            elif clientMessage.arg == 'y':
                player.autoMatch = True
                send(connectionSocket, player.name, serverPort, '200', 0, 'matchmake')

                playerListLock.acquire(blocking=True, timeout=-1)
                for opponent in playerList:
                    if opponent == player:
                        continue
                    elif opponent.autoMatch and opponent.isAvailable:
                        opponent.isAvailable = False
                        player.isAvailable = False
                        opponent.playerNum = 1
                        player.playerNum = 2

                        game = Game(opponent, player)

                        gameListLock.acquire(blocking=True, timeout=-1)
                        gameList.append(game)
                        gameListLock.release()

                        opponent.game = game
                        player.game = game

                        send(opponent.connectionSocket, opponent.name, serverPort, 200, 1, 'You are player 1')
                        send(player.connectionSocket, player.name, serverPort, 200, 1, 'You are player 2')
                playerListLock.release()


            elif clientMessage.arg == 'n':
                player.autoMatch = False
                send(connectionSocket, player.name, serverPort, '200', 0, None)

        #HANDLE PLACE SPOT CASE FROM CLIENT
        elif clientMessage.command == "place":
            num = int(clientMessage.arg)

            #FIRST CHECK IF THERE IS A GAME WITH THIS PLAYER
            if player.game == None:
                send(connectionSocket, player.name, serverPort, '400', 0, 'not a legal move')
                continue

            #CHECK IF LEGAL MOVE
            #CHECK IF IT IS THIS PLAYER'S TURN
            if player.game.board[num-1] == 0 and player.playerNum == player.game.turn:
                player.game.board[num-1] = game.turn

                winState = checkWinner(player.game.board)

                #IF ANY OF THESE ARE TRUE THEN THE GAME IS OVER
                if winState == 1 or winState == 2 or winState == 3:
                    player.game.player1.isAvailable = True
                    player.game.player2.isAvailable = True
                    #DRAW
                    if winState == 3:
                        send(player.game.player1.connectionSocket, player.game.player1.name, serverPort, 200,
                             3,
                             'draw')
                        send(player.game.player2.connectionSocket, player.game.player2.name, serverPort, 200,
                             3,
                             'draw')
                    # PLAYER 2 WON
                    elif winState == 2:
                        send(player.game.player1.connectionSocket, player.game.player1.name, serverPort, 200,
                             3,
                             'player 2 won')
                        send(player.game.player2.connectionSocket, player.game.player2.name, serverPort, 200,
                             3,
                             'player 2 won')
                    # PLAYER 1 WON
                    else:
                        send(player.game.player1.connectionSocket, player.game.player1.name, serverPort, 200,
                             3,
                             'player 1 won')
                        send(player.game.player2.connectionSocket, player.game.player2.name, serverPort, 200,
                             3,
                             'player 1 won')
                    p1 = player.game.player1
                    p2 = player.game.player2

                    gameListLock.acquire(blocking=True, timeout=-1)
                    gameList.remove(p1.game)
                    gameListLock.release()

                    p1.game = None
                    p2.game = None

                    continue


                # OTHERWISE THE GAME IS STILL GOING
                lastPlayerTurn = player.game.turn
                if player.game.turn == 1:
                    player.game.turn = 2
                else:
                    player.game.turn = 1

                send(player.game.player1.connectionSocket, player.game.player1.name, serverPort, 200, lastPlayerTurn,
                     str(num))
                send(player.game.player2.connectionSocket, player.game.player2.name, serverPort, 200, lastPlayerTurn,
                 str(num))

            #ILLEGAL MOVE OR COMMAND
            else:
                send(connectionSocket, player.name, serverPort, '400', player.game.turn, 'not a legal move')



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

        _thread.start_new(handle_client, (connectionSocket, addr))




