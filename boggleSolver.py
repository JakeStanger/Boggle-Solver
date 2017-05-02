import sqlite3 as sql

board = (('c', 'a', 't', 's'),
		 ('w', 'a', 's', 'p'),
		 ('a', 'l', 'l', 'g'),
		 ('t', 'e', 's', 't'))

BOARD_SIZE = len(board) #We can assume the board width = height

db = sql.connect('data/dictionary')
cursor = db.cursor()

words = {}

def getValidWords(chars):
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
	try:
		return board[coord[0]][coord[1]]
	except:
		print(coord)

def getAdjacentCoords(x, y):
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

	return coords

def getWords(x, y, testWordBase):
	coords = getAdjacentCoords(x, y)
	startChar = getLetterAt([x, y])
	for coord in coords:
		testWord = testWordBase + getLetterAt(coord)
		validWords = getValidWords(testWord)
		if len(validWords) > 0: words[testWord] = validWords

		if len(testWord) < 2: getWords(coord[0], coord[1], testWord)

for x in range(BOARD_SIZE):
	for y in range(BOARD_SIZE):
		getWords(x, y, getLetterAt([x, y]))

print(words)

db.commit()
db.close()
