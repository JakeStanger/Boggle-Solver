import sqlite3 as sql

#Constants
#Hard-coded board
board = (('x', 'a', 'c', 't'),
		 ('x', 'd', 'y', 'l'),
		 ('x', 'o', 'p', 'x'),
		 ('r', 'e', 't', 'x'))

BOARD_SIZE = len(board) #We can assume the board width = height

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

def getAdjacentCoords(x, y):
	'''Gets a list of adjacent coordinates for the given set of coordinates'''
	if (x, y) in adjacentCoords:
		return adjacentCoords[(x, y)]

	coords = []
	#Check each surrounding coordinate lies on the board
	if x > 0:
		coords.append((x-1, y))
		if y > 0: coords.append((x-1, y-1))
		if y < BOARD_SIZE-1: coords.append((x-1, y+1))
	if x < BOARD_SIZE-1:
		coords.append((x+1, y))
		if y > 0: coords.append((x+1, y-1))
		if y < BOARD_SIZE-1: coords.append((x+1, y+1))
	if y > 0: coords.append((x, y-1))
	if y < BOARD_SIZE-1: coords.append((x, y+1))

	adjacentCoords[(x, y)] = coords
	return coords

def getWords(x, y, testWordBase, prevCoords):
	'''Gets a list of valid words for the given coordinate
	and pre-assembled set of characters'''
	coords = getAdjacentCoords(x, y)
	startChar = getLetterAt((x, y))
	if not (x, y) in prevCoords:
		for coord in coords:
			testWord = testWordBase + getLetterAt(coord)
			if testWord in words:
				validWords = words[testWord]
			else:
				validWords = getValidWords(testWord)

			if len(validWords) > 0:
				words[testWord] = validWords
				words.pop(testWordBase, None) #Remove old entry

				if len(testWord) < 3:
					prevCoords.append((x, y))
					getWords(coord[0], coord[1], testWord, prevCoords)

#--START OF PROGRAM--
#Find position of each character on the board
for letter in ALPHABET:
	charPositions = getCharPositions(letter)
	if not charPositions == None:
		letterPositions[letter] = getCharPositions(letter)

print(areAdjacent((3, 2), (3, 3)))
#Check possible words for each starting position
#for x in range(BOARD_SIZE):
#	for y in range(BOARD_SIZE):
	#	getWords(x, y, getLetterAt((x, y)), [])

print(words)

db.commit()
db.close()
