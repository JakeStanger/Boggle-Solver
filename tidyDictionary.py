import sqlite3 as sql

db = sql.connect('data/dictionary')

cursor = db.cursor()
cursor.execute("DELETE FROM words WHERE word LIKE \'__\'")
cursor.execute("DELETE FROM words WHERE word LIKE \'%-\'")
cursor.execute("DELETE FROM words WHERE word LIKE \'-%\'")
cursor.execute("DELETE FROM words WHERE word LIKE \'.%\'")
cursor.execute("DELETE FROM words WHERE word LIKE \'%.\'")

db.commit()
db.close()
