import sqlite3 as sql

board = (('c', 'a', 't', 's'),
		 ('w', 'a', 's', 'p'),
		 ('a', 'l', 'l', 'g'),
		 ('t', 'e', 's', 't'))

BOARD_SIZE = len(board) #We can assume the board width = height

db = sql.connect('data/dictionary')
cursor = db.cursor()

def getValidWords(chars):
	validWords = []
	cursor.execute("SELECT word FROM words WHERE word LIKE \'" + chars + "%\'")
	for row in cursor:
		if len(row[0]) <= BOARD_SIZE:
			validWords.append(row[0])
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

def findWord(coords):
	print("")

def findWords(board):
	testWord = ""
	for i in range(BOARD_SIZE):
		for j in range(BOARD_SIZE):
			startChar = getLetterAt(i, j)
			print(startChar)

for x in range(BOARD_SIZE):
	for y in range(BOARD_SIZE):
		coords = getAdjacentCoords(x, y)
		startChar = getLetterAt([x, y])

		for coord in coords:
			testWord = startChar + getLetterAt(coord)
			print(getValidWords(testWord))

db.commit()
db.close()
