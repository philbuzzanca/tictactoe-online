from socket import *
import sys, getopt
import threading
import time
def usage(erron):
	if(erron == 1):
		print("Invalid input")
	print('usage:\tclient.py -h <host> -p <port#>')
	print('      \tclient.py -H for help')
	sys.exit()

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
#To read user input from the stdin


def stdin(buff):
    buff = input("$:")
    usrInput = buff.split(' ')
    while (len(usrInput) > 2) :
        print('Input cannot exceed two arguments. Please try again')
        buff = input("$:")
        usrInput = buff.split(' ')

def server( sockect, buff):
    buff = socket.recv(1024).decode()

def sendDataToServer(socket, buff, log):
    if(buff[0] == 'login'):
        if (log != True):
            socket.send(buff.encode())
        else:
            print("You are already logged in. Enter a different command")
            stdin(buff)
    elif (buff[0] == 'help'):
        dohelp()
    elif (buff[0] == 'exit'):
        print('exiting ...')
        sys.exit()
    elif (buff[0] == 'place'):
        socket.send(buff.encode())



def main(argv):
    port = ''
    host = ''
    userInput = ''
    buffer = ''
    logStatus = False
    try:
        opts, args = getopt.getopt(argv, "Hh:p:", ["help=", "port=", "host="])
        if (len(opts) < 1):
            usage(1)
    except getopt.GetoptError:
        usage(1)
    for opt, arg in opts:
        if opt == '-H':
            usage(0)
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
    try:
        port = int(port)
    except ValueError:
        usage(1)

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))
    stdin(userInput)
    userInput = userInput.split(' ')
    sendDataToServer(clientSocket, userInput, logStatus)
    logStatus = True
    while (True):
        stdinThread = threading.Thread(target=stdin, args=userInput)
        serverThread = threading.Thread(target=server, args=(clientSocket, buffer))
        stdinThread.start()
        serverThread.start()
        #sendDataToServer(clientSocket, userInput, logStatus)
    clientSocket.close()
if __name__ == "__main__":
    main(sys.argv[1:])



