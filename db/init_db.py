import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

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

# Validation des changements et fermeture de la connexion
conn.commit()
conn.close()

print(f"La base de données 'users.db' a été créée dans {DB_PATH} avec succès !")

