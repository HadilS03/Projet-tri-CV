import streamlit as st # type: ignore
from frontend import auth, upload_cv

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Aller à", ["Connexion / Inscription", "Upload CV"])

if page == "Connexion / Inscription":
    auth.run()
elif page == "Upload CV":
    upload_cv.run()
