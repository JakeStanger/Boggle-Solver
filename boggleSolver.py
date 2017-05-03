import sqlite3 as sql

#Hard-coded board
board = (('c', 'a', 't', 's'),
		 ('w', 'a', 's', 'p'),
		 ('a', 'l', 'l', 'g'),
		 ('t', 'e', 's', 't'))

BOARD_SIZE = len(board) #We can assume the board width = height

#Load database
db = sql.connect('data/dictionary')
cursor = db.cursor()

#History
words = {}
adjacentCoords = {}
prevCoords = []

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
				if not any(char in boardRow for boardRow in board):
					isValid = False
			if(isValid): validWords.append(row[0])
	return validWords

def getLetterAt(coord):
	'''Gets the character at the given coordinate'''
	return board[coord[0]][coord[1]]

def getAdjacentCoords(x, y):
	'''Gets a list of adjacent coordinates for the given set of coordinates'''
	if (x, y) in adjacentCoords:
		return adjacentCoords[(x, y)]

	coords = []

	if x > 0:
		coords.append([x-1, y])
		if y > 0: coords.append([x-1, y-1])
		if y < BOARD_SIZE-1: coords.append([x-1, y+1])
	if x < BOARD_SIZE-1:
		coords.append([x+1, y])
		if y > 0: coords.append([x+1, y-1])
		if y < BOARD_SIZE-1: coords.append([x+1, y+1])
	if y > 0: coords.append([x, y-1])
	if y < BOARD_SIZE-1: coords.append([x, y+1])

	adjacentCoords[(x, y)] = coords
	return coords

def getWords(x, y, testWordBase):
	'''Gets a list of valid words for the given coordinate
	and pre-assembled set of characters'''
	coords = getAdjacentCoords(x, y)
	startChar = getLetterAt([x, y])
	if not (x, y) in prevCoords:
		for coord in coords:
			testWord = testWordBase + getLetterAt(coord)
			if testWord in words:
				validWords = words[testWord]
			else:
				validWords = getValidWords(testWord)
			if len(validWords) > 0: words[testWord] = validWords

			if len(testWord) < BOARD_SIZE: getWords(coord[0], coord[1], testWord)

		prevCoords.append((x, y))

#--START OF PROGRAM--
#Check possible words for each starting position
for x in range(BOARD_SIZE):
	for y in range(BOARD_SIZE):
		getWords(x, y, getLetterAt((x, y)))

print(words)

db.commit()
db.close()
