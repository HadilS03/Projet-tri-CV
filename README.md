# Projet Tri de CV

Application d'aide au tri de CV : elle compare chaque CV à une description de poste
par **similarité sémantique locale** et classe les candidatures du plus au moins
pertinent. C'est une **aide à la décision** — jamais un rejet automatique : le
recruteur garde la main sur chaque candidature.

## Architecture

- `core/` : logique métier — extraction de texte (PDF/DOCX), scoring (similarité
  sémantique, mots-clés, expérience), authentification (bcrypt).
- `frontend/` : interface Streamlit (connexion, espace utilisateur, espace admin).
- `db/` : bases SQLite locales (comptes, fichiers) — **non versionnées**, recréées
  au démarrage si absentes.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Variables d'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `CV_MODEL` | Modèle sentence-transformers pour la similarité | `paraphrase-multilingual-MiniLM-L12-v2` |

Le modèle multilingue est retenu car les CV traités sont en français.

## Tests

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -q
```

Les tests ne téléchargent aucun modèle (chargement paresseux `get_model()` +
mocks) : ils tournent hors ligne et en CI.

## Confidentialité et RGPD

- **Traitement 100 % local** : les CV et leur contenu ne quittent jamais la
  machine ; aucun envoi à un service tiers pour l'analyse.
- **Suppression automatique** : les CV et leurs données sont supprimés après 24 h
  (`cleanup_expired_files`, exécuté au démarrage de l'application).
- **Aucune donnée personnelle versionnée** : CV, bases SQLite et rapports sont
  exclus du dépôt via `.gitignore` ; l'analyse n'est lancée qu'après consentement.
- **Aide à la décision** : l'outil classe mais ne rejette jamais automatiquement un
  candidat, conformément à la vigilance de la CNIL sur les outils de recrutement.
