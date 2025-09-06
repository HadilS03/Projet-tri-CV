import streamlit as st  # type: ignore
import sqlite3
import hashlib
import os
import time

# Chemin vers les bases de données
DB_PATH = os.path.join(os.path.dirname(__file__), "../db/users.db")
FILES_DB_PATH = os.path.join(os.path.dirname(__file__), "../db/files.db")

# =========================
#   INIT BASE DE DONNÉES
# =========================
def ensure_tables():
    """Créer la table users si elle n'existe pas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_files_db():
    """Créer la table des fichiers si elle n'existe pas."""
    conn = sqlite3.connect(FILES_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            uploaded_at REAL
        )
    """)
    conn.commit()
    conn.close()
def cleanup_expired_files(expiration_seconds: int = 86400):
    """Supprime les fichiers expirés de la base et du disque (par défaut > 24h)."""
    conn = sqlite3.connect(FILES_DB_PATH)
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("SELECT id, filename, uploaded_at FROM files")
    files = cursor.fetchall()

    for file_id, filename, uploaded_at in files:
        if now - uploaded_at > expiration_seconds:
            # Supprimer le fichier du disque si nécessaire
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
            # Supprimer l'entrée en base
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))

    conn.commit()
    conn.close()

# =========================
#   AUTHENTIFICATION
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hash_password(password)))
        conn.commit()
        st.success("Utilisateur créé avec succès !")
    except sqlite3.IntegrityError:
        st.error("Nom d'utilisateur ou email déjà utilisé.")
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def authenticate(username, password):
    """Alias pour login(), utile dans login_ui."""
    return login(username, password)

# =========================
#   ADMIN FUNCTIONS
# =========================
def create_user(username: str, password: str, email: str) -> tuple[bool, str]:
    """
    Crée un utilisateur avec email et retourne (ok, message)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Vérifier si le nom d'utilisateur existe déjà
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Nom d'utilisateur déjà utilisé"

    # Insérer l'utilisateur dans la base
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, hash_password(password))
    )
    conn.commit()
    conn.close()
    return True, "Utilisateur créé avec succès"





def get_all_users():
    """Retourne la liste des utilisateurs (id, username, email)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(user):
    """Supprime un utilisateur par son ID."""
    if isinstance(user, tuple):
        user_id = user[0]
    else:
        user_id = user
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# =========================
#   UI STREAMLIT
# =========================
def run():
    # Initialiser les variables de session
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    st.title("Module d'authentification")

    if st.session_state.logged_in:
        st.success(f"Connecté en tant que {st.session_state.username} !")
        if st.button("Se déconnecter"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    else:
        st.sidebar.title("Menu d'authentification")
        menu = ["Connexion", "Inscription"]
        choice = st.sidebar.selectbox("Choisissez une option", menu)

        if choice == "Inscription":
            st.subheader("Créer un nouveau compte")
            username = st.text_input("Nom d'utilisateur")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            if st.button("S'inscrire"):
                signup(username, email, password)

        elif choice == "Connexion":
            st.subheader("Se connecter")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                user = login(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
def add_file(filename, user_id=None):
    """Ajoute un fichier à la base de données des fichiers et user_id optionnel pour lier le fichier à un utilisateur.."""
    conn = sqlite3.connect(FILES_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (filename, uploaded_at) VALUES (?, ?)",
        (filename, time.time())
    )
    conn.commit()
    conn.close()
