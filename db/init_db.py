import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    # Connexion à SQLite (le fichier sera créé s'il n'existe pas)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Création de la table utilisateurs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Création de la table des CV
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        filepath TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Validation des changements et fermeture de la connexion
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()
    print("Base de données initialisée avec succès ")