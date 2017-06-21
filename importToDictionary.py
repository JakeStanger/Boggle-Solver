import sqlite3 as sql

db = sql.connect('data/dictionary')

cursor = db.cursor()
#cursor.execute("DROP TABLE words")
cursor.execute("CREATE TABLE words(word TEXT UNIQUE)")


with open("dictionary.txt", 'r') as words:
	for word in words:
		cursor.execute('''INSERT OR IGNORE INTO words(word) VALUES(:word)''', {'word':word.replace("\n", "").lower()})

cursor.execute("DELETE FROM words WHERE word LIKE \'__\'")
cursor.execute("DELETE FROM words WHERE word GLOB \'*[^A-z]*\'")

db.commit()
db.close()
