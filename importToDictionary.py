import sqlite3 as sql

db = sql.connect('data/dictionary')

cursor = db.cursor()
cursor.execute("CREATE TABLE words(id INTEGER PRIMARY KEY, word TEXT)")


with open("words.txt", 'r'), open("words2.txt", "r"), open("words3.txt", "r") as words:
	for word in words:
		cursor.execute('''INSERT INTO words(word) VALUES(:word)''', {'word':word.replace("\n", "")})
db.commit()
db.close()

cursor.execute("SELECT * FROM words")
for row in cursor:
	print('{0} : {1}'.format(row[0], row[1]))
