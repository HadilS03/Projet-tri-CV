import streamlit as st # type: ignore
from core.auth import ensure_tables, init_files_db, cleanup_expired_files
from frontend.login_ui import login_ui
from frontend.admin_ui import admin_ui # type: ignore
from frontend.user_ui import user_app_ui

# --- Initialisation ---
init_files_db()
cleanup_expired_files()
ensure_tables()

st.set_page_config(page_title="Tri intelligent de CV", layout="wide")

# --- Gestion session ---
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# --- Router ---
if st.session_state.page == "login":
    login_ui()
elif st.session_state.page == "admin_app":
    admin_ui()
elif st.session_state.page == "user_app":
    user_app_ui()

