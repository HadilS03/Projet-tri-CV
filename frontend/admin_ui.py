import streamlit as st
from core.auth import create_user, get_all_users, delete_user

def admin_ui():
    st.subheader("Page Administrateur")

    # Déconnexion
    if st.button("Se déconnecter"):
        st.session_state.page = "login"
        st.session_state.user = None
        st.session_state.admin_logged = False

    # Création utilisateur
    st.subheader("Créer un nouvel utilisateur")
    new_user = st.text_input("Nom d'utilisateur")
    new_email = st.text_input("Email")  # <-- champ email ajouté
    new_pass = st.text_input("Mot de passe", type="password")
    new_pass2 = st.text_input("Confirmer le mot de passe", type="password")

    if st.button("Créer l'utilisateur"):
        if new_pass != new_pass2:
            st.error("Les mots de passe ne correspondent pas.")
        elif new_user.strip() == "":
            st.error("Le nom d'utilisateur est vide.")
        elif new_email.strip() == "":
            st.error("L'email est obligatoire.")  # <-- vérification email
        else:
            ok, msg = create_user(new_user, new_pass, new_email)  # <-- email passé à la fonction
            if ok:
                st.success(f"Utilisateur {new_user} créé ✅")
                st.session_state["refresh_admin"] = not st.session_state.get("refresh_admin", False)
            else:
                st.error(msg or "Erreur lors de la création.")

    # Liste des utilisateurs
    st.subheader("Liste des utilisateurs")
    users = get_all_users()
    if users:
        for u in users:
            user_id, username, _ = u
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(username)
            with col2:
                if st.button(f"❌ Supprimer {username}", key=f"del_{user_id}"):
                    if username != "admin":
                        delete_user(user_id)
                        st.success(f"Utilisateur {username} supprimé ✅")
                        st.session_state["refresh_admin"] = not st.session_state.get("refresh_admin", False)
                    else:
                        st.warning("Impossible de supprimer l'administrateur.")
