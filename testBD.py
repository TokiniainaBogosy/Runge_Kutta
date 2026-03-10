import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

'''cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for (table,) in tables:
    print(f"\nStructure de {table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    for col in cursor.fetchall():
        print(col)'''

cursor.execute("DELETE FROM depenses WHERE id = 16;")

"""cursor.execute("DELETE FROM depenses")"""


conn.commit()
conn.close()
'''cursor.execute("""
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP 
    )          
""")'''