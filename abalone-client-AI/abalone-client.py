import socket
import sys
import os
from interface import sendJSON, receiveJSON, NotAJSONObject, fetch
from threading import Timer
import random
import copy
import time
from collections import defaultdict

def send(information):#envoie des informations au serveur
    return sendJSON(s,information)

def inscription(port):#s'inscrit au près du serveur
    request={"request":"subscribe",
                "port":port,
                "name":str(port),
                "matricules":["195187","195120"]}
    return send(request)

def getColor(current):#renvoie la couleur des marbles du joueur
    symbols = ['B', 'W']
    return symbols[current]

def getEnnemy(current):#renvoie la couleur des marbles de son adverssaire
    symbols = ['W', 'B']
    return symbols[current]

def opposite(current):#indique le current opposé
	if current==1:
		return 0
	return 1

def computeMarbles(board,color):#compte le nombre des marbles sur le plateau (pour une couleur spécifique)
	marbles=0
	i=0
	while i<9:
		for state in range(9):
			if boardMarble(board, color, [i,state]):
				marbles+=1
		i+=1
	return marbles

def winner(board,current):#vérifie s'il n'y pas de gagnant
	color=getColor(current)
	ennemy=getEnnemy(current)
	if computeMarbles(board,color)<=8:
		return ennemy
	if computeMarbles(board,ennemy)<=8:
		return color
	return None

def OnBoard(pos):#vérifie si une position est sur le plateau du jeu
	l,c=pos[0],pos[1]
	if min(l,c)<0:
		return False
	if max(l,c)>8:
		return False
	if abs(c-l)>=5:
		return False
	return True

def boardMarble(board,color,pos):#vérifie si la position est sur le plateau et correspond à la couleur
	l,c=pos[0],pos[1]
	if OnBoard(pos)==True:
		try:
			return board[l][c]==color
		except: return False
	return False

def moves(board,color,ennemy):#donne toutes les movements possibles pour une couleur spécifier
	moveOne=[]
	posMarbles=[]
	moveTrain=[]
	i=0
	while i<9:
		for state in range(9):
			if boardMarble(board, color, [i,state]):
				posMarbles.append((i,state))
		i+=1
	for direction in directions:
		for marble in posMarbles:
			li,ci=marble[0],marble[1]
			l,c=directions[direction][0],directions[direction][1]
			if boardMarble(board,'E',[li+l,ci+c]): #anvance 1 pion dans le vide
				moveOne.append([(li,ci),direction])
			if boardMarble(board,ennemy,[li+l,ci+c]):
				if isFree(board,[li+2*l,ci+2*c]):#pousse 2 contre 1
					if boardMarble(board,color,[li-l,ci-c]):
						moveTrain.append([(li,ci),(li-l,ci-c),direction])
						if boardMarble(board,color,[li-2*l,ci-2*c]):#pousse 3 contre 1
							moveTrain.append([(li,ci),(li-l,ci-c),(li-2*l,ci-2*c),direction])
				if boardMarble(board,ennemy,[li+2*l,ci+2*c]): #pousse 3 contre 2
					if isFree(board,[li+3*l,ci+3*c]):
						if boardMarble(board,color,[li-l,ci-c]) and boardMarble(board,color,[li-2*l,ci-2*c]):
							moveTrain.append([(li,ci),(li-l,ci-c),(li-2*l,ci-2*c),direction])

	for move in moveOne:#avance de plusieurs marbles dans le vide
		lm,cm,direction = move[0][0],move[0][1],move[1]
		lf,cf=lm-directions[direction][0],cm-directions[direction][1]
		ld,cd=lf-directions[direction][0],cf-directions[direction][1]
		if boardMarble(board, color, [lf,cf]):
			moveTrain.append([(lm,cm),(lf,cf),direction])
			if boardMarble(board, color, [ld,cd]):
				moveTrain.append([(lm,cm),(lf,cf),(ld,cd),direction])
	moveAll=moveTrain+moveOne
	L=random.sample(moveAll,len(moveAll))
	L.sort(key=len,reverse=True)
	return L

def moveOneMarble(board,move,color):#modification porté par une marble
	li,ci = move[0][0],move[0][1]
	direction=move[1]
	ld,cd=li+directions[direction][0],ci+directions[direction][1]
	try:
		destStatus=board[ld][cd]
	except:
		destStatus='X'
	board=copy.copy(board)
	board[li]=copy.copy(board[li])
	board[li][ci]='E'
	if destStatus=='E':
		board[ld]=copy.copy(board[ld])
		board[ld][cd]=color
	return board

def isFree(board,pos):#est ce qu'il y a une marble dans cette case
	l,c =pos[0],pos[1]
	if OnBoard(pos):
		return board[l][c]=='E'
	else:
		return True

