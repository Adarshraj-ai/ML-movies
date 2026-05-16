import sqlite3
conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT movie_id, title FROM Peliculas WHERE title = 'Minions'")
print(cursor.fetchone())
conn.close()
