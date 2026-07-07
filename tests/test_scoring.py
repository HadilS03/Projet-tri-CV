"""Tests du scoring (mots-clés, expérience, score global normalisé)."""
import types

import core.pipeline as p


def test_keywords_mots_communs_score_positif():
    score = p.keywords_score("developpeur python data", "Developpeur Python confirme")
    assert score > 0


def test_keywords_textes_disjoints_score_nul():
    assert p.keywords_score("boulanger patissier", "ingenieur reseau") == 0


def test_keywords_insensible_accents_et_casse():
    # "DEVELOPPEUR" doit correspondre à "développeur".
    assert p.keywords_score("DEVELOPPEUR", "développeur") == 100


def test_experience_cinq_ans_environ_50():
    score = p.experience_score("j'ai 5 ans d'experience en python")
    assert 40 <= score <= 60


def test_experience_absente_score_nul():
    assert p.experience_score("aucune mention pertinente ici") == 0


def test_experience_bornee_a_100():
    score = p.experience_score("20 ans d'experience")
    assert 0 <= score <= 100
    assert score == 100


def test_score_global_normalise_atteint_100(monkeypatch):
    # On neutralise le modèle et l'extraction pour tester uniquement la
    # combinaison pondérée : si les trois sous-scores valent 100, le global = 100.
    monkeypatch.setattr(p, "extract_text_from_docx", lambda chemin: "texte du cv")
    monkeypatch.setattr(p, "get_model", lambda: types.SimpleNamespace(encode=lambda *a, **k: None))
    monkeypatch.setattr(
        p, "util",
        types.SimpleNamespace(pytorch_cos_sim=lambda a, b: types.SimpleNamespace(item=lambda: 1.0)),
    )
    monkeypatch.setattr(p, "keywords_score", lambda cv, job: 100.0)
    monkeypatch.setattr(p, "experience_score", lambda cv: 100.0)

    res = p.process_cv("dummy.docx", "annonce", 0.5, 0.3, 0.2)
    assert res["score"] == 100.0
    assert 0 <= res["score"] <= 100
