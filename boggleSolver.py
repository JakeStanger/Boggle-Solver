import sqlite3 as sql
from flask import Flask, render_template, request
import ast

app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html',name=name)

board = []
BOARD_SIZE = 0

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

#Load database
db = sql.connect('data/dictionary')
cursor = db.cursor()

#History
words = {}
adjacentCoords = {}
letterPositions = {}

def getValidWords(chars):
	'''Gets a list of words starting with the given character sequence
	where the required letters exist on the board.'''
	validWords = []
	cursor.execute("SELECT word FROM words WHERE word LIKE \'" + chars + "%\'")
	for row in cursor:
		#Words must have a valid number of letters depending on board size
		if len(row[0]) <= BOARD_SIZE*BOARD_SIZE:
			isValid = True
			for char in row[0]:
				if not char in letterPositions:
					isValid = False
			if(isValid): validWords.append(row[0])
	return validWords

def getCharPositions(char):
	'''Gets all the positions of a given character on the board'''
	#Check if any of the character actually exist on the board
	if not any(char in boardRow for boardRow in board):
		return None
	else:
		chars = []
		for x in range(BOARD_SIZE):
			for y in range(BOARD_SIZE):
				if board[x][y] == char: chars.append((x, y))
		return chars

def getLetterAt(coord):
	'''Gets the character at the given coordinate'''
	return board[coord[0]][coord[1]]

def areAdjacent(coord1, coord2):
	'''Checks if two coordinates are adjacent'''
	return coord2 in getAdjacentCoords(coord1[0], coord1[1])

def areCharsAdjacent(char1, char2):
	'''Checks if two characters are adjacent to each other
	in any location on the board'''
	char1PosList = getCharPositions(char1)
	char2PosList = getCharPositions(char2)

	#If the chars do not exist, then they're not adjacent
	if char1PosList == None or char2PosList == None:
		return False

	for pos1 in char1PosList:
		pos1Adj = getAdjacentCoords(pos1[0], pos1[1])
		for pos in pos1Adj:
			if pos in char2PosList: return True
	return False

def getAdjacentCoords(x, y):
	'''Gets a list of adjacent coordinates for the given set of coordinates'''
	if (x, y) in adjacentCoords:
		return adjacentCoords[(x, y)]

	coords = []
	#Check each surrounding coordinate lies on the board
	if x > 0:
		coords.append((x-1, y)) #Centre left
		if y > 0: coords.append((x-1, y-1)) #Top left
		if y < BOARD_SIZE-1: coords.append((x-1, y+1)) #Bottom right
	if x < BOARD_SIZE-1:
		coords.append((x+1, y)) #Centre right
		if y > 0: coords.append((x+1, y-1)) #Top right
		if y < BOARD_SIZE-1: coords.append((x+1, y+1)) #Top right
	if y > 0: coords.append((x, y-1)) #Centre top
	if y < BOARD_SIZE-1: coords.append((x, y+1)) #Centre bottom

	adjacentCoords[(x, y)] = coords
	return coords

def getWords(x, y, testWordBase, prevCoords):
	'''Gets a list of valid words for the given coordinate
	and pre-assembled set of characters.
	This function only recurs once and simply acts as a filter;
	in other words the test word will only ever be 2 characters long.'''
	coords = getAdjacentCoords(x, y)
	startChar = getLetterAt((x, y))
	if not (x, y) in prevCoords:
		for coord in coords:
			testWord = testWordBase + getLetterAt(coord) #TODO ---Fix bug on this line---
			if testWord in words:
				validWords = words[testWord]
			else:
				validWords = getValidWords(testWord)

			if len(validWords) > 0:
				words[testWord] = validWords
				words.pop(testWordBase, None) #Remove old entry

				if len(testWord) < 1:
					prevCoords.append((x, y))
					getWords(coord[0], coord[1], testWord, prevCoords)

@app.route('/boggleSolver.py', methods=['GET', 'POST'])
def boggleSolve():
	global board
	global BOARD_SIZE

	#print(request.get_data())
	data = ast.literal_eval(request.get_data().decode("utf-8"))['board']

	board = []
	rows = data.split("|")
	for row in rows:
		board.append(row.split("-"))

	BOARD_SIZE = len(board) #We can assume the board width = height
	results = []

	#Find position of each character on the board
	for letter in ALPHABET:
		charPositions = getCharPositions(letter)
		if not charPositions == None:
			letterPositions[letter] = getCharPositions(letter)

	#Check possible words for each starting position.
	#Filters possible words to ones with at least 2 characters
	#in the correct order.
	for x in range(BOARD_SIZE):
		for y in range(BOARD_SIZE):
			getWords(x, y, getLetterAt((x, y)), [])

	#Check remaining words to make sure each of their
	#characters are adjacent.
	for key in words:
		for word in words[key]:
			isValid = True
			for i in range(len(word)-1):
				if not areCharsAdjacent(word[i], word[i+1]):
					isValid = False
					break
			if isValid:
				results.append(word)

	db.commit()

	return ",".join(str(word) for word in results)

#--START OF PROGRAM--
if __name__ == "__main__":
	app.run()
	app.debug = True

	db.close()
