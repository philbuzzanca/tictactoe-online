from socket import *
import sys, getopt
def usage(erron):
	if(erron == 1):
		print("Invalid input")
	print('usage:\tclient.py -h <host> -p <port#>')
	print('      \tclient.py -H for help')
	sys.exit()
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
    userInput = input("$: ")
    
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((host, port))

    print(host+" "+port)

if __name__ == "__main__":
    main(sys.argv[1:])

