"""Tests de l'authentification : bcrypt et cycle signup/login sur base temporaire."""
import types

import core.auth as auth


def test_bcrypt_aller_retour():
    empreinte = auth.hash_password("motdepasse")
    assert auth.verify_password("motdepasse", empreinte)
    assert not auth.verify_password("mauvais", empreinte)


def test_bcrypt_sel_deux_hashs_differents():
    # Le sel intégré garantit deux empreintes différentes pour le même mot de passe.
    assert auth.hash_password("motdepasse") != auth.hash_password("motdepasse")


def test_signup_puis_login(tmp_path, monkeypatch):
    base = tmp_path / "users.db"
    monkeypatch.setattr(auth, "DB_PATH", str(base))
    # Neutralise les appels Streamlit (hors runtime dans les tests).
    monkeypatch.setattr(
        auth, "st",
        types.SimpleNamespace(success=lambda *a, **k: None, error=lambda *a, **k: None),
    )

    auth.ensure_tables()
    auth.signup("alice", "alice@example.com", "motdepasse")

    assert auth.login("alice", "motdepasse") is not None
    assert auth.login("alice", "faux") is None