def MoveMarbles(board,marbles,direction,color):
	for pos in marbles:
		board=moveOneMarble(board,[(pos),direction],color)
	return board

def moveMarbleTrain(board,move,color,ennemy):#modification porté par plusieurs marbles
	direction=move[-1]
	marbles= move[0:-1]
	if direction in ['E','SE','SW']:
		marbles=sorted(marbles,key=lambda L:-(L[0]*9+L[1]))
	else:
		marbles=sorted(marbles,key=lambda L:L[0]*9+L[1])
	lf,cf=marbles[0][0]+directions[direction][0],marbles[0][1]+directions[direction][1]
	push=[]
	while not isFree(board,[lf,cf]):
		push.append([lf,cf])
		lf,cf=lf+directions[direction][0],cf+directions[direction][1]
	board=MoveMarbles(board,list(reversed(push))+marbles,direction,color)
	return board

def apply(board,move,color,ennemy):#applique la modification
	state=[]
	for line in board:
		state.append(list(line))
	if len(move)==2:
		return moveOneMarble(state,move,color)
	return moveMarbleTrain(state,move,color,ennemy)

def timeit(fun):#initialise le temp actuel
	def wrapper(*args,**kwargs):
		start=time.time()
		res=fun(*args,**kwargs)
		return res
	return wrapper

@timeit
def next(board,player,fun):
	_,move=fun(board,player)
	return move

def gameOver(board,current):#vérifier s'il y a un gagnant
	if winner(board,current) is not None:
		return True
	return False

def lineValue(state, player):#donne la différence des marbles entre le joueur et son adversaire
	color=getColor(player)
	ennemy=getEnnemy(player)
	mesMarbles=computeMarbles(state,color)
	ennemyMarbles=computeMarbles(state,ennemy)
	if mesMarbles>ennemyMarbles:
		return mesMarbles-ennemyMarbles
	if mesMarbles==ennemyMarbles:
		return 0
	return mesMarbles-ennemyMarbles


def heuristic(state, player):#heuristic de la partie
	color=getColor(player)
	if gameOver(state,player):
		theWinner = winner(state,player)
		if theWinner is None:
			return 0
		if theWinner == color:
			return 9
		return -9
	res = lineValue(state, player)
	return res
	
def negamaxWithPruningIterativeDeepening(state, player):
	cache = defaultdict(lambda : 0)
	def cachedNegamaxWithPruningLimitedDepth(state, player, depth, alpha=float('-inf'), beta=float('inf')):
		color=getColor(player)
		ennemy=getEnnemy(player)
		over = gameOver(state,player)
		if over ==True or depth == 0:
			res = -heuristic(state, player), None, over
		else:
			theValue, theMove, theOver = float('-inf'), None, True
			possibilities = [[move, apply(state, move,color,ennemy)] for move in moves(state,color,ennemy)]
			for i in range(len(possibilities)):
				A=[]
				for elem in possibilities[i][1]:
					A.append(tuple(elem))
				possibilities[i][1]=A
			possibilities.sort(key=lambda poss: cache[tuple(poss[1])])
			for move, successor in possibilities:
				value, _, over = cachedNegamaxWithPruningLimitedDepth(successor, opposite(player), depth-1, -beta, -alpha)
				theOver = theOver and over
				if value > theValue:
					theValue, theMove = value, move
				alpha = max(alpha, theValue)
				if alpha >= beta:
					break
			res = -theValue, theMove, theOver
		cache[tuple(state[0])] = res[0]
		return res

	value, move = 0, None
	depth = 1
	over = False
	while value > -9 and depth<3 and not over :
		value, move, over = cachedNegamaxWithPruningLimitedDepth(state, player, depth)
		depth += 1
	return value, move

def run(fun,board,current):#tourne la fuction 'run' 
	color=getColor(current)
	ennemy=getEnnemy(current)
	move=next(board,current,fun)
	return move

def listenServer():#reçois les instructions du serveur
	sock=socket.socket()
	sock.bind(('0.0.0.0',port))
	sock.listen()
	server, address = sock.accept()
	data=receiveJSON(server)
	if data['request']=='ping':
		return sendJSON(server,{'response':'pong'})
	if data['request']=='play':
		move=run(negamaxWithPruningIterativeDeepening,data['state']['board'],data['state']['current'])
		if move is not None:
			return sendJSON(server,{'response':'move','move':{'marbles':move[0:-1],'direction':move[-1]},'message':'Hello World'})
	else:
		print(data)



if __name__ == '__main__':
    directions = {
	'NE': [-1,0],
	'SW': [1,0],
	'NW': [-1,-1],
	'SE': [1,1],
	'E': [0,1],
	'W': [0,-1]
    }
    port=int(sys.argv[1])
    s=socket.socket()
    s.connect((socket.gethostname(),3000))
    inscription(port)
    while 1:
        listenServer()