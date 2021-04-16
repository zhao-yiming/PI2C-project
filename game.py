import socket
import sys
import os
from client import sendJSON, receiveJSON, NotAJSONObject, fetch
from threading import Timer
import random

def send(information):
    return sendJSON(s,information)

def inscription(port):
    request={"request":"subscribe",
                "port":port,
                "name":str(port),
                "matricules":["195187","195000"]}
    return send(request)

def getColor(current):
    symbols = ['B', 'W']
    return symbols[current]

def checkMarble(board,pos):
    li,ci=pos[0],pos[1]
    direct=[[-1,0],[1,0],[-1,-1],[1,1],[0,1],[0,-1]]
    voisins=[]
    for elem in direct:
        try:
            voisins.append(board[li+elem[0]][ci+elem[1]])
        except:pass
    if 'E' in voisins:
        return True
    else:
        return False

def randomMarble(color,board,posMarbles):
    value=random.randrange(len(posMarbles))
    pos=posMarbles[value]
    if checkMarble(board,pos)==True:
        return pos
    else:
        return randomMarble(color,board,posMarbles[:value]+posMarbles[value+1:])

def choixMarble(color,board):
    posMarbles=[]
    i=0
    while i<9:
        for state in range(len(board[i])):
            if board[i][state]==color:
                posMarbles.append([i,state])
        i+=1
    return randomMarble(color,board,posMarbles)

def checkDirection(marble,board,direction):
    directions = {
	'NE': [-1,0],
	'SW': [1,0],
	'NW': [-1,-1],
	'SE': [1,1],
	 'E': [0,1],
	 'W': [0,-1]
    }
    li,ci=marble[0],marble[1]
    try:
        lf,cf=li+directions[direction][0],ci+directions[direction][1]
        if board[lf][cf]=='E':
            return True
        else:
            return False
    except:return False

def choixDirection(marble,board,listeDirections=['NE','SW','NW','SE','E','W']):
    val=random.randrange(len(listeDirections))
    direction=listeDirections[val]
    if checkDirection(marble,board,direction)==True:
        return direction
    else:
        return choixDirection(marble,board,listeDirections[:val]+listeDirections[val+1:])


def listenServer():
    sock=socket.socket()
    sock.bind(('0.0.0.0',port))
    #try:
    sock.listen()
    server, address = sock.accept()
    data=receiveJSON(server)
    if data['request']=='ping':
        return sendJSON(server,{'response':'pong'})
    if data['request']=='play':
        color= getColor(data['state']['current'])
        marble=choixMarble(color,data['state']['board'])
        marbles=(marble,)
        direction=choixDirection(marble,data['state']['board'])
        return sendJSON(server,{'response':'move','move':{'marbles':marbles,'direction':direction},'message':"random player"})
    else:
        print(data)
    #except:
        #pass



if __name__ == '__main__':
    port=int(sys.argv[1])
    s=socket.socket()
    s.connect((socket.gethostname(),3000))
    inscription(port)
    while 1:
        listenServer()
#& python c:/sketch_oct01a/PI2C-project/game.py 8888