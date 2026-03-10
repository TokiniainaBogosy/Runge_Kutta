import sqlite3
def init_db():
    # Crée la base
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        capital_initial REAL NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS revenus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_user TEXT NOT NULL,
        mois INTEGER NOT NULL,
        taux_revenu REAL NOT NULL,
        FOREIGN KEY (email_user) REFERENCES utilisateurs(email) ON DELETE CASCADE
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_user TEXT NOT NULL,
        mois INTEGER NOT NULL,
        coefficient_depense REAL NOT NULL,
        depense_fixe REAL NOT NULL,
        FOREIGN KEY (email_user) REFERENCES utilisateurs(email) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

    print("Base de données créée !")