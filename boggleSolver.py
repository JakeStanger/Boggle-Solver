import sqlite3 as sql
from flask import Flask, render_template, request
import ast
import timeit

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
adjacentLetters = {}
letterPositions = {}

def getWordScore(word):
    length = len(word)
    if length <= 4: return 1
    if length == 5: return 2
    if length == 6: return 3
    if length == 7: return 5
    if length >= 8: return 11

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

def getAdjacentChars(x, y):
	'''Gets a list of adjacent letters for the given set of coordinates'''
	if (x, y) in adjacentLetters:
		return adjacentLetters[(x, y)]

	coords = getAdjacentCoords(x, y)

	returnData = {}
	for coord in coords:
		char = getLetterAt(coord)
		if not char in returnData:
			returnData[char] = [coord]
		else: returnData[char].append(coord)

	adjacentLetters[(x, y)] = returnData
	return returnData

def findCharOnBoard(char):
	occurs = []
	for i in range(len(board)):
		indices = [j for j, x in enumerate(board[i]) if x == char]
		for k in range(len(indices)): occurs.append((i, indices[k]))
	return occurs

def getWords(x, y, testWordBase):
	'''Gets a list of possible words for every possible 2 character
	combination starting at the given co-ordinate'''
	coords = getAdjacentCoords(x, y)
	for coord in coords:
		testWord = testWordBase + getLetterAt(coord) #TODO Fix bug on this line (3x3 grid)
		if testWord in words:
			validWords = words[testWord]
		else:
			validWords = getValidWords(testWord)

		if len(validWords) > 0:
			words[testWord] = validWords
			words.pop(testWordBase, None) #Remove old entry

def isWordValid(word, i, locationHistory, locations):
	'''Recurs to check if the given word is valid'''
	#Crop history length (there seems to be some issue with appending otherwise)
	locationHistory = locationHistory[:i]

	anyLocationValid = False
	for location in locations:
		if not location in locationHistory: #Check tile not already used
			adjacentChars = getAdjacentChars(location[0], location[1])

			#Check next and previous letters are adjacent
			if word[i+1] in adjacentChars and (word[i-1] in adjacentChars or i-1 < 0):
				#Check current location is adjacent to previously added location
				if len(locationHistory) == 0 or areAdjacent(locationHistory[-1], location):

					#Check all possible positions of next char are valid
					anyPossibleWay = False
					for nextPos in adjacentChars[word[i+1]]:
						#Check this location is adjacent
						if location in getAdjacentCoords(nextPos[0], nextPos[1]):
							#Check next position has not been used
							if not nextPos in locationHistory:
								anyPossibleWay = True

					#If no tile for the next character is valid
					#Then skip to the next location for this character
					if not anyPossibleWay: continue

					#If less than max recursion depth
					if i < len(word)-2:
						locationHistory.append(location)
						anyLocationValid = isWordValid(word, i+1, locationHistory, adjacentChars[word[i+1]])
						if anyLocationValid: return True
					else: return True #Otherwise all is valid

	return anyLocationValid

@app.route('/boggleSolver.py', methods=['GET', 'POST'])
def boggleSolve():
	startTime = timeit.default_timer()

	global board
	global BOARD_SIZE

	global words
	global adjacentCoords
	global adjacentLetters
	global letterPositions

	#Clear history
	words = {}
	adjacentCoords = {}
	adjacentLetters = {}
	letterPositions = {}

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
			getWords(x, y, getLetterAt((x, y)))

	#Check remaining words to make sure each of their
	#characters are adjacent.
	for key in words:
		for word in words[key]:
			isValid = isWordValid(word, 0, [], findCharOnBoard(word[0]))
			if isValid: results.append(word)

	db.commit()

	elapsedTime = timeit.default_timer() - startTime

	return ",".join(str(word) + ":" + str(getWordScore(word)) for word in results) + "-" + str(round(elapsedTime, 2))

#--START OF PROGRAM--
if __name__ == "__main__":
	app.run()
	app.debug = True

	db.close()
