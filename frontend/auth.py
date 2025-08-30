import streamlit as st # type: ignore
import sqlite3
import hashlib
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "../db/users.db")

# Fonction pour hasher le mot de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fonction pour créer un nouvel utilisateur
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

# Fonction pour vérifier l'utilisateur lors de la connexion
def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Initialiser les variables de session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Interface Streamlit
st.title("Module d'authentification")

if st.session_state.logged_in:
    st.success(f"Connecté en tant que {st.session_state.username} !")
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()  # Recharge la page pour revenir au menu
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
                st.experimental_rerun()  # Recharge la page pour afficher l'état connecté
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

