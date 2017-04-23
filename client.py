from socket import *
import sys, getopt
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

def main(argv):
    port = ''
    host = ''
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
    userInput = input("$: ")
    userInput = userInput.split(' ')

    print(str(host)+" "+str(port))
    if(userInput[0] == 'help'):
        dohelp()

    clientSocket.close()

if __name__ == "__main__":
    main(sys.argv[1:])



