import streamlit as st # type: ignore
from core.auth import authenticate

def login_ui():
    st.title("Tri automatique de CV")
    st.subheader("Page de connexion")

    # Champs login
    username = st.text_input("Nom d'utilisateur", value=st.session_state.get("login_username", ""))
    password = st.text_input("Mot de passe", type="password", value=st.session_state.get("login_password", ""))

    # Sauvegarde des infos dans la session
    st.session_state.login_username = username
    st.session_state.login_password = password

    # Bouton connexion
    if st.button("Se connecter"):
        # Admin hardcodé
        if username == "admin" and password == "admin123":
            st.session_state.admin_logged = True
            st.session_state.page = "admin_app"
            st.success("Connexion administrateur réussie ✅")
        elif authenticate(username, password):
            st.session_state.user = username.strip().lower()
            st.session_state.page = "user_app"
            st.success("Connexion utilisateur réussie ✅")
        else:
            st.error("Identifiants invalides.")
