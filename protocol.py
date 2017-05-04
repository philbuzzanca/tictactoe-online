# Protocol:
# All messages sent from the client should be in the form a ClientMessage
# Use the toString() method to send a message as a colon separated string
# On the server-side, use ParseClientMessage(message)
# This returns the string to a ClientMessage object
# userID and destinationport fields are required. Command may be "help" or "join" or etc.
# arg is the single arg associated with the command (if necessary)
# It is up to the client to determine when and how to create the client messages
# Similarly, messages from the server are sent as a ServerMessage
# UserID and destination port are required with each server message
# Status should be an int. Use 200 for OK and 400 for error (implement server- and client-side)
# Client should check that the server did not send a 400 before allowing another command
# gameState is also an int: (0 = no active game, 1 = player 1 turn, 2 = player 2 turn, 3 = game over)
# message is an optional field to send info such as "user x is player 1" or "Invalid value for n"
# take care not to put any ":" in the message, this may break the parser

# gameplay should operate as follows:
# client a: login
# server->a: OK (gamestate 0)
# client b: login
# server->b: OK (gamestate 0)
# Server will matchmake player a and b
# Server->a,b: player 1 turn (gamestate 1)
# Client a: place n
# Server->a,b: OK, player 2 turn (gamestate 2) OR Error, player 1 turn (gamestate 1) (e.g. client sends "place 0")
# Client b: place n
# Server->a,b: OK, player 1 turn (gamestate 1) OR Error, player 2 turn (gamestate 2) (e.g. client attempts to place in a taken position)
# Repeat until server detects a win or tie
# Server->a,b: OK, game over (gamestate 3). Message = "Player x wins/draw/player left game"

class ClientMessage:
	def __init__(self, userid, destinationPort, command, arg=None):
		self.userid = userid
		self.destinationPort = destinationPort
		self.command = command
		self.arg = arg

	def toString(self):
		ret = self.userid+":"+str(self.destinationPort)
		if self.command is not None:
			ret = ret + ":" + self.command
		if self.arg is not None:
			ret = ret + ":" + self.arg
		return ret

class ServerMessage:
	def __init__(self, userid, destinationPort, status, gameState, message=None):
		self.userid = userid
		self.destinationPort = destinationPort
		self.status = status
		self.gameState = gameState
		self.message = message

	def toString(self):
		ret = self.userid+":"+str(self.destinationPort)
		if self.status is not None:
			ret = ret + ":" + str(self.status)
		if self.gameState is not None:
			ret = ret + ":" + str(self.arg)
		return ret

def ParseClientMessage(message):
	split = message.split(":", message.count(':'))
	ret = ClientMessage(split[0], split[1])
	if split[2] is not None:
		ret.command = split[2]
	if split[3] is not None:
		ret.arg = split[3]
	return ret

def ParseServerMessage(message):
	split = message.split(":", message.count(':'))
	ret = ServerMessage(split[0], split[1], int(split[2]), int(split[3]))
	if split[4] is not None:
		ret.message = split[4]
	return ret