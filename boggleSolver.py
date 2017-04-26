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

def findWord(board):
	currentPos = [0, 0]
	for row in board:
		word = ""
		validWords = []
		for letter in row:
			word += letter
			newValidWords = getValidWords(word)
			if len(newValidWords) > 0:
				validWords = newValidWords
		print(validWords)

findWord(board)
#print(getValidWords('cat'))

db.commit()
db.close()
