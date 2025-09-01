import streamlit as st # type: ignore
import os
import sqlite3

# Dossier où stocker les CV
DB_PATH = os.path.join(os.path.dirname(__file__), "../db/users.db")
UPLOAD_FOLDER = "uploads"

# Création du dossier si inexistant
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_cv_to_db(username, filename, filepath):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Récupérer l’ID utilisateur
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        cursor.execute("INSERT INTO cvs (user_id, filename, filepath) VALUES (?, ?, ?)",
                       (user_id, filename, filepath))
        conn.commit()

    conn.close()


def run():
    st.title(" Upload de CV")

    # Vérifier si l’utilisateur est connecté
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Veuillez vous connecter avant d'uploader un CV.")
    else:
        uploaded_file = st.file_uploader("Choisissez un CV", type=["pdf", "docx"])

        if uploaded_file is not None:
            filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

            # Sauvegarde du fichier
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"CV {uploaded_file.name} uploadé avec succès !")
            st.info(f"Chemin : {filepath}")
